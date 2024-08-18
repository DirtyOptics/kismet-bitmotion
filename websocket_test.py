import asyncio
import websockets
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=<YOUR_API_KEY>'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        print("Connected to Kismet WebSocket")

        while True:
            try:
                message = await websocket.recv()
                print("Received:", message)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break

asyncio.run(listen_to_kismet())
