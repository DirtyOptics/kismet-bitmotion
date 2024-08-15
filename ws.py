import asyncio
import websockets
import json
import requests
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Database setup with an absolute path
DATABASE_URL = "sqlite:////home/tb/kismet-bitmotion/kismet_data.db"
Base = declarative_base()

class AccessPoint(Base):
    __tablename__ = 'access_points'
    id = Column(Integer, primary_key=True)
    bssid = Column(String, unique=True)
    ssid = Column(String)
    last_seen = Column(String)
    signal_dbm = Column(Float)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Replace with your actual API token
api_token = "your_actual_api_token_here"
kismet_rest_url = "http://localhost:2501/devices/views/all_devices.json"  # Kismet REST API URL

# Function to process and log APs
def log_access_point(ap_data):
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    ssid = ap_data.get("kismet.device.base.name", "")
    last_seen = ap_data.get("kismet.device.base.last_time", "")
    signal_dbm = ap_data.get("kismet.device.base.signal_dbm", None)

    # Print to console
    print(f"Found AP: BSSID={bssid}, SSID={ssid}, Last Seen={last_seen}, Signal={signal_dbm} dBm")

    ap = session.query(AccessPoint).filter_by(bssid=bssid).first()
    if ap:
        ap.last_seen = last_seen
        ap.signal_dbm = signal_dbm
    else:
        ap = AccessPoint(bssid=bssid, ssid=ssid, last_seen=last_seen, signal_dbm=signal_dbm)
        session.add(ap)

    session.commit()

# Function to perform an initial sweep of existing APs
def sweep_existing_aps():
    headers = {"Authorization": f"Token {api_token}"}
    response = requests.get(kismet_rest_url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        for device in devices:
            if "kismet.device.base.type" in device and device["kismet.device.base.type"] == "Wi-Fi AP":
                log_access_point(device)
    else:
        print(f"Failed to fetch existing APs: {response.status_code}")

# WebSocket connection and data processing
async def capture_kismet_data():
    # Perform an initial sweep to log existing APs
    sweep_existing_aps()

    # Continue to capture new APs in real-time via WebSocket
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
                    "kismet.device.base.signal_dbm": base_device.get("kismet.device.base.signal_dbm", None)
                }

                log_access_point(ap_data)

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(capture_kismet_data())
