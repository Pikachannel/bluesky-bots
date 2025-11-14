# -------- Imports --------
from .bsky.jetstream import Websocket
from .bsky.client import login
from .bsky.followers import refresh_followers
from .bsky.worker import worker
from .bsky.dm_worker import check_dms
from .utils.json_worker import json_worker
import asyncio
import os
import json
from dotenv import load_dotenv

# -------- Variables --------
load_dotenv()

# -- Account info
HANDLE = os.getenv("HANDLE")
PASSWORD = os.getenv("PASSWORD")
ACCOUNT_DID = os.getenv("ACCOUNT_DID")

# -- File paths
MESSAGES_JSON_PATH = "bots/data/messages.json"
USER_DATA_PATH = "bots/data/user_data.json"

# -- Setup followers
followers_set = set()

# -------- Load json files --------
with open(MESSAGES_JSON_PATH, "r", encoding="utf-8") as f:
    messages = json.load(f)["messages"]["en"]

with open(USER_DATA_PATH, "r", encoding="utf-8") as f:
    user_data = json.load(f)

# ------ Main Function --------
async def main():
    # -- Setup client connection
    client, profile = await login(HANDLE, PASSWORD)
    if not client:
        input("[Run] Press enter to exit...")
        return

    # -- Create queues
    queue = asyncio.Queue()
    json_queue = asyncio.Queue()

    # -- Start all functions as background tasks
    asyncio.create_task(refresh_followers(client, followers_set, ACCOUNT_DID))
    asyncio.create_task(check_dms(client, json_queue, ACCOUNT_DID))
    for _ in range(3):
        asyncio.create_task(worker(client, queue, followers_set, ACCOUNT_DID, messages, user_data))
    
    asyncio.create_task(json_worker(USER_DATA_PATH, json_queue, user_data))

    # -- Setup websocket connection to the bsky jetstream
    ws = Websocket()
    await ws.connect(queue)
