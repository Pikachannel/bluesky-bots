# -------- Imports --------
from ..bsky.post import make_post
from ..bsky.delete import delete_post
import asyncio

# -------- Worker Function --------
async def worker(client, queue, followers_set, account_did, messages, user_data):
    print("[BSKY Worker] Worker starting")
    # -- Start Worker
    while True:
        message = await queue.get() # Get new messages as they're added to the queue
        try:
            # -- Extract message info
            user_did = message.get("did")
            eventType = message.get("commit", {}).get("collection")
            eventOperation = message.get("commit", {}).get("operation")

        # -- Check if the event type
            if eventType == "app.bsky.graph.follow":
                if eventOperation == "create":
 
                    if message.get("commit", {}).get("record", {}).get("subject", {}) == account_did: # Check if the user follows the bot
                        followers_set.add(user_did) # Add user to the follow set 

            if eventType != "app.bsky.feed.post" or eventOperation != "create": # Skip everything but posts
                continue 

            if user_did not in followers_set: # Skip none followers
                continue

            if message.get("commit", {}).get("record", {}).get("reply", {}): # Only handle delete requests for replies
                await delete_post(client, message, account_did, user_did)
                continue

            # -- Extract post cid and uri
            post_rkey = message.get("commit", {}).get("rkey")
            post_cid = message.get("commit", {}).get("cid")
            post_uri = f"at://{user_did}/app.bsky.feed.post/{post_rkey}"

            # -- Make the post
            await make_post(client, post_cid, post_uri, user_did, messages, user_data)

        except Exception as e:
            print(f"[BSKY Worker] An error has occured, {e}")
        finally:
            queue.task_done() # Remove the task from the queue
