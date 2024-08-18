import csv
import json
import websockets
import asyncio

async def websocket_listener():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL
    
    with open('output.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Assuming these are the correct headings based on your needs
        writer.writerow(['SSID', 'Signal Strength', 'Last Seen', 'Lat', 'Lon'])

        async with websockets.connect(websocket_url) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                # Extract necessary fields (modify these keys based on your data)
                ssid = data.get('SSID')
                signal_strength = data.get('signal_strength')
                last_seen = data.get('last_seen')
                lat = data.get('lat')
                lon = data.get('lon')

                # Only write rows that have all the necessary data
                if ssid and signal_strength and last_seen and lat and lon:
                    writer.writerow([ssid, signal_strength, last_seen, lat, lon])
                    print(f"Data written to CSV: {[ssid, signal_strength, last_seen, lat, lon]}")

asyncio.run(websocket_listener())
