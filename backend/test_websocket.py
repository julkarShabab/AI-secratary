import asyncio
import json
import websockets

async def test_chat():
    uri = "ws://localhost:8000/ws/chat/test_session_001"

    async with websockets.connect(
        uri,
        open_timeout=30,
        ping_interval=None,
        ping_timeout=None
    ) as ws:

        print("=== Test 1: Connection ===")
        response = await ws.recv()
        data = json.loads(response)
        print(f"  Type: {data['type']}")
        print(f"  Message: {data['message']}")

        print("\n=== Test 2: Send a message ===")
        await ws.send(json.dumps({"message": "What can you help me with?"}))

        while True:
            response = await ws.recv()
            data = json.loads(response)
            print(f"  Type: {data['type']}")
            print(f"  Message: {data['message']}")
            if data["type"] == "message":
                break

        print("\n=== Test 3: Ask about emails ===")
        await ws.send(json.dumps({"message": "Check my latest emails"}))

        while True:
            response = await ws.recv()
            data = json.loads(response)
            print(f"  Type: {data['type']}")
            if data["type"] == "message":
                print(f"  Message: {data['message'][:200]}...")
                break

asyncio.run(test_chat())