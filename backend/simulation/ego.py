import math
from .config import Config

class EgoVehicle:
    def __init__(self, x=0.0, y=0.0, heading=0.0, speed=0.0):
        self.x = x
        self.y = y
        self.heading = heading  # radians
        self.speed = speed      # m/s
        self.accel = 0.0        # m/s^2
        self.steer = 0.0        # radians
        
        # Dimensions
        self.length = Config.VEHICLE_LENGTH
        self.width = Config.VEHICLE_WIDTH
        self.wheelbase = Config.WHEELBASE

    def update(self, dt):
        """Update vehicle state using Kinematic Bicycle Model."""
        # 1. Update speed
        self.speed += self.accel * dt
        self.speed = max(0.0, min(self.speed, Config.MAX_SPEED))
        
        # 2. Update position and heading
        if self.speed > 0.01:
            beta = math.atan(0.5 * math.tan(self.steer))
            # simplified model
            self.x += self.speed * math.cos(self.heading + beta) * dt
            self.y += self.speed * math.sin(self.heading + beta) * dt
            self.heading += (self.speed / self.wheelbase) * math.sin(beta) * dt

        # Normalize heading
        self.heading = (self.heading + math.pi) % (2 * math.pi) - math.pi

    def apply_control(self, accel, steer):
        """Apply control inputs with limits."""
        self.accel = max(Config.MAX_DECEL, min(accel, Config.MAX_ACCEL))
        self.steer = max(-Config.MAX_STEER, min(steer, Config.MAX_STEER))

    def get_state(self):
        return {
            "x": self.x,
            "y": self.y,
            "heading": self.heading,
            "speed": self.speed,
            "accel": self.accel,
            "steer": self.steer,
            "length": self.length,
            "width": self.width
        }
