class MetricsEngine:
    def __init__(self):
        self.collisions = 0
        self.near_collisions = 0
        self.min_clearance = float('inf')
        self.min_ttc = float('inf')
        self.planning_times = []
        self.replans = 0
        self.path_length = 0.0
        self.emergency_brakes = 0
        self.last_state = "CRUISE"
        self.last_pos = None

    def update(self, ego, risk, plan_time, collision, state):
        if not hasattr(self, 'in_collision'):
            self.in_collision = False
            
        if collision and not self.in_collision:
            self.collisions += 1
            
        self.in_collision = collision
            
        if risk["min_clearance"] < 1.0 and risk["min_clearance"] >= 0:
            self.near_collisions += 1
            
        if risk["min_clearance"] < self.min_clearance:
            self.min_clearance = risk["min_clearance"]
            
        if risk["min_ttc"] < self.min_ttc:
            self.min_ttc = risk["min_ttc"]
            
        self.planning_times.append(plan_time)
        
        if self.last_pos:
            import math
            dx = ego.x - self.last_pos[0]
            dy = ego.y - self.last_pos[1]
            self.path_length += math.hypot(dx, dy)
        self.last_pos = (ego.x, ego.y)
        
        if state == "EMERGENCY_STOP" and self.last_state != "EMERGENCY_STOP":
            self.emergency_brakes += 1
            
        if self.last_state != "CRUISE" and state == "CRUISE":
            pass # just a state change
        elif self.last_state != state:
            self.replans += 1
            
        self.last_state = state

    def get_summary(self):
        avg_plan = sum(self.planning_times)/len(self.planning_times) if self.planning_times else 0.0
        return {
            "collisions": self.collisions,
            "near_misses": self.near_collisions,
            "min_clearance": round(self.min_clearance, 2),
            "min_ttc": round(self.min_ttc, 2),
            "replans": self.replans,
            "avg_plan_time_ms": round(avg_plan * 1000, 2),
            "path_length": round(self.path_length, 2),
            "emergency_brakes": self.emergency_brakes
        }
