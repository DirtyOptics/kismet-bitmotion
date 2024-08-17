import asyncio
import websockets
import json
import requests
import yaml
import pytz
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Load configuration
with open("config.yaml", "r") as config_file:
    config = yaml.safe_load(config_file)

DATABASE_URL = config["database_url"]
timezone = config["timezone"]

# Database setup
Base = declarative_base()

class AccessPoint(Base):
    __tablename__ = 'access_points'
    id = Column(Integer, primary_key=True)
    ssid = Column(String)
    encryption = Column(String)
    channel = Column(Integer)
    clients = Column(Integer)
    bssid = Column(String)
    manufacturer = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    first_seen = Column(String)
    last_seen = Column(String)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Replace with your actual API token
api_token = config["api_token"]
view_id = "phydot11_accesspoints"  # The view ID for IEEE802.11 Access Points
kismet_rest_url = f"http://localhost:2501/devices/views/{view_id}/devices.json?KISMET={api_token}"

def log_access_point(ap_data):
    ssid = ap_data.get("kismet.device.base.name", "(hidden)")
    encryption = ap_data.get("kismet.device.base.crypt", "Unknown")
    channel = ap_data.get("kismet.device.base.channel", None)
    clients = ap_data.get("dot11.device.num_associated_clients", 0)
    bssid = ap_data.get("kismet.device.base.macaddr", "")
    manufacturer = ap_data.get("kismet.device.base.manuf", "Unknown")
    gps_data = ap_data.get("kismet.device.base.location", {})
    latitude = gps_data.get("kismet.common.location.lat", None)
    longitude = gps_data.get("kismet.common.location.lon", None)
    first_seen = datetime.fromtimestamp(ap_data.get("kismet.device.base.first_time", 0), pytz.timezone(timezone)).strftime("%H:%M:%S %d-%m-%Y")
    last_seen = datetime.fromtimestamp(ap_data.get("kismet.device.base.last_time", 0), pytz.timezone(timezone)).strftime("%H:%M:%S %d-%m-%Y")

    # Print the AP information
    print(f"SSID: {ssid}, Encryption: {encryption}, Channel: {channel}, Clients: {clients}, BSSID: {bssid}, Manufacturer: {manufacturer}, Latitude: {latitude}, Longitude: {longitude}, First Seen: {first_seen}, Last Seen: {last_seen}")

    ap = session.query(AccessPoint).filter_by(bssid=bssid).first()
    if ap:
        ap.ssid = ssid
        ap.encryption = encryption
        ap.channel = channel
        ap.clients = clients
        ap.manufacturer = manufacturer
        ap.latitude = latitude
        ap.longitude = longitude
        ap.last_seen = last_seen
    else:
        ap = AccessPoint(
            ssid=ssid,
            encryption=encryption,
            channel=channel,
            clients=clients,
            bssid=bssid,
            manufacturer=manufacturer,
            latitude=latitude,
            longitude=longitude,
            first_seen=first_seen,
            last_seen=last_seen
        )
        session.add(ap)

    session.commit()

async def capture_kismet_data():
    uri = f"ws://localhost:2501/eventbus/events.ws?KISMET={api_token}"
    
    async with websockets.connect(uri) as websocket:
        subscribe_message = {
            "SUBSCRIBE": "DOT11_ADVERTISED_SSID"
        }
        await websocket.send(json.dumps(subscribe_message))

        async for message in websocket:
            data = json.loads(message)

            # Print the raw message for debugging
            print("Raw WebSocket Message:", json.dumps(data, indent=2))

            if "DOT11_ADVERTISED_SSID" in data:
                base_device = data.get("DOT11_NEW_SSID_BASEDEV", {})
                ssid_record = data.get("DOT11_ADVERTISED_SSID", {})
                
                ap_data = {
                    "kismet.device.base.macaddr": base_device.get("kismet.device.base.macaddr", ""),
                    "kismet.device.base.name": ssid_record.get("ssid", ""),
                    "kismet.device.base.first_time": base_device.get("kismet.device.base.first_time", ""),
                    "kismet.device.base.last_time": base_device.get("kismet.device.base.last_time", ""),
                    "kismet.device.base.signal_dbm": base_device.get("kismet.device.base.signal_dbm", None),
                    "kismet.device.base.crypt": base_device.get("kismet.device.base.crypt", "Unknown"),
                    "kismet.device.base.channel": base_device.get("kismet.device.base.channel", None),
                    "dot11.device.num_associated_clients": base_device.get("dot11.device.num_associated_clients", 0),
                    "kismet.device.base.manuf": base_device.get("kismet.device.base.manuf", "Unknown"),
                    "kismet.device.base.location": base_device.get("kismet.device.base.location", {})
                }

                log_access_point(ap_data)

if __name__ == "__main__":
    asyncio.run(capture_kismet_data())
