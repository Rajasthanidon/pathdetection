import unittest
from simulation.ego import EgoVehicle
from simulation.planning import AdaptivePlanner
from simulation.scenarios import Scenarios
from simulation.control import Controller
from simulation.engine import SimulationEngine
import math

class TestPhysicsAndPlanner(unittest.TestCase):
    def test_straight_road(self):
        ego = EgoVehicle(x=0, y=0, heading=0, speed=10)
        ego.update(0.1)
        self.assertGreater(ego.x, 0)
        self.assertAlmostEqual(ego.y, 0, places=3)
        self.assertAlmostEqual(ego.heading, 0, places=3)
        
    def test_kinematics(self):
        ego = EgoVehicle(x=0, y=0, heading=0, speed=10)
        ego.apply_control(accel=0.0, steer=0.2)
        ego.update(0.1)
        self.assertGreater(ego.heading, 0) # Should turn counter-clockwise (Left/Positive)
        
    def test_road_corridor_constraint(self):
        planner = AdaptivePlanner()
        env = {"road_left": -2.0, "road_right": 2.0, "obstacles": []}
        ego = EgoVehicle(x=0, y=0, heading=0, speed=5)
        candidates = planner.generate_candidates(ego, env)
        
        # Check all candidates stay within road limits
        for path in candidates:
            for x, y in path:
                self.assertGreaterEqual(y, -2.0 - 1.0) # margin
                self.assertLessEqual(y, 2.0 + 1.0)
                
    def test_scenarios_execute(self):
        engine = SimulationEngine()
        for i in range(1, 6):
            engine.scenario_id = i
            engine.reset()
            engine.running = True
            try:
                for _ in range(50):
                    engine.step()
            except Exception as e:
                self.fail(f"Scenario {i} failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
