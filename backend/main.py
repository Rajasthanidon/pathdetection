import asyncio
import json
import websockets
import http
import math
import os
import traceback
from simulation.engine import SimulationEngine
from simulation.config import Config

engine = SimulationEngine()
clients = set()
speed_multiplier = 1.0

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
    global speed_multiplier
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
                    msg = None
                    
                if msg:
                    for client in list(clients):
                        try:
                            await client.send(msg)
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            traceback.print_exc()
                
        sleep_time = Config.DT / speed_multiplier if speed_multiplier > 0 else Config.DT
        await asyncio.sleep(sleep_time)

async def handler(websocket, path):
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
    except Exception as e:
        print(f"WebSocket exception: {e}")
    finally:
        if websocket in clients:
            clients.remove(websocket)

async def process_request(path, request_headers):
    if path == "/health":
        body = json.dumps({"status": "ok", "service": "autonomous-india-road"}).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
        ]
        return http.HTTPStatus.OK, headers, body
    if path != "/ws":
        return http.HTTPStatus.NOT_FOUND, [], b"Not found"
    return None

async def main():
    asyncio.create_task(simulation_loop())
    
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting WebSocket server on ws://0.0.0.0:{port}/ws")
    
    # process_request handles HTTP /health, handler handles WS /ws
    async with websockets.serve(handler, "0.0.0.0", port, process_request=process_request):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
