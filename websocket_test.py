import csv
import asyncio
import websockets
import json

# Define CSV file name and headers
csv_file = 'kismet_ap_data.csv'
headers = ['SSID', 'Encryption Type', 'Channel', 'Num Clients', 'BSSID', 'Manufacturer', 'GPS Latitude', 'GPS Longitude', 'Signal Strength', 'First Seen', 'Last Seen', 'Timestamp']

# Open CSV file and write headers
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(headers)

async def process_ap_data(ap_data):
    # Parse the JSON data from the WebSocket
    ap = json.loads(ap_data)

    # Extract the required fields
    ssid = ap.get('kismet.device.base.name', 'Unknown SSID')
    encryption_type = ap.get('kismet.device.base.crypt', 'Unknown')
    channel = ap.get('kismet.device.base.channel', 'Unknown')
    num_clients = ap.get('kismet.device.base.clients', 0)
    bssid = ap.get('kismet.device.base.macaddr', 'Unknown BSSID')
    manufacturer = ap.get('kismet.device.base.manuf', 'Unknown Manufacturer')
    gps_lat = ap.get('kismet.device.base.location', {}).get('kismet.common.location.lat', 'N/A')
    gps_lon = ap.get('kismet.device.base.location', {}).get('kismet.common.location.lon', 'N/A')
    signal_strength = ap.get('kismet.device.base.signal', {}).get('kismet.common.signal.last_signal', 'N/A')
    first_seen = ap.get('kismet.device.base.first_time', 'N/A')
    last_seen = ap.get('kismet.device.base.last_time', 'N/A')
    timestamp = ap.get('kismet.device.base.last_time', 'N/A')

    # Print the data for debugging
    print(f"SSID: {ssid}, BSSID: {bssid}, Signal: {signal_strength} dBm")

    # Write AP data to CSV
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            ssid, encryption_type, channel, num_clients,
            bssid, manufacturer, gps_lat, gps_lon,
            signal_strength, first_seen, last_seen, timestamp
        ])

async def connect_to_websocket():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your WebSocket URL
    async with websockets.connect(websocket_url) as websocket:
        while True:
            ap_data = await websocket.recv()
            await process_ap_data(ap_data)

# Run the WebSocket connection
asyncio.get_event_loop().run_until_complete(connect_to_websocket())
