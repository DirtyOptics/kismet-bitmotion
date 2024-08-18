import asyncio
import websockets
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# WebSocket URL
websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'

async def kismet_listener():
    async with websockets.connect(websocket_url) as websocket:
        while True:
            try:
                # Receive a message from Kismet
                message = await websocket.recv()
                logging.info(f"Received message: {message}")

            except websockets.ConnectionClosed:
                logging.error("Connection closed, retrying...")
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

async def main():
    await kismet_listener()

# Run the WebSocket listener
asyncio.run(main())
