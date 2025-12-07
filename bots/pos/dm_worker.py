#-- ------ Imports --------
from atproto import Client, IdResolver, models
from datetime import datetime, timedelta, timezone
import asyncio
import json
from typing import Any

# -------- Check DMs Function --------
async def check_dms(client: Client, json_queue: asyncio.Queue[dict], account_did: str, user_data: dict) -> None:    
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
                        nickname_data = {
                            "type": "update",
                            "user_did": user_did,
                            "nickname": nickname.strip()[:20]
                        }
                        
                        await json_queue.put(nickname_data)

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
                                 
                # -- Add the chance value to the json queue
                elif parts[0] == "!chance":
                    # -- Check if the user is resetting or has provided a number
                    chance_value = parts[1] if len(parts) > 1 else "!pop_entry"
                    if chance_value != "!pop_entry":
                        try:
                            chance_value = float(chance_value)
                            is_digit = True
                        except:
                            is_digit = False

                    if not is_digit and chance_value != "!pop_entry":
                        error_message(dm, convo)
                        continue
                    if chance_value != "!pop_entry":
                        chance_value = float(chance_value)
                        if chance_value < 0 or chance_value > 100: # Make sure the number provided is with the valid range
                            error_message(dm, convo)
                            continue

                    # -- Add the chance value to the json queue
                    chance_data = {
                        "type": "update",
                        "user_did": user_did,
                        "chance": float(str(chance_value)[:5]) if chance_value != "!pop_entry" else "!pop_entry" # Truncate the value to 2 decimal places
                    }
                    
                    await json_queue.put(chance_data)

                    if chance_value != "!pop_entry":
                        dm_text = f"The chance of a reply under your posts is now '{chance_value}%'!\nYou can change this at anytime by sending the same command."
                    else:
                        dm_text = "The chance of a reply under your posts has been reset to 100%."

                    # -- Send a confirmation message
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=dm_text
                            ),
                        )
                    )
                
                # -- Add the interval value to the json queue
                elif parts[0] == "!interval":
                    # -- Check if the user is resetting or has provided a number
                    interval_value = parts[1] if len(parts) > 1 else "!pop_entry"
                    if interval_value != "!pop_entry":
                        try:
                            interval_value = float(interval_value)
                            is_digit = True
                        except:
                            is_digit = True

                    if not is_digit and interval_value != "!pop_entry":
                        error_message(dm, convo)
                        continue
                    if interval_value != "!pop_entry":
                        interval_value = float(interval_value)
                        if interval_value < 0 or interval_value > 3600:
                            error_message(dm, convo)
                            continue
                    
                    # -- Add the interval value to the json queue
                    interval_data = {
                        "type": "update",
                        "user_did": user_did,
                        "interval": float(str(interval_value)[:5]) if interval_value != "!pop_entry" else "!pop_entry"
                    }

                    await json_queue.put(interval_data)

                    if interval_value != "!pop_entry":
                        dm_text = f"The interval between replies under your posts is now '{interval_value}' seconds!\nYou can change this at anytime by sending the same command."
                    else:
                        dm_text = "The interval between replies under your posts has been reset to have no interval."
                    
                    # -- Send a confirmation message
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=dm_text
                            ),
                        )
                    )
                   
                # -- Send the user's settings
                elif parts[0] == "!settings":
                    load_settings = user_data.get(user_did, None)


                    if load_settings:
                        settings = "\n".join(f"{key.capitalize()}: {value}" for key, value in load_settings.items())

                        dm_text = f"Your settings are:\n{settings}"
                    else:
                        dm_text = "You do not have any settings configured, you can change your settings by using commands"
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

                # -- Send the help message
                elif parts[0] == "!help":
                    # -- Setup text
                    text = "Check out the README file for a full list of commands and features."
                    link_text = "README file"
                    uri = "https://github.com/Pikachannel/bluesky-bots"
                    byte_start = text.encode("utf-8").find(link_text.encode("utf-8"))
                    byte_end = byte_start + len(link_text.encode("utf-8"))

                    # -- Creates the clickable link
                    facet = {
                        "index": {
                            "byteStart": byte_start,
                            "byteEnd": byte_end
                        },
                        "features": [
                            {
                                "$type": "app.bsky.richtext.facet#link",
                                "uri": uri
                            }
                        ]
                    }

                    # -- Send the DM response
                    dm.send_message(
                        models.ChatBskyConvoSendMessage.Data(
                            convo_id=convo.id,
                            message=models.ChatBskyConvoDefs.MessageInput(
                                text=text,
                                facets=[facet] # Attaches the clickable link to the text
                            ),
                        )
                    )
                
        except Exception as e:
            print(f"[DM Worker] Error: {e}")
            continue
        finally:
            await asyncio.sleep(300) # Check dms every 5 minutes

def error_message(dm: Any, convo: Any) -> None:
    dm.send_message(
    models.ChatBskyConvoSendMessage.Data(
        convo_id=convo.id,
        message=models.ChatBskyConvoDefs.MessageInput(
            text=f"An error occurred while processing your request.\nPlease make sure you format the command correctly and try again."
        ),
    )
)
