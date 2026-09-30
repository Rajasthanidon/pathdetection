import time
from simulation.engine import SimulationEngine
from simulation.actors import ScriptedAnimal

def test_far_cattle():
    print("--- Test: Far Cattle (No Emergency Braking) ---")
    engine = SimulationEngine()
    engine.scenario_id = 5
    engine.reset()
    
    # Move cattle far away
    cattle = [a for a in engine.actors if isinstance(a, ScriptedAnimal)][0]
    cattle.y = 100.0 # 100m away
    
    engine.running = True
    
    braked = False
    for _ in range(30):
        engine.step()
        state = engine.get_state()
        if "BRAKE" in state["behavior"]:
            braked = True
            
    assert not braked, "Vehicle braked for a far-away cattle!"
    print("PASS: Vehicle did not brake.")

def test_near_cattle():
    print("--- Test: Near Cattle (Emergency Braking & Replanning) ---")
    engine = SimulationEngine()
    engine.scenario_id = 5
    engine.reset()
    
    # Cattle is default (y=22, x=4.0)
    engine.running = True
    
    braked = False
    replanned = False
    critical = False
    
    for i in range(80):
        engine.step()
        state = engine.get_state()
        if "BRAKE" in state["behavior"]:
            braked = True
        if state.get("replanning", False):
            replanned = True
        if state["risk"]["risk_level"] == "CRITICAL":
            critical = True
            
        print(f"Step {i}: Risk={state['risk']['risk_level']}, Behavior={state['behavior']}")
            
    assert critical, "Risk did not reach CRITICAL!"
    assert replanned, "Vehicle did not replan!"
    assert braked, "Vehicle did not brake!"
    print("PASS: Vehicle properly detected near cattle, reached CRITICAL risk, replanned, and braked.")

if __name__ == "__main__":
    test_far_cattle()
    test_near_cattle()
