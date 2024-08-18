import asyncio
import websockets
import json
import logging

# Enable debug logging and set up logging to a file
logging.basicConfig(level=logging.DEBUG, filename='websocket_output.txt', filemode='w', format='%(message)s')

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'

    async with websockets.connect(websocket_url) as websocket:
        subscribe_message = {
            "SUBSCRIBE": "DOT11_ADVERTISED_SSID"
        }
        await websocket.send(json.dumps(subscribe_message))

        async for message in websocket:
            logging.info(message)

asyncio.run(listen_to_kismet())
