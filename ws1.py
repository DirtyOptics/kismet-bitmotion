import asyncio
import websockets
import json
import requests
import yaml
from datetime import datetime, timezone
import pytz
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Load configuration from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

api_token = config.get("api_token")
timezone_setting = config.get("timezone", "local")
database_url = config.get("database_url", "sqlite:///kismet-bitmotion/kismet_data.db")

# Database setup
Base = declarative_base()

class APObservation(Base):
    __tablename__ = 'ap_observations'
    id = Column(Integer, primary_key=True)
    ssid = Column(String)
    encryption_type = Column(String)
    channel = Column(String)
    num_clients = Column(Integer)
    bssid = Column(String)
    manufacturer = Column(String)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    signal_dbm = Column(Float, nullable=True)
    first_seen = Column(String)
    last_seen = Column(String)
    timestamp = Column(String)

engine = create_engine(database_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

view_id = "phydot11_accesspoints"  # The view ID for IEEE802.11 Access Points
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def convert_time(timestamp):
    # Convert timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp)

    # Apply timezone based on configuration
    if timezone_setting == "UTC":
        dt = dt.replace(tzinfo=timezone.utc)
    elif timezone_setting == "local":
        dt = dt.astimezone()  # Convert to local timezone

    # Format time as "Time Date"
    return dt.strftime("%H:%M:%S %d-%m-%Y")

def log_access_point(ap_data):
    ssid = ap_data.get("kismet.device.base.name", "")
    encryption_type = ap_data.get("kismet.device.base.crypt", "")
    channel = ap_data.get("kismet.device.base.channel", "")
    num_clients = len(ap_data.get("dot11.device.associated_client_map", {}))
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    manufacturer = ap_data.get("kismet.device.base.manuf", "")
    
    # Extract GPS data
    location_data = ap_data.get("kismet.device.base.location", {}).get("kismet.common.location.avg_loc", {})
    gps_latitude = location_data.get("kismet.common.location.geopoint", [None, None])[1]
    gps_longitude = location_data.get("kismet.common.location.geopoint", [None, None])[0]

    first_seen = convert_time(ap_data.get("kismet.device.base.first_time", 0))
    last_seen = convert_time(ap_data.get("kismet.device.base.last_time", 0))

    # Generate a timestamp for when this observation was made
    observation_timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

    # Check if SSID is hidden or matches the BSSID
    if not ssid or ssid == bssid:
        ssid = "(hidden)"

    print(f"SSID: {ssid}, Encryption: {encryption_type}, Channel: {channel}, Clients: {num_clients}, "
          f"BSSID: {bssid}, Manufacturer: {manufacturer}, Latitude: {gps_latitude}, Longitude: {gps_longitude}, "
          f"First Seen: {first_seen}, Last Seen: {last_seen}, Timestamp: {observation_timestamp}")

    # Insert the observation into the database
    ap_observation = APObservation(
        ssid=ssid,
        encryption_type=encryption_type,
        channel=channel,
        num_clients=num_clients,
        bssid=bssid,
        manufacturer=manufacturer,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        signal_dbm=ap_data.get("kismet.device.base.signal_dbm", None),
        first_seen=first_seen,
        last_seen=last_seen,
        timestamp=observation_timestamp
    )
    session.add(ap_observation)
    session.commit()

def sweep_existing_aps():
    response = requests.get(kismet_rest_url)
    if response.status_code == 200:
        devices = response.json()
        for device in devices:
            log_access_point(device)
    else:
        print(f"Failed to fetch existing APs: {response.status_code}")

async def capture_kismet_data():
    sweep_existing_aps()

    uri = f"ws://localhost:2501/eventbus/events.ws?KISMET={api_token}"
    
    async with websockets.connect(uri) as websocket:
        subscribe_message = {
            "SUBSCRIBE": "DOT11_ADVERTISED_SSID"
        }
        await websocket.send(json.dumps(subscribe_message))

        async for message in websocket:
            data = json.loads(message)
            if "DOT11_ADVERTISED_SSID" in data:
                base_device = data.get("DOT11_NEW_SSID_BASEDEV", {})
                ssid_record = data.get("DOT11_ADVERTISED_SSID", {})
                
                ap_data = {
                    "kismet.device.base.macaddr": base_device.get("kismet.device.base.macaddr", ""),
                    "kismet.device.base.name": ssid_record.get("ssid", ""),
                    "kismet.device.base.last_time": base_device.get("kismet.device.base.last_time", ""),
                    "kismet.device.base.first_time": base_device.get("kismet.device.base.first_time", ""),
                    "kismet.device.base.crypt": base_device.get("kismet.device.base.crypt", ""),
                    "kismet.device.base.channel": base_device.get("kismet.device.base.channel", ""),
                    "kismet.device.base.manuf": base_device.get("kismet.device.base.manuf", ""),
                    "kismet.device.base.location": base_device.get("kismet.device.base.location", {}),
                    "dot11.device.associated_client_map": base_device.get("dot11.device.associated_client_map", {})
                }

                log_access_point(ap_data)

async def main():
    try:
        await capture_kismet_data()
    except asyncio.CancelledError:
        print("Task was cancelled.")
    except KeyboardInterrupt:
        print("Script interrupted by user.")

if __name__ == "__main__":
    asyncio.run(main())
