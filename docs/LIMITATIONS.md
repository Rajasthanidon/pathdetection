# Limitations & Simulated Features

## Implemented Features (Working)
- Complete Simulation Engine (dt=0.1s)
- React+Vite Real-time UI Visualization
- Kinematic Bicycle Model
- 5 Distinct Traffic Actors (with simple behaviors)
- Sensor Observation Generation with Gaussian Noise
- Tracking & Constant Velocity Prediction
- TTC Risk Assessment Engine
- Adaptive Free-Space Path Planner (Trajectory Generation & Scoring)
- Pure Pursuit Controller & Emergency Braking Supervisor

## Simulated / Assumed Features
- **Deep Learning Perception**: We bypass raw camera/lidar point cloud processing. The simulation generates ground-truth bounding boxes and adds Gaussian noise to simulate the *output* of a sensor fusion layer.
- **Advanced Prediction**: We use constant velocity prediction. Real-world Indian traffic prediction would require graph neural networks predicting multi-modal trajectories.
- **Map Geometry**: Currently, non-drivable regions are treated as simple bounding lines. Complex occupancy grids are recommended for real deployment.
- **Framework Limits**: Since MATLAB and RoadRunner were unavailable on the evaluation machine, Python was chosen as a fallback to ensure a complete, runnable solution could be delivered.

## Future Deployment
The backend `SimulationEngine` serves as a clean adapter. It can be wrapped in ROS2 nodes and replaced with Unreal Engine (Carla) or MATLAB/Simulink automated driving toolboxes for production deployment.
