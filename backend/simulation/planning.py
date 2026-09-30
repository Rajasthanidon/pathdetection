import math
from .config import Config

class AdaptivePlanner:
    def __init__(self):
        self.last_path = None
        self.last_candidate_idx = None
        self.replanning = False
        
    def generate_candidates(self, ego):
        candidates = []
        for i in range(Config.LATERAL_SAMPLES):
            # Target lateral offset relative to current position, capped by total spacing
            target_lat = (i - Config.LATERAL_SAMPLES//2) * Config.LATERAL_SPACING
            
            path = []
            for step in range(Config.PREDICTION_STEPS):
                t = step * Config.DT
                # Predict distance along ego's current heading
                # Simple approximation: ego moves longitudinally along its current heading
                s = ego.speed * t + 0.5 * ego.accel * (t**2)
                if s == 0 and step > 0: s = 0.5 # ensure some forward lookahead
                
                # Smooth polynomial lateral shift (quintic-like S-curve)
                # Let lookahead length be roughly speed * PREDICTION_HORIZON
                total_L = max(10.0, ego.speed * Config.PREDICTION_HORIZON)
                tau = min(1.0, s / total_L)
                # s-curve: 3*tau^2 - 2*tau^3
                lat_shift = target_lat * (3*(tau**2) - 2*(tau**3))
                
                # We need x, y. Ego's heading is roughly along X if heading=0
                px = ego.x + s * math.cos(ego.heading) - lat_shift * math.sin(ego.heading)
                py = ego.y + s * math.sin(ego.heading) + lat_shift * math.cos(ego.heading)
                
                path.append((px, py))
                
            candidates.append(path)
        return candidates

    def check_collision(self, ego, path, tracks, predictions, env):
        min_dist_overall = float('inf')
        max_uncertainty = 0.0
        
        road_left = env.get("road_left", -10.0)
        road_right = env.get("road_right", 10.0)
        obstacles = env.get("obstacles", [])
        
        ego_hw = Config.VEHICLE_WIDTH / 2.0
        ego_hl = Config.VEHICLE_LENGTH / 2.0
        
        for step, (px, py) in enumerate(path):
            # 1. Road Boundary Check
            if py - ego_hw < road_left:
                return True, 0.0, 0.0, f"ROAD_LEFT at step {step}"
            if py + ego_hw > road_right:
                return True, 0.0, 0.0, f"ROAD_RIGHT at step {step}"
                
            # 2. Static Obstacle Check
            for obs in obstacles:
                ox, oy = obs["x"], obs["y"]
                ow, ol = obs["width"], obs["length"]
                # AABB collision check
                if abs(px - ox) < (ego_hl + ol/2.0) and abs(py - oy) < (ego_hw + ow/2.0):
                    return True, 0.0, 0.0, f"STATIC_OBS {obs['cls']} at step {step}"
            
            # 3. Dynamic Obstacle Check
            for t in tracks:
                tid = t["id"]
                if tid in predictions and step < len(predictions[tid]["path"]):
                    tx, ty = predictions[tid]["path"][step]
                    uncertainty = predictions[tid]["uncertainty"]
                else:
                    tx, ty = t["x"], t["y"]
                    uncertainty = 0.5
                
                # Scale uncertainty by time: no prediction uncertainty at t=0
                time_scaled_uncertainty = uncertainty * (step / Config.PREDICTION_STEPS)
                
                dist = math.hypot(px - tx, py - ty)
                clearance = dist - (ego_hw + t["width"]/2) - (time_scaled_uncertainty * 0.5)
                
                if clearance < min_dist_overall:
                    min_dist_overall = clearance
                    max_uncertainty = max(max_uncertainty, time_scaled_uncertainty)
                    
                if clearance < 0.2: # Hard collision boundary
                    return True, 0.0, max_uncertainty, f"DYNAMIC_OBS {tid} at step {step} (dist={dist:.2f}, tx={tx:.2f}, ty={ty:.2f}, px={px:.2f}, py={py:.2f})"
                    
        return False, min_dist_overall, max_uncertainty, "SAFE"

    def plan(self, ego, tracks, predictions, risk, env):
        candidates = self.generate_candidates(ego)
        best_path = None
        best_score = float('inf')
        
        self.last_candidates = []
        
        for idx, path in enumerate(candidates):
            is_collision, min_clear, uncertainty, coll_reason = self.check_collision(ego, path, tracks, predictions, env)
            if is_collision:
                self.last_candidates.append({"path": path, "score": float('inf'), "is_collision": True, "reason": coll_reason})
                continue
            
            end_dx = path[-1][0] - ego.x
            end_dy = path[-1][1] - ego.y
            ideal_dx = Config.LOOKAHEAD_DIST * math.cos(ego.heading)
            ideal_dy = Config.LOOKAHEAD_DIST * math.sin(ego.heading)
            
            curvature_cost = math.hypot(end_dx - ideal_dx, end_dy - ideal_dy)
            clearance_cost = 1.0 / (min_clear + 0.1)
            uncertainty_cost = uncertainty
            
            # Continuity: penalize switching candidates
            continuity_cost = 0.0
            if self.last_candidate_idx is not None:
                continuity_cost = abs(idx - self.last_candidate_idx) * 2.0
            
            score = (Config.W_CURVATURE * curvature_cost + 
                     Config.W_CLEARANCE * clearance_cost +
                     Config.W_UNCERTAINTY * uncertainty_cost +
                     Config.W_CONTINUITY * continuity_cost)
            
            self.last_candidates.append({"path": path, "score": score, "is_collision": False, "reason": "SAFE"})
            
            if score < best_score:
                best_score = score
                best_path = path
                best_idx = idx
                
        if best_path:
            self.last_path = best_path
            self.last_candidate_idx = best_idx
            self.replanning = (best_idx != Config.LATERAL_SAMPLES // 2)
        else:
            self.replanning = False
            
        return best_path
