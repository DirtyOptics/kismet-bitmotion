import asyncio
import websockets
import json
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        # Subscribe to the DOT11_ADVERTISED_SSID event
        subscribe_message = {
            "SUBSCRIBE": "DOT11_ADVERTISED_SSID"
        }
        await websocket.send(json.dumps(subscribe_message))
        print("Subscribed to DOT11_ADVERTISED_SSID event")

        while True:
            message = await websocket.recv()
            print("Received:", message)

asyncio.run(listen_to_kismet())
