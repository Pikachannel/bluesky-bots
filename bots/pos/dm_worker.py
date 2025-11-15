# -------- Imports --------
from atproto import Client, IdResolver, models
from datetime import datetime, timedelta, timezone
import asyncio

# -------- Check DMs Function --------
async def check_dms(client, json_queue, account_did):
    # -- Start function
    print(f"[DM Worker] Worker starting")
    while True:
        try:
            # -- Get the messages sent to the bot
            dm_client = client.with_bsky_chat_proxy()
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
                if user_did == account_did:
                    continue

                # -- Split the message into a prefix and param 
                parts = last_message.split(maxsplit=1)
                if parts[0] == "!nickname":
                    nickname = parts[1] if len(parts) > 1 else "!pop_entry" # Send a pop instruction if no nickname was provided

                    # -- Add the nickname to the json queue
                    if nickname:
                        user_data = {
                            "type": "update",
                            "user_did": user_did,
                            "nickname": nickname.strip()
                        }
                        
                        await json_queue.put(user_data)

                        # -- Send a confirmation message
                        if nickname != "!pop_entry":
                            dm_text = f"Your nickname has been successfully changed to '{nickname.strip()}'!\nYou can change it at anytime by sending the same command."
                        else:
                            dm_text = "Your nickname has been sucessfully reset to your display name."

                        dm.send_message(
                            models.ChatBskyConvoSendMessage.Data(
                                convo_id=convo.id,
                                message=models.ChatBskyConvoDefs.MessageInput(
                                    text=dm_text
                                ),
                            )
                        )
                    
                
                # -- Handle deleting a user's data
                elif parts[0] == "!delete":
                    delete_data = {
                        "type": "delete",
                        "user_did": user_did
                    }

                    await json_queue.put(delete_data)

                    # -- Send a confirmation message
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=f"Your data was successfully deleted from the bots storage."
                            ),
                        )
                    )


        except Exception as e:
            print(f"[DM Worker] Error: {e}")
            continue
        finally:
            await asyncio.sleep(300) # -- Check dms every 5 minutes
                
