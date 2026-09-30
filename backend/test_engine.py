import asyncio
import json
import math
from simulation.engine import SimulationEngine

def sanitize_for_json(obj):
    if isinstance(obj, float):
        return obj if math.isfinite(obj) else None
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(value) for value in obj]
    if isinstance(obj, tuple):
        return [sanitize_for_json(value) for value in obj]
    return obj

# 1. Explicit Dictionary Test
test_dict = {
    "a": float("inf"),
    "b": float("-inf"),
    "c": float("nan"),
    "d": 0.0,
    "e": 12.5
}
safe_test_dict = sanitize_for_json(test_dict)
json_result = json.dumps(safe_test_dict, allow_nan=False)
print("Explicit test result:", json_result)
assert "null" in json_result and "NaN" not in json_result and "Infinity" not in json_result

# 2. Engine State Test
engine = SimulationEngine()
engine.reset()

state = engine.get_state()
safe_state = sanitize_for_json(state)
msg = json.dumps(safe_state, allow_nan=False)
print("Initial state serialization success. Length:", len(msg))

engine.running = True
engine.step()
state2 = engine.get_state()
safe_state2 = sanitize_for_json(state2)
msg2 = json.dumps(safe_state2, allow_nan=False)
print("Post-step serialization success. Length:", len(msg2))

