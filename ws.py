import asyncio
import websockets
import json
import requests
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Load the API key from the config.json file
with open('config.json') as config_file:
    config = json.load(config_file)
    api_token = config.get("api_token")

# Database setup with an absolute path
DATABASE_URL = "sqlite:///kismet_data.db"
Base = declarative_base()

class AccessPoint(Base):
    __tablename__ = 'access_points'
    id = Column(Integer, primary_key=True)
    bssid = Column(String, unique=True)
    ssid = Column(String, nullable=True)
    last_seen = Column(String)
    signal_dbm = Column(Float, nullable=True)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

view_id = "phydot11_accesspoints"  # The view ID for IEEE802.11 Access Points
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def log_access_point(ap_data):
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    ssid = ap_data.get("kismet.device.base.name", "(unknown)")
    
    # Convert the last seen time to a format with time first, then date
    last_seen_timestamp = ap_data.get("kismet.device.base.last_time", "")
    last_seen = datetime.utcfromtimestamp(last_seen_timestamp).strftime('%H:%M:%S %Y-%m-%d')
    
    signal_dbm = ap_data.get("kismet.device.base.signal", {}).get("kismet.common.signal.last_signal", None)

    print(f"Found AP: BSSID={bssid}, SSID={ssid}, Last Seen={last_seen}, Signal={signal_dbm} dBm")

    ap = session.query(AccessPoint).filter_by(bssid=bssid).first()
    if ap:
        ap.last_seen = last_seen
        ap.signal_dbm = signal_dbm
    else:
        ap = AccessPoint(bssid=bssid, ssid=ssid, last_seen=last_seen, signal_dbm=signal_dbm)
        session.add(ap)

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
    try:
        sweep_existing_aps()

        uri = f"ws://localhost:2501/eventbus/events.ws?KISMET={api_token}"
        
        async with websockets.connect(uri) as websocket:
            subscribe_message = {
                "SUBSCRIBE": "DOT11_ADVERTISED_SSID"
            }
            await websocket.send(json.dumps(subscribe_message))

            async for message in websocket:
                # Parse the JSON message
                data = json.loads(message)
                
                if "DOT11_ADVERTISED_SSID" in data and "DOT11_NEW_SSID_BASEDEV" in data:
                    base_device = data.get("DOT11_NEW_SSID_BASEDEV", {})

                    ap_data = {
                        "kismet.device.base.macaddr": base_device.get("kismet.device.base.macaddr", ""),
                        "kismet.device.base.name": base_device.get("kismet.device.base.name", "(unknown)"),
                        "kismet.device.base.last_time": base_device.get("kismet.device.base.last_time", ""),
                        "kismet.device.base.signal": base_device.get("kismet.device.base.signal", {})
                    }

                    log_access_point(ap_data)
    except asyncio.CancelledError:
        print("Task was cancelled.")
    except KeyboardInterrupt:
        print("Script interrupted by user. Exiting...")

async def main():
    try:
        await capture_kismet_data()
    except KeyboardInterrupt:
        print("Main function interrupted. Exiting...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program terminated.")
