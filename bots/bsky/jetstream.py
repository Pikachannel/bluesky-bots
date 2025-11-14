# -------- Imports --------
import asyncio
import websockets
import json
from websockets.exceptions import ConnectionClosedError

# -------- Websocket Class --------
class Websocket():
    # -- Setup websocket variables
    def __init__(self, endpoint: str = None):
        self.endpoint = "wss://jetstream1.us-east.bsky.network/subscribe"
        self.reconnect = 1
        self.connect = False

    # -- Connect function
    async def connect(self, queue):
        # Try to connect infinitely 
        self.connect = True
        while self.connected:
            try:
                # Connect to the bsky jetstream
                async with websockets.connect(self.endpoint) as ws:
                    print(f"[Websocket] Connected to {self.endpoint}")
                    async for raw_message in ws: # Get new messages
                        try:
                            message = json.loads(raw_message)

                            # Add them to a queue for the worker function
                            await queue.put(message)
                        except json.JSONDecodeError:
                            continue
            except ConnectionClosedError as e:
                print(f"[Websocket] Connection lost, {e} reconnecting shortly...")
                await asyncio.sleep(self.reconnect) # Wait to connect upon disconnection 
            except Exception as e:
                print(f"[Websocket] An error has occured, {e} reconnecting shortly...")
                await asyncio.sleep(self.reconnect) # Wait to reconnect upon error

