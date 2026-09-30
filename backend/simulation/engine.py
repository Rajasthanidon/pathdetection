import time
from .config import Config
from .scenarios import Scenarios
from .perception import PerceptionSystem
from .risk import RiskEngine
from .planning import AdaptivePlanner
from .behavior import BehaviorPlanner
from .control import Controller
from .metrics import MetricsEngine

class SimulationEngine:
    def __init__(self):
        self.running = False
        self.status = "IDLE"
        self.scenario_id = 1
        self.perception = PerceptionSystem()
        self.risk_engine = RiskEngine()
        self.planner = AdaptivePlanner()
        self.behavior = BehaviorPlanner()
        self.metrics = MetricsEngine()
        self.last_predictions = {}
        self.last_risk = {}
        self.last_tracks = []
        self.reset()
        
    def reset(self):
        self.env, self.ego, self.actors = Scenarios.load(self.scenario_id)
        self.perception = PerceptionSystem()
        self.planner = AdaptivePlanner()
        self.behavior = BehaviorPlanner()
        self.metrics = MetricsEngine()
        self.time = 0.0
        self.state_history = []
        self.running = False
        self.status = "IDLE"
        self.last_predictions = {}
        self.last_risk = {"risk_level": "SAFE", "min_ttc": float('inf'), "min_clearance": float('inf'), "critical": False}
        self.last_tracks = []
        
    def step(self):
        if not self.running:
            return
            
        self.status = "RUNNING"
        start_time = time.time()
        
        # 1. Update Actors
        for actor in self.actors:
            actor.update(Config.DT, ego=self.ego, actors=self.actors, env=self.env)
            
        # 2. Perception & Tracking
        tracks = self.perception.detect_and_track(self.ego, self.actors)
        self.last_tracks = list(tracks)
        
        # 3. Prediction
        predictions = self.perception.predict(tracks, self.ego)
        self.last_predictions = predictions
        
        # 4. Risk Assessment (evaluates current/last trajectory)
        current_path = self.planner.last_path if hasattr(self.planner, 'last_path') else None
        risk = self.risk_engine.calculate_risk(self.ego, tracks, predictions, current_path)
        self.last_risk = risk
        
        # 5. Planning
        path, intent, target_speed = self.planner.plan(self.ego, tracks, predictions, self.env, risk)
        
        # 6. Behavior
        state, target_speed = self.behavior.decide(self.ego, risk, path, intent, target_speed)
        
        # 7. Control
        accel, steer = Controller.pure_pursuit(self.ego, path, target_speed)
        
        # 8. Update Ego
        self.ego.apply_control(accel, steer)
        self.ego.update(Config.DT)
        
        self.time += Config.DT
        plan_time = time.time() - start_time
        
        # 9. Metrics
        collision = (risk["min_clearance"] < 0)
        self.metrics.update(self.ego, risk, plan_time, collision, state)
        
        # 10. Continuous Environment Maintenance
        # Clean up actors and obstacles behind the ego vehicle
        self.actors = [a for a in self.actors if a.x > self.ego.x - 30.0]
        self.env["obstacles"] = [o for o in self.env["obstacles"] if o["x"] > self.ego.x - 30.0]
        
        # Maintain traffic density / scenario continuity
        Scenarios.maintain_world(self.scenario_id, self.env, self.ego, self.actors)
        
        # Handle Collision Safety State (Ego recovery)
        if collision:
            self.status = "COLLISION_RECOVERY"
            # In a real system, a collision might disable the vehicle.
            # Here we just slow it down drastically to simulate impact/recovery, but let it continue.
            self.ego.speed *= 0.8
        else:
            self.status = "RUNNING"
            
    def get_state(self):
        return {
            "time": self.time,
            "status": self.status,
            "scenario_id": self.scenario_id,
            "ego": self.ego.get_state(),
            "actors": [a.get_state() for a in self.actors],
            "tracks": self.last_tracks,
            "predictions": self.last_predictions,
            "path": self.planner.last_path if self.planner.last_path else [],
            "candidates": self.planner.last_candidates if hasattr(self.planner, 'last_candidates') else [],
            "replanning": self.planner.replanning if hasattr(self.planner, 'replanning') else False,
            "risk": self.last_risk,
            "behavior": self.behavior.state,
            "memory": self.planner.memory.get_stats() if hasattr(self.planner, 'memory') else None,
            "metrics": self.metrics.get_summary()
        }
