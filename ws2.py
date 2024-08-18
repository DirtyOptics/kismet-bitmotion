import asyncio
import requests
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

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

engine = create_engine('sqlite:////home/db/kismet-bitmotion/kismet_data.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

api_token = "<your_api_token>"
view_id = "phydot11_accesspoints"
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def convert_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S %d-%m-%Y")

def log_access_point(ap_data):
    ssid = ap_data.get("kismet.device.base.name", "")
    encryption_type = ap_data.get("kismet.device.base.crypt", "")
    channel = ap_data.get("kismet.device.base.channel", "")
    num_clients = len(ap_data.get("dot11.device.associated_client_map", {}))
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    manufacturer = ap_data.get("kismet.device.base.manuf", "")
    
    location_data = ap_data.get("kismet.device.base.location", {}).get("kismet.common.location.avg_loc", {})
    gps_latitude = location_data.get("kismet.common.location.geopoint", [None, None])[1]
    gps_longitude = location_data.get("kismet.common.location.geopoint", [None, None])[0]

    first_seen = convert_time(ap_data.get("kismet.device.base.first_time", 0))
    last_seen = convert_time(ap_data.get("kismet.device.base.last_time", 0))

    signal_dbm = ap_data.get("kismet.device.base.signal", {}).get("kismet.common.signal.last_signal", None)
    observation_timestamp = datetime.now().strftime("%H:%M:%S %d-%m-%Y")

    ap_observation = APObservation(
        ssid=ssid,
        encryption_type=encryption_type,
        channel=channel,
        num_clients=num_clients,
        bssid=bssid,
        manufacturer=manufacturer,
        gps_latitude=gps_latitude,
        gps_longitude=gps_longitude,
        signal_dbm=signal_dbm,
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

async def periodic_scan():
    while True:
        sweep_existing_aps()
        await asyncio.sleep(5)  # Adjust the polling interval as needed

async def main():
    sweep_existing_aps()
    await periodic_scan()

if __name__ == "__main__":
    asyncio.run(main())
