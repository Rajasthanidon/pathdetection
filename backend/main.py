import asyncio
import json
import websockets
from simulation.engine import SimulationEngine
from simulation.config import Config

engine = SimulationEngine()
clients = set()
speed_multiplier = 1.0

import math

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

async def simulation_loop():
    print("Simulation loop started!")
    while True:
        try:
            if engine.running:
                engine.step()
            
            state = engine.get_state()
            if clients:
                safe_state = sanitize_for_json(state)
                try:
                    msg = json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False)
                except Exception as json_e:
                    print(f"JSON SERIALIZATION ERROR\ntype: {type(json_e)}\nvalue: {json_e}")
                    # Don't send, but continue loop
                    msg = None
                    
                if msg:
                    for client in list(clients):
                        try:
                            await client.send(msg)
                        except Exception as e:
                            pass
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            import traceback
            traceback.print_exc()
                
        # Sleep according to speed multiplier (if 0.5x -> sleep longer)
        sleep_time = Config.DT / speed_multiplier if speed_multiplier > 0 else Config.DT
        await asyncio.sleep(sleep_time)

async def handler(websocket):
    global speed_multiplier
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["type"] == "HELLO":
                await websocket.send(json.dumps({
                    "type": "READY", 
                    "server": "autonomous-india-road", 
                    "protocol": 1
                }))
                safe_state = sanitize_for_json(engine.get_state())
                await websocket.send(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
            elif data["type"] == "START":
                if engine.status in ["COMPLETED", "ERROR"]:
                    engine.reset()
                engine.running = True
                engine.status = "RUNNING"
            elif data["type"] == "PAUSE":
                engine.running = False
                engine.status = "PAUSED"
            elif data["type"] == "RESET":
                engine.reset()
                safe_state = sanitize_for_json(engine.get_state())
                await websocket.send(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
            elif data["type"] == "SET_SCENARIO":
                engine.scenario_id = data["scenario_id"]
                engine.reset()
                safe_state = sanitize_for_json(engine.get_state())
                await websocket.send(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
            elif data["type"] == "SET_SPEED":
                speed_multiplier = data["speed"]
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)

async def main():
    # Start the simulation loop in the background
    asyncio.create_task(simulation_loop())
    # Start the WebSocket server
    print("Starting WebSocket server on ws://127.0.0.1:8001")
    async with websockets.serve(handler, "127.0.0.1", 8001):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
