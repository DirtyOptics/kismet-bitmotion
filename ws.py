import asyncio
import websockets
import json
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Database setup with an absolute path
DATABASE_URL = "sqlite:////home/db/kismet-bitmotion/kismet_data.db"
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

# WebSocket connection and data processing
async def capture_kismet_data():
    uri = "ws://localhost:2501/"
    headers = {
        "Authorization": f"Token {api_token}"
    }
    async with websockets.connect(uri, extra_headers=headers) as websocket:
        await websocket.send(json.dumps({
            "Kismet": {
                "subscribe": ["*"]  # Subscribe to all data
            }
        }))

        async for message in websocket:
            data = json.loads(message)
            if "kismet.device.base.name" in data:
                bssid = data.get("kismet.device.base.macaddr", "")
                ssid = data.get("kismet.device.base.name", "")
                last_seen = data.get("kismet.device.base.last_time", "")
                signal_dbm = data.get("kismet.device.base.signal_dbm", None)

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

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(capture_kismet_data())
