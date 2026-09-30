import asyncio
import json
import math
import os
import traceback
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute
from starlette.responses import JSONResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

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
                            await client.send_text(msg)
                        except Exception:
                            pass
        except Exception as e:
            print(f"Error in simulation loop: {e}")
            traceback.print_exc()
                
        sleep_time = Config.DT / speed_multiplier if speed_multiplier > 0 else Config.DT
        await asyncio.sleep(sleep_time)

async def health_check(request):
    return JSONResponse({"status": "ok", "service": "autonomous-india-road"})

async def websocket_endpoint(websocket):
    global speed_multiplier
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)
            if data["type"] == "HELLO":
                await websocket.send_text(json.dumps({
                    "type": "READY", 
                    "server": "autonomous-india-road", 
                    "protocol": 1
                }))
                safe_state = sanitize_for_json(engine.get_state())
                await websocket.send_text(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
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
                await websocket.send_text(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
            elif data["type"] == "SET_SCENARIO":
                engine.scenario_id = data["scenario_id"]
                engine.reset()
                safe_state = sanitize_for_json(engine.get_state())
                await websocket.send_text(json.dumps({"type": "STATE", "data": safe_state}, allow_nan=False))
            elif data["type"] == "SET_SPEED":
                speed_multiplier = data["speed"]
    except Exception as e:
        pass
    finally:
        if websocket in clients:
            clients.remove(websocket)

@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()

frontend_origins = os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173")
origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

middleware = [
    Middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
]

async def root_endpoint(request):
    return JSONResponse({"service": "PathDetection Backend", "status": "ok"})

app = Starlette(
    routes=[
        Route("/", root_endpoint),
        Route("/health", health_check),
        WebSocketRoute("/ws", websocket_endpoint)
    ],
    middleware=middleware,
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
