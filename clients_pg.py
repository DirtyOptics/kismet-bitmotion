import asyncio
import requests
import yaml
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import time

# Load configuration from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

api_token = config.get("api_token")
timezone_setting = config.get("timezone", "local")
database_url = config.get("database_url_clients")

# Database setup
Base = declarative_base()

class ClientObservation(Base):
    __tablename__ = 'client_observations'
    id = Column(Integer, primary_key=True)
    client_mac = Column(String)
    signal_dbm = Column(Float, nullable=True)
    channel = Column(String)
    manufacturer = Column(String)
    first_seen = Column(String)
    last_seen = Column(String)
    bssid = Column(String)

# Create the engine using the PostgreSQL URL from the config
engine = create_engine(database_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

view_id = "phydot11_clients"  # The view ID for IEEE802.11 clients
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def convert_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    if timezone_setting == "UTC":
        dt = dt.replace(tzinfo=timezone.utc)
    elif timezone_setting == "local":
        dt = dt.astimezone()
    return dt.strftime("%H:%M:%S %d-%m-%Y")

def log_client(client_data):
    client_mac = client_data.get("kismet.device.base.macaddr", "")
    signal_dbm = client_data.get("kismet.device.base.signal", {}).get("kismet.common.signal.last_signal", None)
    channel = client_data.get("kismet.device.base.channel", "")
    manufacturer = client_data.get("kismet.device.base.manuf", "")
    first_seen = convert_time(client_data.get("kismet.device.base.first_time", 0))
    last_seen = convert_time(client_data.get("kismet.device.base.last_time", 0))
    bssid = client_data.get("dot11.device.client_map", {}).get("kismet.device.base.macaddr", "")
    
    print(f"Client MAC: {client_mac}, Signal: {signal_dbm}, Channel: {channel}, Manufacturer: {manufacturer}, "
          f"First Seen: {first_seen}, Last Seen: {last_seen}, BSSID: {bssid}")

    # Check if this client already exists in the database
    last_observation = session.query(ClientObservation).filter_by(client_mac=client_mac).order_by(ClientObservation.timestamp.desc()).first()

    # Only add to the database if something has changed
    if (not last_observation or
        last_observation.signal_dbm != signal_dbm or
        last_observation.channel != channel or
        last_observation.last_seen != last_seen):
        
        client_observation = ClientObservation(
            client_mac=client_mac,
            signal_dbm=signal_dbm,
            channel=channel,
            manufacturer=manufacturer,
            first_seen=first_seen,
            last_seen=last_seen,
            bssid=bssid
        )
        session.add(client_observation)
        session.commit()

def sweep_existing_clients():
    response = requests.get(kismet_rest_url)
    if response.status_code == 200:
        clients = response.json()
        for client in clients:
            log_client(client)
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

