import math
import uuid
import random

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

    def update(self, dt, ego=None):
        self.x += self.speed * math.cos(self.heading) * dt
        self.y += self.speed * math.sin(self.heading) * dt

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
        super().__init__(x, y, heading, speed, length=0.5, width=0.5, cls_name="Pedestrian")

class Car(Actor):
    def __init__(self, x, y, heading, speed=5.0):
        super().__init__(x, y, heading, speed, length=4.5, width=1.8, cls_name="Car")

class Motorcycle(Actor):
    def __init__(self, x, y, heading, speed=6.0):
        super().__init__(x, y, heading, speed, length=2.0, width=0.8, cls_name="Motorcycle")

class Animal(Actor):
    def __init__(self, x, y, heading, speed=0.5):
        super().__init__(x, y, heading, speed, length=2.0, width=0.6, cls_name="Animal")
        self.timer = 0.0
        self.behavior_change_time = random.uniform(1.0, 3.0)

    def update(self, dt, ego=None):
        self.timer += dt
        if self.timer > self.behavior_change_time:
            self.heading += random.uniform(-0.5, 0.5)
            self.timer = 0.0
            self.behavior_change_time = random.uniform(1.0, 3.0)
        super().update(dt, ego)

class AutoRickshaw(Actor):
    def __init__(self, x, y, heading, speed=4.0):
        super().__init__(x, y, heading, speed, length=2.6, width=1.3, cls_name="AutoRickshaw")

class ScriptedAnimal(Animal):
    def __init__(self, x, y, heading, speed=0.0):
        super().__init__(x, y, heading, speed)
        self.triggered = False
        self.behavior_change_time = 9999.0 # disable random wander
        
    def update(self, dt, ego=None):
        if ego and not self.triggered:
            # Trigger when ego gets close enough on the x axis (forward)
            dist_x = self.x - ego.x
            if 0 < dist_x < 25.0:
                self.triggered = True
                self.speed = 1.8
                # Move towards center (y=0). If y > 0, move negative y (heading = -1.57). Else positive y (heading = 1.57).
                self.heading = -1.57 if self.y > 0 else 1.57
        super().update(dt, ego)
