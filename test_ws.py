import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://127.0.0.1:8001/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket.")
            await websocket.send(json.dumps({"type": "HELLO", "client": "test_client"}))
            print("Sent HELLO.")
            
            ready_msg = await websocket.recv()
            print(f"Received READY: {ready_msg[:100]}")
            
            state_msg = await websocket.recv()
            print(f"Received STATE: {state_msg[:100]}...")
            
            await websocket.send(json.dumps({"type": "START"}))
            print("Sent START.")
            
            for _ in range(30):
                state_msg = await websocket.recv()
                state_data = json.loads(state_msg)
                time_val = state_data.get("data", {}).get("time", -1)
                print(f"Received TICK STATE, time: {time_val}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
