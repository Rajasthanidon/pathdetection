import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.engine import SimulationEngine
from simulation.config import Config

def run_test(scenario_id, name, expected_behavior_sequence):
    print(f"--- Running Test: {name} (Scenario {scenario_id}) ---")
    engine = SimulationEngine()
    engine.scenario_id = scenario_id
    engine.reset()
    engine.running = True
    
    behaviors_seen = []
    
    for step in range(300):
        engine.step()
        state = engine.get_state()
        b = state["behavior"]
        if not behaviors_seen or behaviors_seen[-1] != b:
            behaviors_seen.append(b)
            if hasattr(engine.planner, 'last_candidates'):
                print(f"Step {step} Planner Candidates for {b}:")
                for c in engine.planner.last_candidates:
                    print(f"  {c['behavior']} (y={c['target_y']}): collision={c['is_collision']} reason={c['reason']} score={c.get('score')}")
            
    print(f"Behaviors executed: {behaviors_seen}")
    
    # Check if the expected behavior occurred
    passed = False
    for expected in expected_behavior_sequence:
        if expected in behaviors_seen:
            passed = True
            
    if passed:
        print("RESULT: PASS\n")
    else:
        print("RESULT: FAIL\n")
        
if __name__ == "__main__":
    # Test 1: Left safe, Right blocked -> Expect PASS_LEFT
    run_test(6, "Obstacle Ahead + Left Clear", ["PASS_LEFT"])
    
    # Test 2: Right safe, Left blocked -> Expect PASS_RIGHT
    run_test(7, "Obstacle Ahead + Right Clear", ["PASS_RIGHT"])
    
    # Test 3: Both blocked -> Expect FOLLOW or EMERGENCY_STOP
    run_test(8, "Obstacle Ahead + Both Blocked", ["FOLLOW", "EMERGENCY_STOP", "BRAKE"])
