# Automated Testing & Scenarios

The platform evaluates the ego vehicle across 5 required scenarios corresponding to the SIH problem statement:

1. **Unmarked Village Road**: Tests navigation around multiple static and dynamic obstacles without lane constraints.
2. **Unsignalized Urban Intersection**: Tests yielding, prediction, and gap acceptance at cross traffic.
3. **Highway Merge**: Tests longitudinal speed control and yielding to faster merging traffic.
4. **Dense Market**: Low-speed high-density environment requiring frequent replanning.
5. **Sudden Cattle Crossing**: Stress-test for the Time-To-Collision (TTC) risk engine and emergency braking supervisor.

## How to Test
Currently, scenarios are executed interactively via the Dashboard.
A Python-based automated testing script can be created that instantiates `SimulationEngine`, runs `step()` until the scenario finishes, and asserts `metrics.collisions == 0`.
