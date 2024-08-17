import asyncio
import websockets
import json
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

# Database setup with an absolute path
DATABASE_URL = "sqlite:///kismet-bitmotion/kismet_data.db"
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
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    ssid = ap_data.get("kismet.device.base.name", "")
    last_seen = convert_time(ap_data.get("kismet.device.base.last_time", 0))
    signal_dbm = ap_data.get("kismet.device.base.signal", {}).get("kismet.common.signal.last_signal", None)

    # Check if SSID is hidden or matches the BSSID
    if not ssid or ssid == bssid:
        ssid = "(hidden)"

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
                    "kismet.device.base.signal": base_device.get("kismet.device.base.signal", None)
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
