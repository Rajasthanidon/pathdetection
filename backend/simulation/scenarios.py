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
            # ADAPTIVE OBSTACLE AVOIDANCE DEMO
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            env["obstacles"].append({"x": 10, "y": -6.5, "width": 1.5, "length": 1.5, "cls": "TREE"})
            env["obstacles"].append({"x": 40, "y": 6.5, "width": 2, "length": 5, "cls": "SHOP"})
            
            ego.speed = 9.0
            ego.y = 0.0
            
            # Slow/stopped vehicle directly ahead
            actors.append(Car(x=35, y=0.0, heading=0, speed=1.0))
            
            # Left lane has a safe gap (no cars near ego)
            # Right side has traffic
            actors.append(Motorcycle(x=25, y=4.0, heading=0, speed=4.0))
            actors.append(AutoRickshaw(x=45, y=3.0, heading=0, speed=5.0))
            actors.append(Car(x=10, y=-4.0, heading=0, speed=8.0)) # car far behind on left
            
        elif scenario_id == 2:
            # BUSY URBAN INTERSECTION WITHOUT SIGNAL
            env["road_left"] = -5.0
            env["road_right"] = 5.0
            # Buildings forming an intersection
            env["obstacles"].append({"x": 20, "y": -8.0, "width": 6, "length": 15, "cls": "BUILDING"})
            env["obstacles"].append({"x": 20, "y": 8.0, "width": 6, "length": 15, "cls": "BUILDING"})
            env["obstacles"].append({"x": 45, "y": -8.0, "width": 6, "length": 15, "cls": "BUILDING"})
            env["obstacles"].append({"x": 45, "y": 8.0, "width": 6, "length": 15, "cls": "BUILDING"})
            
            ego.speed = 8.0 
            
            # Crossing traffic
            actors.append(Motorcycle(x=32, y=-15, heading=1.57, speed=6.0)) 
            actors.append(Pedestrian(x=35, y=4, heading=-1.57, speed=1.2))
            actors.append(Car(x=32, y=12, heading=-1.57, speed=5.0))
            
        elif scenario_id == 3:
            # HIGHWAY MERGE WITH SLOW VEHICLES
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            env["obstacles"].append({"x": 10, "y": -7.5, "width": 1, "length": 200, "cls": "WALL"})
            env["obstacles"].append({"x": 10, "y": 7.5, "width": 1, "length": 200, "cls": "WALL"})
            # To visually represent the merge lane, we can add a polygon or use obstacles, but for now
            # the merge lane exists from y=-12 coming into y=-2
            
            ego.y = 2.0 # ego is in the middle/right lane (y=2)
            ego.speed = 15.0
            
            from .actors import MergingVehicle
            # Traffic on main highway
            actors.append(Car(x=30, y=2.0, heading=0, speed=16.0))
            actors.append(Motorcycle(x=60, y=-2.0, heading=0, speed=18.0))
            actors.append(Car(x=80, y=2.0, heading=0, speed=12.0))
            
            # Traffic in merging lane
            actors.append(MergingVehicle(x=20, y=-10.0, heading=0.3, speed=10.0, target_y=-2.0))
            actors.append(MergingVehicle(x=50, y=-8.0, heading=0.3, speed=12.0, target_y=-2.0))
            
        elif scenario_id == 4:
            # DENSE MARKET
            env["road_left"] = -2.5
            env["road_right"] = 2.5
            
            # Continuous stalls/shops on edges
            for x_pos in range(10, 150, 12):
                env["obstacles"].append({"x": x_pos, "y": -3.5, "width": 2, "length": 8, "cls": "SHOP"})
                env["obstacles"].append({"x": x_pos, "y": 3.5, "width": 2, "length": 8, "cls": "SHOP"})
                
            ego.speed = 4.0
            actors.append(Pedestrian(x=15, y=1.5, heading=1.5))
            actors.append(Pedestrian(x=20, y=-1.5, heading=-0.5))
            actors.append(Motorcycle(x=25, y=0.5, heading=0, speed=2.0))
            actors.append(AutoRickshaw(x=35, y=-0.5, heading=0, speed=1.5))
            actors.append(Pedestrian(x=45, y=0.0, heading=3.14)) 
            actors.append(Motorcycle(x=50, y=1.0, heading=3.14, speed=3.0))
            
        elif scenario_id == 5:
            # SUDDEN CATTLE CROSSING (HERO DEMO)
            env["road_left"] = -3.5
            env["road_right"] = 3.5
            # Trees on the side
            env["obstacles"].append({"x": 25, "y": 4.5, "width": 1.5, "length": 1.5, "cls": "TREE"})
            env["obstacles"].append({"x": 40, "y": -4.5, "width": 1.5, "length": 1.5, "cls": "TREE"})
            
            ego.y = 0.0
            ego.speed = 10.0 # 36 km/h
            
            # Cattle starts near the edge, scripted to cross when ego approaches
            # ScriptedAnimal will be triggered to move laterally
            actors.append(ScriptedAnimal(x=25, y=3.0, heading=-1.57, speed=0.0))
            
        elif scenario_id == 6:
            # HERO SCENARIO 1: Left is safe, right is blocked.
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            ego.speed = 10.0
            ego.y = 0.0
            
            # Obstacle in center
            actors.append(Car(x=30, y=0.0, heading=0, speed=2.0))
            # Right side blocked
            actors.append(Car(x=28, y=4.0, heading=0, speed=2.0))
            actors.append(Car(x=35, y=4.0, heading=0, speed=2.0))
            
        elif scenario_id == 7:
            # HERO SCENARIO 2: Right is safe, left is blocked.
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            ego.speed = 10.0
            ego.y = 0.0
            
            # Obstacle in center
            actors.append(Car(x=30, y=0.0, heading=0, speed=2.0))
            # Left side blocked
            actors.append(Car(x=28, y=-4.0, heading=0, speed=2.0))
            actors.append(Car(x=35, y=-4.0, heading=0, speed=2.0))
            
        elif scenario_id == 8:
            # HERO SCENARIO 3: Both sides blocked.
            env["road_left"] = -6.0
            env["road_right"] = 6.0
            ego.speed = 10.0
            ego.y = 0.0
            
            # Obstacle in center
            actors.append(Car(x=30, y=0.0, heading=0, speed=2.0))
            # Left blocked
            actors.append(Car(x=28, y=-4.0, heading=0, speed=2.0))
            # Right blocked
            actors.append(Car(x=32, y=4.0, heading=0, speed=2.0))
            
        return env, ego, actors

    @staticmethod
    def maintain_world(scenario_id, env, ego, actors):
        import random
        # Maintain a dynamic environment up to 100m ahead of the ego
        spawn_horizon = ego.x + 80.0
        
        # 1. Maintain Static Environment (e.g. continuous market stalls or highway walls)
        highest_obs_x = max([o["x"] for o in env["obstacles"]]) if env["obstacles"] else ego.x
        while highest_obs_x < spawn_horizon + 50.0:
            if scenario_id == 3: # Highway walls
                env["obstacles"].append({"x": highest_obs_x + 50, "y": -7.5, "width": 1, "length": 50, "cls": "WALL"})
                env["obstacles"].append({"x": highest_obs_x + 50, "y": 7.5, "width": 1, "length": 50, "cls": "WALL"})
                highest_obs_x += 50
            elif scenario_id == 4: # Market stalls
                env["obstacles"].append({"x": highest_obs_x + 12, "y": -3.5, "width": 2, "length": 8, "cls": "SHOP"})
                env["obstacles"].append({"x": highest_obs_x + 12, "y": 3.5, "width": 2, "length": 8, "cls": "SHOP"})
                highest_obs_x += 12
            else:
                highest_obs_x = spawn_horizon + 50.0 # No continuous static objects needed
                
        # 2. Maintain Dynamic Actors
        target_actors = {
            1: 6,  # Village
            2: 8,  # Urban
            3: 10, # Highway
            4: 12, # Market
            5: 4   # Cattle (less traffic)
        }.get(scenario_id, 5)
        
        if len(actors) < target_actors:
            # Try to spawn a new actor
            if random.random() < 0.05: # 5% chance per tick if under target
                spawn_x = spawn_horizon + random.uniform(0, 30.0)
                
                # Choose random valid y based on road width
                road_left = env.get("road_left", -3.5)
                road_right = env.get("road_right", 3.5)
                spawn_y = random.uniform(road_left + 1.0, road_right - 1.0)
                
                # Check clearance against existing actors
                clear = True
                for a in actors:
                    if abs(a.x - spawn_x) < 5.0 and abs(a.y - spawn_y) < 2.0:
                        clear = False
                        break
                        
                if clear:
                    classes = [Pedestrian, Car, Motorcycle, Animal, AutoRickshaw]
                    if scenario_id == 3: # Highway: cars/motorcycles mainly
                        classes = [Car, Car, Motorcycle]
                    elif scenario_id == 4: # Market: VRUs mainly
                        classes = [Pedestrian, Pedestrian, Motorcycle, AutoRickshaw]
                        
                    cls = random.choice(classes)
                    
                    # Randomize behavior a bit
                    heading = 0.0
                    if cls == Pedestrian or cls == Animal:
                        heading = random.uniform(-3.14, 3.14)
                    
                    from .actors import MergingVehicle
                    
                    speed_multiplier = 1.0
                    if scenario_id == 3: speed_multiplier = 1.5
                    elif scenario_id == 4: speed_multiplier = 0.7
                    
                    if scenario_id == 3 and random.random() < 0.3:
                        # 30% of spawned vehicles on highway are merging vehicles
                        new_actor = MergingVehicle(x=spawn_x, y=-12.0, heading=0.3, speed=10.0, target_y=-2.0)
                    else:
                        new_actor = cls(x=spawn_x, y=spawn_y, heading=heading)
                        new_actor.speed *= speed_multiplier
                    
                    # For cars/motorcycles on two-way roads (e.g. Village/Urban), maybe make them oncoming
                    if cls in [Car, Motorcycle, AutoRickshaw] and scenario_id in [1, 2]:
                        if spawn_y < 0: # Left lane -> Oncoming (assuming left-hand traffic)
                            new_actor.heading = 3.14
                        else:
                            new_actor.heading = 0.0
                            
                    actors.append(new_actor)
