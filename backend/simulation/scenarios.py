from .ego import EgoVehicle
from .actors import Pedestrian, Car, Motorcycle, Animal, AutoRickshaw, ScriptedAnimal

class Scenarios:
    @staticmethod
    def load(scenario_id):
        actors = []
        ego = EgoVehicle(x=0, y=0, heading=0, speed=5.0)
        env = {
            "road_left": -3.5,
            "road_right": 3.5,
            "obstacles": []
        }

        if scenario_id == 1:
            env["road_left"] = -3.0
            env["road_right"] = 3.0
            env["obstacles"].append({"x": 10, "y": -4.0, "width": 2, "length": 5, "cls": "STALL"})
            env["obstacles"].append({"x": 40, "y": 4.0, "width": 2, "length": 5, "cls": "STALL"})
            
            ego.y = 1.0 # lateral offset
            ego.speed = 6.0
            actors.append(Pedestrian(x=15, y=3, heading=3.14)) # walking backwards
            actors.append(Animal(x=30, y=-3, heading=0.1))
            actors.append(Motorcycle(x=40, y=1, heading=-1.5, speed=2.0))
            actors.append(Motorcycle(x=60, y=-2, heading=3.1, speed=5.0))
            actors.append(AutoRickshaw(x=80, y=-1, heading=3.14, speed=4.0))
            actors.append(Pedestrian(x=25, y=-3.5, heading=-1.0))
            
        elif scenario_id == 2:
            env["road_left"] = -5.0
            env["road_right"] = 5.0
            env["obstacles"].append({"x": 20, "y": -8.0, "width": 6, "length": 10, "cls": "BUILDING"})
            env["obstacles"].append({"x": 20, "y": 8.0, "width": 6, "length": 10, "cls": "BUILDING"})
            env["obstacles"].append({"x": 40, "y": -8.0, "width": 6, "length": 10, "cls": "BUILDING"})
            env["obstacles"].append({"x": 40, "y": 8.0, "width": 6, "length": 10, "cls": "BUILDING"})
            
            ego.speed = 8.0 # ~28 km/h
            ego.y = 0.0
            
            actors.append(Motorcycle(x=30, y=-15, heading=1.57, speed=7.5)) 
            actors.append(Pedestrian(x=40, y=3.5, heading=-1.57, speed=1.2))
            actors.append(Car(x=30, y=10, heading=1.57, speed=0.0))
            actors.append(AutoRickshaw(x=50, y=-2, heading=3.14, speed=3.0))
            
        elif scenario_id == 3:
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            env["obstacles"].append({"x": 100, "y": -7.0, "width": 1, "length": 200, "cls": "WALL"})
            env["obstacles"].append({"x": 100, "y": 9.0, "width": 1, "length": 200, "cls": "WALL"})
            
            ego.y = -2.0 # middle lane
            ego.speed = 15.0
            actors.append(Car(x=80, y=-2.0, heading=0, speed=8.0))
            actors.append(Car(x=30, y=-6.0, heading=0, speed=18.0))
            actors.append(Car(x=40, y=4.0, heading=-0.2, speed=10.0))
            actors.append(Car(x=120, y=2.0, heading=3.14, speed=15.0))
            
        elif scenario_id == 4:
            env["road_left"] = -3.0
            env["road_right"] = 3.0
            for x_pos in range(0, 150, 15):
                env["obstacles"].append({"x": x_pos, "y": -4.5, "width": 3, "length": 10, "cls": "SHOP"})
                env["obstacles"].append({"x": x_pos, "y": 4.5, "width": 3, "length": 10, "cls": "SHOP"})
                
            ego.y = 0.5
            ego.speed = 4.0
            actors.append(Pedestrian(x=10, y=2.5, heading=1.5))
            actors.append(Pedestrian(x=12, y=-2.5, heading=-0.5))
            actors.append(Motorcycle(x=18, y=1, heading=0, speed=1.0))
            actors.append(AutoRickshaw(x=25, y=-1, heading=0, speed=1.5))
            actors.append(Pedestrian(x=35, y=0, heading=3.14)) 
            actors.append(Animal(x=45, y=-3, heading=0.5))
            actors.append(Pedestrian(x=50, y=3, heading=-1.57))
            
        elif scenario_id == 5:
            env["road_left"] = -3.5
            env["road_right"] = 3.5
            env["obstacles"].append({"x": 30, "y": 6.0, "width": 2, "length": 2, "cls": "TREE"})
            env["obstacles"].append({"x": 40, "y": -6.0, "width": 2, "length": 2, "cls": "TREE"})
            
            ego.y = 0.0
            ego.speed = 10.0 # 36 km/h
            
            actors.append(Car(x=60, y=-3.0, heading=3.14, speed=8.0))
            actors.append(ScriptedAnimal(x=22, y=4.5, heading=1.57, speed=0.0))
            
        return env, ego, actors
