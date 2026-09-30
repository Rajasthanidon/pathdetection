# Software Architecture

The platform operates using a closed-loop deterministic simulation that executes at a fixed timestep (`dt = 0.1s`).

## Backend (Python)
- **Engine (`engine.py`)**: The central heartbeat. Manages simulation time, ego vehicle state, actors, and sequentially invokes perception, risk, behavior, planning, and control modules.
- **Ego Vehicle (`ego.py`)**: Implements a Kinematic Bicycle Model simulating realistic vehicle motion and constraints.
- **Actors (`actors.py`)**: Defines dynamic traffic participants (Car, Motorcycle, Pedestrian, Animal, AutoRickshaw).
- **Perception & Tracking (`perception.py`)**: Simulates sensor detections (within a radius) and injects noise. Maintains ID-based tracks across frames.
- **Prediction (`perception.py`)**: Implements short-term constant-velocity predictions for all tracked actors.
- **Risk Engine (`risk.py`)**: Computes minimum clearance and Time-To-Collision (TTC) based on predictions. Evaluates severity (SAFE, CAUTION, CRITICAL).
- **Behavior Planner (`behavior.py`)**: State machine that sets target speeds based on risk (CRUISE, YIELD, EMERGENCY_BRAKE).
- **Adaptive Planner (`planning.py`)**: Implements free-space trajectory generation (lateral sampling) and collision checking. Selects the trajectory that minimizes curvature while maximizing clearance.
- **Controller (`control.py`)**: A Pure Pursuit controller for lateral tracking and P-controller for longitudinal speed.
- **Metrics (`metrics.py`)**: Real-time evaluation of planning latency, collisions, and clearances.

## Frontend (React + Vite)
- **WebSocket Connection**: Subscribes to the backend's state updates at ~10Hz.
- **SimulationView**: Renders ego, actors, tracks, bounding boxes, predicted paths, and the selected trajectory on a responsive 2D canvas.
- **Telemetry**: Displays numeric metrics, risk indicators, and behavior states.
- **Controls**: Interactive commands (Start, Pause, Reset, Change Scenario).
