import asyncio
import websockets

async def listen_to_kismet():
    websocket_url = 'ws://localhost:2501/eventbus/events.ws?KISMET=D470660EF5CB6466F4B8143B204F8816'  # Replace with your actual API key

    async with websockets.connect(websocket_url) as websocket:
        while True:
            try:
                message = await websocket.recv()
                print(message)  # Print the raw message received from the WebSocket
            except websockets.ConnectionClosed:
                print("Connection closed")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                break

if __name__ == "__main__":
    asyncio.run(listen_to_kismet())
