import asyncio
import websockets
import json

# To track updates to a particular AP
tracked_aps = {}

async def test_websocket():
    uri = "ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816"
    async with websockets.connect(uri) as websocket:
        # Send subscription message
        subscribe_message = {"SUBSCRIBE": "DOT11_ADVERTISED_SSID"}
        await websocket.send(json.dumps(subscribe_message))

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                # Look for DOT11_ADVERTISED_SSID data
                if "DOT11_ADVERTISED_SSID" in data:
                    ssid_data = data["DOT11_ADVERTISED_SSID"]
                    bssid = ssid_data.get("dot11.advertisedssid.bssid", None)
                    ssid = ssid_data.get("dot11.advertisedssid.ssid", "(hidden)")
                    signal = ssid_data.get("dot11.advertisedssid.signal_dbm", None)
                    
                    if bssid:
                        # Check if this AP has been seen before
                        if bssid in tracked_aps:
                            previous_signal = tracked_aps[bssid]['signal']
                            # If the signal has changed, print the update
                            if signal != previous_signal:
                                print(f"AP {bssid} ({ssid}) signal changed from {previous_signal} to {signal}")
                                tracked_aps[bssid]['signal'] = signal
                        else:
                            # First time seeing this AP
                            tracked_aps[bssid] = {'ssid': ssid, 'signal': signal}
                            print(f"First seen AP {bssid} ({ssid}) with signal {signal}")
                    
            except websockets.exceptions.ConnectionClosed:
                print("Connection closed")
                break

asyncio.run(test_websocket())
