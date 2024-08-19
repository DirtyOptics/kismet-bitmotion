import asyncio
import requests
import yaml
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Load configuration from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

api_token = config.get("api_token")
timezone_setting = config.get("timezone", "local")
database_url_clients = config.get("database_url_clients")  # Correct reference here

# Database setup
Base = declarative_base()

class ClientObservation(Base):
    __tablename__ = 'client_observations'
    id = Column(Integer, primary_key=True)
    client_mac = Column(String)
    signal_dbm = Column(Float, nullable=True)
    channel = Column(String)
    bssid = Column(String)  # The BSSID the client is associated with
    manufacturer = Column(String)
    first_seen = Column(String)
    last_seen = Column(String)
    timestamp = Column(String)

# Create the engine using the PostgreSQL URL from the config
engine = create_engine(database_url_clients)  # Correct reference here
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

view_id = "phy-IEEE802.11"  # This is the view that contains both AP and client data
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def convert_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    if timezone_setting == "UTC":
        dt = dt.replace(tzinfo=timezone.utc)
    elif timezone_setting == "local":
        dt = dt.astimezone()
    return dt.strftime("%H:%M:%S %d-%m-%Y")

def log_client_data(client_data, bssid):
    for client_mac, client_info in client_data.items():
        if isinstance(client_info, dict):  # Ensure client_info is a dictionary
            signal_dbm = client_info.get("kismet.common.signal.last_signal", None)
            channel = client_info.get("kismet.device.base.channel", None)
            manufacturer = client_info.get("kismet.device.base.manuf", "")
            first_seen = convert_time(client_info.get("kismet.device.base.first_time", 0))
            last_seen = convert_time(client_info.get("kismet.device.base.last_time", 0))
            observation_timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

            print(f"Client MAC: {client_mac}, BSSID: {bssid}, Signal: {signal_dbm}, Channel: {channel}, "
                  f"First Seen: {first_seen}, Last Seen: {last_seen}, Timestamp: {observation_timestamp}")
            
            # Check if this client already exists in the database
            last_observation = session.query(ClientObservation).filter_by(client_mac=client_mac, bssid=bssid).order_by(ClientObservation.timestamp.desc()).first()

            # Only add to the database if something has changed
            if (not last_observation or
                last_observation.signal_dbm != signal_dbm or
                last_observation.last_seen != last_seen):
                
                client_observation = ClientObservation(
                    client_mac=client_mac,
                    signal_dbm=signal_dbm,
                    channel=channel,
                    bssid=bssid,
                    manufacturer=manufacturer,
                    first_seen=first_seen,
                    last_seen=last_seen,
                    timestamp=observation_timestamp
                )
                session.add(client_observation)
                session.commit()
        else:
            print(f"Unexpected data format for client {client_mac}: {client_info}")

def process_device(device):
    bssid = device.get("kismet.device.base.macaddr", "")
    if "dot11.device.associated_client_map" in device["dot11.device"]:
        log_client_data(device["dot11.device"]["dot11.device.associated_client_map"], bssid)
    if "dot11.device.client_map" in device["dot11.device"]:
        log_client_data(device["dot11.device"]["dot11.device.client_map"], bssid)

def sweep_existing_clients():
    response = requests.get(kismet_rest_url)
    if response.status_code == 200:
        devices = response.json()
        print(f"API response status: {response.status_code}")
        print(f"Number of devices returned: {len(devices)}")
        for device in devices:
            process_device(device)
    else:
        print(f"Failed to fetch existing clients: {response.status_code}")

async def periodic_update(interval=5):
    while True:
        sweep_existing_clients()
        await asyncio.sleep(interval)

async def main():
    try:
        await periodic_update(interval=5)
    except asyncio.CancelledError:
        print("Task was cancelled.")
    except KeyboardInterrupt:
        print("Script interrupted by user.")

if __name__ == "__main__":
    asyncio.run(main())
