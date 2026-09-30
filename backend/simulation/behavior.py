from .config import Config

class BehaviorPlanner:
    def __init__(self):
        self.state = "CRUISE"
        self.dwell_time = 0.0
        self.last_state = "CRUISE"

    def decide(self, ego, risk, has_path):
        target_speed = Config.MAX_SPEED
        desired_state = "CRUISE"
        
        if risk["critical"]:
            desired_state = "EMERGENCY_STOP"
            target_speed = 0.0
        elif not has_path:
            desired_state = "BRAKE"
            target_speed = 0.0
        elif risk["risk_level"] == "HIGH":
            desired_state = "AVOID RIGHT" if hasattr(self, 'last_candidate_idx') and self.last_candidate_idx > Config.LATERAL_SAMPLES//2 else "AVOID LEFT"
            target_speed = ego.speed * 0.8
        elif risk["risk_level"] == "CAUTION":
            desired_state = "FOLLOW"
            target_speed = ego.speed * 0.5
            
        # Hysteresis / Dwell logic: Do not downgrade from EMERGENCY_STOP instantly
        if self.state == "EMERGENCY_STOP" and desired_state != "EMERGENCY_STOP":
            if self.dwell_time < 2.0:
                desired_state = "EMERGENCY_STOP"
                target_speed = 0.0
                
        if desired_state != self.state:
            self.state = desired_state
            self.dwell_time = 0.0
        else:
            self.dwell_time += Config.DT
            
        self.last_state = self.state
        return self.state, target_speed
