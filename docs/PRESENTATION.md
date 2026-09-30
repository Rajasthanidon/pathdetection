# SIH Presentation Structure

**1. Problem Statement**
Adaptive Path Planning & Collision Avoidance on Unstructured Indian Roads.

**2. The Challenge of Indian Roads**
Unlike structured western highways, Indian roads have missing markings, extremely diverse traffic (cows, rickshaws, pedestrians), and erratic driving behaviors (wrong-way driving, sudden crossing). Traditional lane-keeping AI fails here.

**3. Proposed Architecture**
- Closed-Loop Simulation System
- Sensor Fusion -> Object Tracking -> Motion Prediction -> Risk Assessment -> Free-Space Path Planning -> Vehicle Control

**4. Core Innovation: Adaptive Free-Space Planning**
Instead of following lanes, our planner samples multiple lateral candidate trajectories into the "Drivable Free Space", scores them based on clearance and curvature, and seamlessly replans dynamically around unstructured obstacles.

**5. Collision Avoidance & Risk Engine**
Calculates Time-To-Collision (TTC) continuously. An independent Safety Supervisor triggers emergency braking if the primary planner fails to find a safe path.

**6. Demonstrated Scenarios**
1. Unmarked Village Road (Animal/Pedestrian avoidance)
2. Urban Intersection (Yielding & Prediction)
3. Highway Merge
4. Dense Market (Low-speed replanning)
5. Sudden Cattle Crossing (Emergency Supervisor Test)

**7. Real-Time Dashboard**
We built a deterministic simulation engine running in Python, interfaced with a professional React-based visualization dashboard streaming telemetry at 10Hz via WebSockets.

**8. Results**
0 Collisions in all scenarios compared to baseline fixed-path followers.

**9. Limitations & Future Scope**
Currently simulates perception bounding boxes with noise. Future deployment involves porting the architecture via ROS2 into an actual hardware perception stack with Deep Learning models.
