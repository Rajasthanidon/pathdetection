import math
from .config import Config

class RiskEngine:
    @staticmethod
    def calculate_risk(ego, tracks, predictions, current_path=None):
        min_ttc = float('inf')
        min_clearance = float('inf')
        critical = False
        
        stopping_distance = (ego.speed ** 2) / (2 * abs(Config.MAX_DECEL)) + (ego.speed * 0.5) # 0.5s reaction margin
        
        counterfactual_collision = False
        counterfactual_clearance = float('inf')
        
        for t in tracks:
            dx = t["x"] - ego.x
            dy = t["y"] - ego.y
            dist = math.hypot(dx, dy)
            
            is_vru = t.get("cls") in ["Pedestrian", "Animal", "ScriptedAnimal", "Bicycle"]
            
            # AABB-based clearance approximation
            dx_abs = abs(dx)
            dy_abs = abs(dy)
            clearance_x = dx_abs - (ego.length/2.0 + t["length"]/2.0)
            clearance_y = dy_abs - (ego.width/2.0 + t["width"]/2.0)
            
            # If both are negative, we are overlapping. The clearance is the max of the two overlaps.
            # If at least one is positive, that's the clearance distance in that axis.
            if clearance_x > 0 and clearance_y > 0:
                clearance = math.hypot(clearance_x, clearance_y)
            else:
                clearance = max(clearance_x, clearance_y)
                
            if clearance < min_clearance:
                min_clearance = clearance
                
            v_rel_x = ego.speed * math.cos(ego.heading) - t["speed"] * math.cos(t["heading"])
            v_rel_y = ego.speed * math.sin(ego.heading) - t["speed"] * math.sin(t["heading"])
            v_rel = (v_rel_x * dx + v_rel_y * dy) / (dist + 1e-5)
            
            ttc_crit = Config.TTC_CRITICAL_VRU if is_vru else Config.TTC_CRITICAL
            clr_crit = Config.CLEARANCE_CRITICAL_VRU if is_vru else Config.CLEARANCE_CRITICAL
            
            # Predicted collision with stopping distance envelope
            if v_rel > 0:
                ttc = dist / v_rel
                if ttc < min_ttc:
                    min_ttc = ttc
                    
                if ttc < ttc_crit and dist <= stopping_distance * 1.5:
                    critical = True
                    
            if clearance < clr_crit and dist <= stopping_distance:
                critical = True
                
        # Counterfactual evaluation (if we just went straight / followed current path)
        if current_path and predictions:
            for step, (px, py) in enumerate(current_path):
                for t in tracks:
                    tid = t["id"]
                    if tid in predictions and step < len(predictions[tid]["path"]):
                        tx, ty = predictions[tid]["path"][step]
                    else:
                        tx, ty = t["x"], t["y"]
                    
                    dx_c = abs(px - tx)
                    dy_c = abs(py - ty)
                    cx = dx_c - (Config.VEHICLE_LENGTH/2.0 + t["length"]/2.0)
                    cy = dy_c - (Config.VEHICLE_WIDTH/2.0 + t["width"]/2.0)
                    if cx > 0 and cy > 0:
                        clr = math.hypot(cx, cy)
                    else:
                        clr = max(cx, cy)
                        
                    if clr < counterfactual_clearance:
                        counterfactual_clearance = clr
                    if clr < 0.2:
                        counterfactual_collision = True
                    
        risk_level = "SAFE"
        if critical:
            risk_level = "CRITICAL"
        elif min_ttc < Config.TTC_WARNING_VRU or min_clearance < Config.CLEARANCE_WARNING_VRU:
            risk_level = "HIGH" if min_ttc < Config.TTC_WARNING else "CAUTION"
            
        return {
            "min_ttc": min_ttc,
            "min_clearance": min_clearance,
            "risk_level": risk_level,
            "critical": critical,
            "stopping_distance": stopping_distance,
            "counterfactual": {
                "collision": counterfactual_collision,
                "clearance": counterfactual_clearance
            }
        }
