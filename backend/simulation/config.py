class Config:
    # Simulation
    DT = 0.1
    
    # Ego Vehicle Parameters (Kinematic Bicycle Model)
    VEHICLE_LENGTH = 4.5
    VEHICLE_WIDTH = 1.8
    WHEELBASE = 2.8
    MAX_STEER = 0.8  # radians
    MAX_STEER_RATE = 1.5 # radians per second (allows quick avoidance)
    MAX_ACCEL = 4.0  # m/s^2
    MAX_DECEL = -5.0 # m/s^2 (emergency brake)
    MAX_SPEED = 20.0 # m/s (approx 72 km/h)
    
    # Sensor Parameters
    SENSOR_RANGE = 80.0
    SENSOR_NOISE_POS = 0.2
    SENSOR_NOISE_VEL = 0.5
    
    # Prediction
    PREDICTION_HORIZON = 3.0 # seconds
    PREDICTION_STEPS = int(PREDICTION_HORIZON / DT)
    
    # Risk & Behavior
    TTC_CRITICAL = 1.5
    TTC_WARNING = 3.0
    CLEARANCE_CRITICAL = 1.0
    CLEARANCE_WARNING = 2.0
    
    TTC_CRITICAL_VRU = 2.5
    TTC_WARNING_VRU = 4.0
    CLEARANCE_CRITICAL_VRU = 2.0
    CLEARANCE_WARNING_VRU = 3.0
    
    # Planner Weights
    W_COLLISION = 10000.0
    W_CLEARANCE = 100.0
    W_LENGTH = 1.0
    W_CURVATURE = 5.0
    W_SPEED = 10.0
    W_CONTROL = 2.0
    W_CONTINUITY = 20.0
    W_UNCERTAINTY = 50.0
    
    # Trajectory Generation
    LATERAL_SAMPLES = 7 # e.g. -3, -2, -1, 0, 1, 2, 3 meters
    LATERAL_SPACING = 0.7 # meters between samples
    LOOKAHEAD_DIST = 15.0 # meters for path generation
    
    # Grid for free space (if using occupancy grid)
    GRID_RES = 0.5 # meters per cell
