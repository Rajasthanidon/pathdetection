# Autonomous India Road Simulation Platform

This project implements an Adaptive Path Planning and Collision Avoidance system tailored for Unstructured Indian Roads, built for the Smart India Hackathon.

## What it does
The platform simulates an autonomous ego vehicle navigating complex, unstructured environments typical in India. It avoids collisions, predicts actor movements, calculates time-to-collision (TTC), and dynamically replans its free-space trajectory. It runs a fully closed-loop deterministic simulation in Python with a React/Vite visualization dashboard.

## How to Install
1. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # (or .\venv\bin\python.exe on Windows)
   pip install websockets
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

## How to Run
1. Start the backend simulation server (WebSocket):
   ```bash
   cd backend
   python main.py
   ```
2. Start the frontend dashboard:
   ```bash
   cd frontend
   npm run dev
   ```
3. Open the browser at `http://localhost:5173`.

## Demo Mode / How to Select Scenarios
1. Open the dashboard.
2. Under "Controls", select a scenario from the dropdown (e.g., "1. Unmarked Village Road", "5. Sudden Cattle Crossing").
3. Click **Start** to run the simulation.
4. Watch the telemetry and simulation view update in real-time.

## Architecture & Limitations
Please see the `docs/` folder for `ARCHITECTURE.md`, `LIMITATIONS.md`, and `RESULTS.md`.
