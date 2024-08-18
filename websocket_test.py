import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816"
    async with websockets.connect(uri) as websocket:
        # Send subscription message
        subscribe_message = {"SUBSCRIBE": "DOT11_ADVERTISED_SSID"}
        await websocket.send(json.dumps(subscribe_message))

        # Receive and print messages
        while True:
            try:
                message = await websocket.recv()
                print(message)
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

asyncio.run(test_websocket())
