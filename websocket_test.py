import asyncio
import websockets
import json
import csv
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

# WebSocket URL
websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'

# CSV file setup
csv_filename = 'kismet_data.csv'
csv_columns = [
    'SSID', 'Encryption', 'Channel', 'NumClients', 
    'BSSID', 'Manufacturer', 'GPSLatitude', 'GPSLongitude', 
    'SignalStrength', 'FirstSeen', 'LastSeen', 'Timestamp'
]

# Ensure the CSV file is ready
with open(csv_filename, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

async def kismet_listener():
    async with websockets.connect(websocket_url) as websocket:
        while True:
            try:
                # Receive a message from Kismet
                message = await websocket.recv()
                logging.info(f"Received message: {message}")

                # Parse the JSON message
                data = json.loads(message)
                logging.info(f"Parsed JSON data: {data}")

                # Check if the message contains relevant data
                if 'fields' in data:
                    fields = data['fields']
                    logging.info(f"Fields found: {fields}")

                    # Extract relevant fields
                    ssid = fields.get('kismet.device.base.name', 'Unknown')
                    encryption = ', '.join(fields.get('kismet.device.base.crypt', []))
                    channel = fields.get('kismet.device.base.channel', 'Unknown')
                    num_clients = fields.get('kismet.device.base.clients', 0)
                    bssid = fields.get('kismet.device.base.macaddr', 'Unknown')
                    manufacturer = fields.get('kismet.device.base.manuf', 'Unknown')
                    gps_lat = fields.get('kismet.device.base.location', {}).get('kismet.common.location.lat', 'Unknown')
                    gps_lon = fields.get('kismet.device.base.location', {}).get('kismet.common.location.lon', 'Unknown')
                    signal_strength = fields.get('kismet.device.base.signal.last_signal', 'Unknown')
                    first_seen = fields.get('kismet.device.base.first_time', 'Unknown')
                    last_seen = fields.get('kismet.device.base.last_time', 'Unknown')
                    timestamp = datetime.now().isoformat()

                    # Prepare the row for the CSV file
                    row = {
                        'SSID': ssid,
                        'Encryption': encryption,
                        'Channel': channel,
                        'NumClients': num_clients,
                        'BSSID': bssid,
                        'Manufacturer': manufacturer,
                        'GPSLatitude': gps_lat,
                        'GPSLongitude': gps_lon,
                        'SignalStrength': signal_strength,
                        'FirstSeen': first_seen,
                        'LastSeen': last_seen,
                        'Timestamp': timestamp
                    }
                    logging.info(f"Writing row to CSV: {row}")

                    # Write the row to the CSV file
                    with open(csv_filename, 'a', newline='') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                        writer.writerow(row)

            except websockets.ConnectionClosed:
                logging.error("Connection closed, retrying...")
                break
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON, skipping this message.")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

async def main():
    while True:
        await kismet_listener()

# Run the WebSocket listener
asyncio.run(main())
