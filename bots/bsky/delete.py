# -------- Delete Function --------
async def delete_post(client, message, account_did, user_did):
    # -- Get all post information 
    commit = message.get("commit", {})
    record = commit.get("record", {})
    reply = record.get("reply", {})
    parent = reply.get("parent", {})
    root = reply.get("root", {})

    # -- Get the orignal posts key and psoters did and the replies
    rootDID, rootKEY = root.get("uri", "").split('at://')[1].split('/app.bsky.feed.post/')
    parentDID, parentKEY = parent.get("uri", "").split('at://')[1].split('/app.bsky.feed.post/')

    # -- Check if the original post belongs to the user and the reply belongs to the bot
    if user_did == rootDID and account_did == parentDID:
        if record.get("text", "").lower() == "delete":
            client.delete_post(parent.get("uri", "")) # Delete the post
            print(f"[Delete] Post deleted from {user_did}")



