import random
import math
from .config import Config

class PerceptionSystem:
    def __init__(self):
        self.tracks = {} # id -> track state
        
    def detect_and_track(self, ego, actors):
        # 1. Simulate Sensors (Camera, LiDAR, Radar) with Sensor Fusion Concept
        observations = []
        for a in actors:
            dx = a.x - ego.x
            dy = a.y - ego.y
            dist = math.hypot(dx, dy)
            if dist < Config.SENSOR_RANGE:
                # Add noise
                obs_x = a.x + random.gauss(0, Config.SENSOR_NOISE_POS)
                obs_y = a.y + random.gauss(0, Config.SENSOR_NOISE_POS)
                obs_v = a.speed + random.gauss(0, Config.SENSOR_NOISE_VEL)
                
                # Determine mock sensor sources based on distance
                sources = ["camera"]
                if dist < 60: sources.append("radar")
                if dist < 40: sources.append("lidar")
                
                observations.append({
                    "id": a.id,
                    "x": obs_x,
                    "y": obs_y,
                    "heading": a.heading,
                    "speed": obs_v,
                    "length": a.length,
                    "width": a.width,
                    "cls": a.cls_name,
                    "dist": dist,
                    "source": sources,
                    "confidence": min(1.0, 0.95 + len(sources)*0.01 - (dist/Config.SENSOR_RANGE)*0.1)
                })
        
        # 2. Tracking (Simple Kalman-filter concept: smooth update, stable ID)
        current_ids = set()
        for obs in observations:
            tid = obs["id"]
            current_ids.add(tid)
            if tid not in self.tracks:
                obs["age"] = 1
                self.tracks[tid] = obs
            else:
                alpha = 0.6 # Gain
                self.tracks[tid]["x"] = alpha*obs["x"] + (1-alpha)*self.tracks[tid]["x"]
                self.tracks[tid]["y"] = alpha*obs["y"] + (1-alpha)*self.tracks[tid]["y"]
                self.tracks[tid]["speed"] = alpha*obs["speed"] + (1-alpha)*self.tracks[tid]["speed"]
                self.tracks[tid]["heading"] = obs["heading"]
                self.tracks[tid]["dist"] = obs["dist"]
                self.tracks[tid]["source"] = obs["source"]
                self.tracks[tid]["confidence"] = obs["confidence"]
                self.tracks[tid]["age"] += 1

        # Remove old tracks
        for tid in list(self.tracks.keys()):
            if tid not in current_ids:
                del self.tracks[tid]
                
        return list(self.tracks.values())

    def predict(self, tracks, ego):
        # Behavior-Aware Motion Prediction
        predictions = {}
        for t in tracks:
            x, y, h, s = t["x"], t["y"], t["heading"], t["speed"]
            cls = t["cls"]
            
            # Determine motion class
            motion_class = "normal"
            if s < 0.5:
                motion_class = "stopped"
            else:
                # Check crossing (heading roughly perpendicular to ego)
                heading_diff = abs((h - ego.heading + math.pi) % (2*math.pi) - math.pi)
                if 1.0 < heading_diff < 2.1: # roughly 60 to 120 degrees
                    motion_class = "crossing"
                elif 0.2 < heading_diff <= 1.0:
                    motion_class = "merging"
                    
            # Base uncertainty
            uncertainty = 0.5
            if cls in ["Pedestrian", "Animal", "ScriptedAnimal", "Bicycle"]:
                uncertainty = 1.5 # VRU higher uncertainty
                
            if motion_class in ["crossing", "merging"]:
                uncertainty *= 1.5
                
            preds = []
            for step in range(Config.PREDICTION_STEPS):
                dt = Config.DT * step
                px = x + s * math.cos(h) * dt
                py = y + s * math.sin(h) * dt
                preds.append([px, py])
                
            predictions[t["id"]] = {
                "path": preds,
                "motion_class": motion_class,
                "uncertainty": uncertainty
            }
        return predictions
