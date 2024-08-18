import asyncio
import websockets
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        try:
            while True:
                message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                print("Received:", message)
        except asyncio.TimeoutError:
            print("No data received within the last 10 seconds, waiting...")
        except websockets.ConnectionClosed:
            print("WebSocket connection closed")

asyncio.run(listen_to_kismet())
