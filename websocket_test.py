import asyncio
import websockets
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        print("Connected to Kismet WebSocket")

        while True:
            try:
                # Receive message from the WebSocket
                message = await websocket.recv()
                # Print the raw message received from the Kismet WebSocket
                print("Raw data received:", message)

            except websockets.exceptions.ConnectionClosed as e:
                print(f"WebSocket connection closed: {e}")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

asyncio.run(listen_to_kismet())
