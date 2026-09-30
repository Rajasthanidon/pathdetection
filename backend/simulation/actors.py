import math
import uuid
import random

def check_aabb_overlap(x1, y1, w1, l1, x2, y2, w2, l2):
    # Simple axis-aligned overlap test with a slight margin
    return abs(x1 - x2) < (l1/2 + l2/2 + 0.1) and abs(y1 - y2) < (w1/2 + w2/2 + 0.1)

class Actor:
    def __init__(self, x, y, heading, speed, length, width, cls_name):
        self.id = str(uuid.uuid4())[:8]
        self.x = x
        self.y = y
        self.heading = heading
        self.speed = speed
        self.length = length
        self.width = width
        self.cls_name = cls_name
        self.active = True
        
        # Physics limits
        self.max_speed = 15.0
        self.max_accel = 2.0
        self.max_decel = 4.0
        self.target_speed = speed

    def get_forward_vehicle(self, actors, ego, max_dist=30.0):
        # Find closest vehicle ahead in the same lane (roughly same Y and heading)
        min_dist = float('inf')
        closest = None
        
        all_others = actors + ([ego] if ego else [])
        for other in all_others:
            if other is self: continue
            
            # Simple lane check: must be ahead and roughly same lateral position
            dx = other.x - self.x
            dy = other.y - self.y
            dist = math.hypot(dx, dy)
            
            if dist < max_dist and dx * math.cos(self.heading) + dy * math.sin(self.heading) > 0:
                # Is it laterally close? (project onto perpendicular)
                lat_dist = abs(-dx * math.sin(self.heading) + dy * math.cos(self.heading))
                if lat_dist < (self.width/2 + other.width/2 + 0.5):
                    if dist < min_dist:
                        min_dist = dist
                        closest = other
        return closest, min_dist

    def update(self, dt, ego=None, actors=None, env=None):
        if not actors: actors = []
        
        # 1. Kinematics (Bicycle-like or point-mass bounded)
        # IDM logic: maintain safe following distance
        closest_ahead, dist_ahead = self.get_forward_vehicle(actors, ego)
        
        desired_accel = 0.0
        if closest_ahead:
            # Safe distance = min_gap + reaction_time * v + braking_diff
            safe_dist = 2.0 + 1.0 * self.speed
            v_rel = self.speed - closest_ahead.speed
            if v_rel > 0:
                safe_dist += (v_rel**2) / (2 * self.max_decel)
                
            gap = dist_ahead - (self.length/2 + closest_ahead.length/2)
            
            if gap < safe_dist:
                # Need to brake
                desired_accel = -self.max_decel * min(1.0, (safe_dist - gap) / max(1.0, safe_dist))
                if gap < 0.5: # Extreme collision avoidance
                    desired_accel = -self.max_decel * 2.0
            else:
                # Accelerate to target speed
                desired_accel = self.max_accel * (1.0 - (self.speed / max(1.0, self.target_speed)))
        else:
            # Free road
            desired_accel = self.max_accel * (1.0 - (self.speed / max(1.0, self.target_speed)))
            
        # Apply acceleration
        self.speed += desired_accel * dt
        self.speed = max(0.0, min(self.speed, self.max_speed))
        
        # Propose new position
        new_x = self.x + self.speed * math.cos(self.heading) * dt
        new_y = self.y + self.speed * math.sin(self.heading) * dt
        
        # Strict Overlap Prevention (Don't move if it puts us inside another car or obstacle)
        overlap = False
        all_others = actors + ([ego] if ego else [])
        for other in all_others:
            if other is self: continue
            if check_aabb_overlap(new_x, new_y, self.width, self.length, other.x, other.y, other.width, other.length):
                overlap = True
                break
                
        if not overlap and env and "obstacles" in env:
            for obs in env["obstacles"]:
                if check_aabb_overlap(new_x, new_y, self.width, self.length, obs["x"], obs["y"], obs["width"], obs["length"]):
                    overlap = True
                    break
                    
        if not overlap:
            self.x = new_x
            self.y = new_y
        else:
            # Full stop if we would intersect
            self.speed = 0.0

    def get_state(self):
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "heading": self.heading,
            "speed": self.speed,
            "length": self.length,
            "width": self.width,
            "cls": self.cls_name
        }

class Pedestrian(Actor):
    def __init__(self, x, y, heading, speed=1.0):
        super().__init__(x, y, heading, speed, length=0.6, width=0.6, cls_name="Pedestrian")
        self.max_speed = 2.0
        self.max_accel = 1.0

class Car(Actor):
    def __init__(self, x, y, heading, speed=5.0):
        super().__init__(x, y, heading, speed, length=4.5, width=1.8, cls_name="Car")
        self.max_speed = 20.0

class Motorcycle(Actor):
    def __init__(self, x, y, heading, speed=6.0):
        super().__init__(x, y, heading, speed, length=2.0, width=0.8, cls_name="Motorcycle")
        self.max_speed = 22.0

class AutoRickshaw(Actor):
    def __init__(self, x, y, heading, speed=4.0):
        super().__init__(x, y, heading, speed, length=2.7, width=1.4, cls_name="AutoRickshaw")
        self.max_speed = 12.0

class Animal(Actor):
    def __init__(self, x, y, heading, speed=0.5):
        super().__init__(x, y, heading, speed, length=2.0, width=0.6, cls_name="Animal")
        self.max_speed = 3.0
        self.max_accel = 1.5
        self.timer = 0.0
        self.behavior_change_time = random.uniform(1.0, 3.0)
        self.target_heading = heading

    def update(self, dt, ego=None, actors=None, env=None):
        self.timer += dt
        if self.timer > self.behavior_change_time:
            self.target_heading += random.uniform(-0.8, 0.8)
            self.timer = 0.0
            self.behavior_change_time = random.uniform(1.0, 3.0)
            
        # Smooth turning
        heading_diff = (self.target_heading - self.heading + math.pi) % (2*math.pi) - math.pi
        self.heading += max(-1.0, min(1.0, heading_diff)) * dt
        
        super().update(dt, ego, actors, env)

class ScriptedAnimal(Animal):
    def __init__(self, x, y, heading, speed=0.0):
        super().__init__(x, y, heading, speed)
        self.triggered = False
        self.behavior_change_time = 9999.0
        
    def update(self, dt, ego=None, actors=None, env=None):
        if ego and not self.triggered:
            dist_x = self.x - ego.x
            if 0 < dist_x < 30.0:
                self.triggered = True
                self.target_speed = 1.8
                # Move towards center (y=0). If y > 0, move negative y (-1.57)
                self.target_heading = -1.57 if self.y > 0 else 1.57
        super().update(dt, ego, actors, env)

class MergingVehicle(Car):
    def __init__(self, x, y, heading, speed=8.0, target_y=-2.0):
        super().__init__(x, y, heading, speed)
        self.target_y = target_y
        self.state = "APPROACHING" # APPROACHING -> MERGING -> MERGED
        
    def update(self, dt, ego=None, actors=None, env=None):
        if not actors: actors = []
        
        if self.state == "APPROACHING":
            # Wait until it's safe to merge laterally
            # Check gap in the target lane
            safe_to_merge = True
            all_others = actors + ([ego] if ego else [])
            for other in all_others:
                if other is self: continue
                # Is it in the target lane roughly?
                if abs(other.y - self.target_y) < 3.0:
                    dx = other.x - self.x
                    # If it's nearby
                    if abs(dx) < 20.0:
                        safe_to_merge = False
                        break
                        
            if safe_to_merge:
                self.state = "MERGING"
            else:
                # Slow down and wait for gap
                self.target_speed = min(5.0, self.speed * 0.9)
                
        elif self.state == "MERGING":
            self.target_speed = 12.0
            y_diff = self.target_y - self.y
            if abs(y_diff) < 0.2:
                self.state = "MERGED"
                self.y = self.target_y
                self.heading = 0.0
            else:
                # Steer towards target y smoothly
                target_heading = 0.2 * (1.0 if y_diff > 0 else -1.0)
                self.heading += (target_heading - self.heading) * dt * 2.0
                
        elif self.state == "MERGED":
            self.target_speed = 15.0
            self.heading = 0.0
            
        super().update(dt, ego, actors, env)
