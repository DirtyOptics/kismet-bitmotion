import asyncio
import websockets
import logging
import json

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL

    async with websockets.connect(websocket_url) as websocket:
        # Subscribe to all events
        subscription_message = '{"Kismet": {"subscribe": ["*"]}}'
        await websocket.send(subscription_message)
        print("Subscribed to all events")

        try:
            while True:
                message = await websocket.recv()
                print("Raw message received:", message)
                data = json.loads(message)

                # Now try to filter for DOT11_ADVERTISED_SSID
                if "DOT11_ADVERTISED_SSID" in data:
                    base_device = data.get("DOT11_NEW_SSID_BASEDEV", {})
                    ssid_record = data.get("DOT11_ADVERTISED_SSID", {})

                    print(f"SSID: {ssid_record.get('ssid', 'N/A')}")
                    print(f"Base Device: {base_device}")
                    print(f"Record: {ssid_record}")

        except websockets.exceptions.ConnectionClosed as e:
            print(f"WebSocket connection closed: {e}")

asyncio.run(listen_to_kismet())
