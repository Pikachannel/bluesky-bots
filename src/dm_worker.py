# -------- Imports --------
from atproto import Client, models
from typing import Any
import asyncio
from datetime import datetime, timezone, timedelta

# -------- DmWorker Class --------
class DmWorker:
    def __init__(self, client: Client, command_manager: Any, json_queue: asyncio.Queue, account_did: str, check_interval: int = 300) -> None:
        self.client = client
        self.command_manager = command_manager
        self.json_queue = json_queue
        self.account_did = account_did
        self.check_interval = check_interval
    
    # -------------
    # -- Start the DM Worker
    async def start(self) -> None:
        print("[DM Worker] Starting DM worker")
        while True:
            try:
                await self.check_dms()
            except Exception as e:
                print(f"[DMWorker] Error: {e}")
            await asyncio.sleep(self.check_interval)
    
    # -------------
    # -- Check DMs sent to the bot
    async def check_dms(self) -> None:
        # -- Get the messages sent to the bot
        dm_client = self.client.with_bsky_chat_proxy()
        dm = dm_client.chat.bsky.convo

        convo_list = dm.list_convos()

        # -- Loop through all users dms
        for convo in convo_list.convos:
            # -- Extract message information
            user_did = convo.last_message.sender.did
            last_message = convo.last_message.text
            sent_at = convo.last_message.sent_at
            sent_at = datetime.fromisoformat(sent_at.replace("Z", "+00:00"))

            # -- Check if the message was sent in the last 5 minutes
            now = datetime.now(timezone.utc)
            if now - sent_at >= timedelta(minutes=5):
                break
            if user_did == self.account_did:
                continue

            # -- Split the message into a prefix and param 
            parts = last_message.split(maxsplit=1)
            command = parts[0].lower()
            param = parts[1] if len(parts) > 1 else None

            # Map to CommandManager methods
            msg_to_send = None
            facet = None
            if command == "!nickname":
                _, msg_to_send = await self.command_manager.update_nickname(user_did, param)
            elif command == "!chance":
                _, msg_to_send = await self.command_manager.chance(user_did, param)
            elif command == "!interval":
                _, msg_to_send = await self.command_manager.interval_time(user_did, param)
            elif command == "!delete":
                _, msg_to_send = await self.command_manager.delete_settings(user_did)
            elif command == "!settings":
                _, msg_to_send = await self.command_manager.view_settings(user_did)
            elif command == "!help":
                _, msg_to_send, facet = await self.command_manager.help()
            else:
                continue
            
            if msg_to_send:
                if not facet:
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=msg_to_send
                            ),
                        )
                    )
                else:
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=msg_to_send,
                                facets=[facet]
                            ),
                        )
                    )
