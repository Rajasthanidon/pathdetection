# Environment Settings

The environment utilized for this project was evaluated dynamically at runtime.

- **OS**: Windows (x64)
- **CPU**: 12th Gen Intel Core i5-12450H (8 Cores, 12 Logical)
- **RAM**: 16 GB
- **GPU**: Intel(R) UHD Graphics
- **Python**: 3.14.6 (MSYS2)
- **Node.js**: v24.16.0
- **MATLAB/Simulink/RoadRunner**: NOT FOUND on the system.

Because MATLAB and RoadRunner were unavailable, the platform was constructed using a robust custom Python backend simulating the autonomous driving pipeline deterministically, integrated with a React dashboard for visualization. The architecture uses a decoupled design, meaning the backend engine can be seamlessly replaced by MATLAB/Simulink/RoadRunner at a later stage via an adapter.
