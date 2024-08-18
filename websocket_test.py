import asyncio
import websockets
import logging
import json

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        # Subscribe to dot11.advertised_ssid events
        subscription_message = '{"Kismet": {"subscribe": ["dot11.advertised_ssid"]}}'
        await websocket.send(subscription_message)
        print("Subscribed to dot11.advertised_ssid events")

        try:
            while True:
                message = await websocket.recv()
                print("Raw message received:", message)
                data = json.loads(message)

                if "dot11.advertised_ssid" in data:
                    ssid_record = data.get("dot11.advertised_ssid", {})
                    print(f"SSID: {ssid_record.get('ssid', 'N/A')}")
                    print(f"Record: {ssid_record}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")

asyncio.run(listen_to_kismet())
