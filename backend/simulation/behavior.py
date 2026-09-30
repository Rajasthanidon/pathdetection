from .config import Config

class BehaviorPlanner:
    def __init__(self):
        self.state = "CRUISE"
        self.dwell_time = 0.0
        self.last_state = "CRUISE"

    def decide(self, ego, risk, path, intent, target_speed):
        desired_state = intent
        
        # If RiskEngine detects critical imminent collision that the planner didn't avoid
        # (e.g. obstacle suddenly appears out of nowhere)
        if risk["critical"] and not path:
            desired_state = "EMERGENCY_STOP"
            target_speed = 0.0
            
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
