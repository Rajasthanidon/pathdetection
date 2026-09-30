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
            actor.update(Config.DT, self.ego)
            
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
        path = self.planner.plan(self.ego, tracks, predictions, risk, self.env)
        
        # 6. Behavior
        state, target_speed = self.behavior.decide(self.ego, risk, path is not None)
        
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
        
        # Scenario Completion (e.g. after 60s or collision)
        if collision:
            self.running = False
            self.status = "ERROR"
        elif self.time >= 60.0:
            self.running = False
            self.status = "COMPLETED"
            
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
            "metrics": self.metrics.get_summary()
        }
