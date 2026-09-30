import math
from .config import Config

class DecisionMemory:
    def __init__(self):
        self.history = []
        self.preferences = {
            "CRUISE": 0.0,
            "FOLLOW": 0.0,
            "PASS_LEFT": 1.0,
            "PASS_RIGHT": 1.0,
            "WAIT": 0.0,
            "EMERGENCY_STOP": -10.0
        }
        
    def record(self, state):
        self.history.append(state)
        # Very simple adaptive logic: reward successful passes
        action = state.get("action")
        if state.get("result") == "SUCCESS" and action in self.preferences:
            self.preferences[action] += 0.1
        elif state.get("result") == "UNSAFE" and action in self.preferences:
            self.preferences[action] -= 0.5
            
    def get_preference(self, action):
        return self.preferences.get(action, 0.0)
        
    def get_stats(self):
        return {
            "total_experiences": len(self.history),
            "successes": sum(1 for h in self.history if h.get("result") == "SUCCESS"),
            "unsafe": sum(1 for h in self.history if h.get("result") == "UNSAFE"),
            "preferences": self.preferences
        }

class AdaptivePlanner:
    def __init__(self):
        self.last_path = None
        self.last_behavior = "CRUISE"
        self.last_target_y = 0.0
        self.memory = DecisionMemory()
        self.commitment_time = 0.0
        self.last_candidates = []
        self.replanning = False
        
    def check_corridor_safe(self, ego, path, tracks, predictions, env):
        # Swept volume collision check
        min_clearance = float('inf')
        road_left = env.get("road_left", -10.0)
        road_right = env.get("road_right", 10.0)
        ego_hw = ego.width / 2.0
        ego_hl = ego.length / 2.0
        
        for step, (px, py) in enumerate(path):
            if py - ego_hw < road_left: return False, 0.0, "ROAD_LEFT"
            if py + ego_hw > road_right: return False, 0.0, "ROAD_RIGHT"
            
            for obs in env.get("obstacles", []):
                ox, oy, ow, ol = obs["x"], obs["y"], obs["width"], obs["length"]
                if abs(px - ox) < (ego_hl + ol/2.0) and abs(py - oy) < (ego_hw + ow/2.0):
                    return False, 0.0, "STATIC_OBS"
                    
            for t in tracks:
                tid = t["id"]
                if tid in predictions and step < len(predictions[tid]["path"]):
                    tx, ty = predictions[tid]["path"][step]
                else:
                    tx, ty = t["x"], t["y"]
                
                # Apply buffer only for future steps, otherwise you can get stuck if starting close
                buffer = 0.2 if step > 5 else 0.0
                
                # OBB check approximation (AABB for speed)
                if abs(px - tx) < (ego_hl + t["length"]/2.0 + buffer) and abs(py - ty) < (ego_hw + t["width"]/2.0 + buffer):
                    return False, 0.0, f"DYNAMIC_COLLISION_{tid}"
                    
                dist = math.hypot(px - tx, py - ty)
                clearance = dist - (ego_hw + t["width"]/2.0)
                if clearance < min_clearance: min_clearance = clearance
                
        return True, min_clearance, "SAFE"

    def generate_candidate(self, ego, target_y, target_speed, behavior_name):
        path = []
        for step in range(Config.PREDICTION_STEPS):
            t = step * Config.DT
            s = max(0.0, target_speed * t)
            
            # Shift laterally much quicker (e.g. over 15 meters) so we clear obstacles
            total_L = max(15.0, target_speed * 1.5)
            tau = min(1.0, s / total_L)
            
            lat_shift = (target_y - ego.y) * (3*(tau**2) - 2*(tau**3))
            
            px = ego.x + s * math.cos(ego.heading) - lat_shift * math.sin(ego.heading)
            py = ego.y + s * math.sin(ego.heading) + lat_shift * math.cos(ego.heading)
            path.append((px, py))
            
        return {
            "behavior": behavior_name,
            "target_y": target_y,
            "target_speed": target_speed,
            "path": path
        }

    def plan(self, ego, tracks, predictions, env, risk):
        # 1. State Hysteresis (Commitment)
        if self.commitment_time > 0:
            self.commitment_time -= Config.DT
            c = self.generate_candidate(ego, self.last_target_y, ego.speed, self.last_behavior)
            safe, clr, reason = self.check_corridor_safe(ego, c["path"], tracks, predictions, env)
            if safe:
                self.last_path = c["path"]
                self.replanning = (abs(self.last_target_y) > 0.5)
                return c["path"], c["behavior"], c["target_speed"]
            else:
                self.commitment_time = 0.0 
        
        candidates = []
        
        # 1. CRUISE
        candidates.append(self.generate_candidate(ego, 0.0, Config.MAX_SPEED, "CRUISE"))
        
        # 2. FOLLOW
        front_dist = float('inf')
        front_speed = 0.0
        for t in tracks:
            dx = t["x"] - ego.x
            dy = t["y"] - ego.y
            if dx > 0 and abs(dy) < ego.width + 0.5:
                if dx < front_dist:
                    front_dist = dx
                    front_speed = t["speed"]
                    
        if front_dist < 40.0:
            follow_speed = max(0.0, min(front_speed, Config.MAX_SPEED))
            candidates.append(self.generate_candidate(ego, 0.0, follow_speed, "FOLLOW"))
        
        # 3. PASS_LEFT and PASS_RIGHT
        pass_speed = max(6.0, ego.speed)
        for offset in [3.0, 4.0]:
            candidates.append(self.generate_candidate(ego, -offset, pass_speed, "PASS_LEFT"))
            candidates.append(self.generate_candidate(ego, offset, pass_speed, "PASS_RIGHT"))
            
        # 4. RECOVER
        if abs(ego.y) > 1.0:
            candidates.append(self.generate_candidate(ego, 0.0, pass_speed, "RECOVER"))

        self.last_candidates = []
        best_candidate = None
        best_score = float('inf')
        
        for cand in candidates:
            safe, clearance, reason = self.check_corridor_safe(ego, cand["path"], tracks, predictions, env)
            
            if not safe:
                cand["score"] = float('inf')
                cand["is_collision"] = True
                cand["reason"] = reason
                self.last_candidates.append(cand)
                continue
                
            # Score valid candidates
            # Base cost: deviation from center (y=0)
            cost = abs(cand["target_y"]) * 5.0
            
            # Speed cost: heavily penalize slowing down!
            cost += max(0, Config.MAX_SPEED - cand["target_speed"]) * 15.0
            
            # Clearance cost
            cost += 5.0 / (clearance + 0.1)
            
            # Memory Preference
            cost -= self.memory.get_preference(cand["behavior"]) * 10.0
            
            if self.last_target_y is not None:
                cost += abs(cand["target_y"] - self.last_target_y) * 10.0
                
            cand["score"] = cost
            cand["is_collision"] = False
            cand["reason"] = "SAFE"
            self.last_candidates.append(cand)
            
            if cost < best_score:
                best_score = cost
                best_candidate = cand
                
        if best_candidate:
            behavior = best_candidate["behavior"]
            
            if behavior in ["PASS_LEFT", "PASS_RIGHT", "RECOVER"] and self.last_behavior != behavior:
                self.commitment_time = 1.5
                
            if behavior == "CRUISE" and self.last_behavior in ["RECOVER", "PASS_LEFT", "PASS_RIGHT"]:
                self.memory.record({"action": self.last_behavior, "result": "SUCCESS"})
                
            self.last_behavior = behavior
            self.last_target_y = best_candidate["target_y"]
            self.last_path = best_candidate["path"]
            self.replanning = abs(best_candidate["target_y"]) > 0.5
            
            return best_candidate["path"], behavior, best_candidate["target_speed"]
            
        else:
            self.memory.record({"action": self.last_behavior, "result": "UNSAFE"})
            self.last_behavior = "EMERGENCY_STOP"
            return [], "EMERGENCY_STOP", 0.0
