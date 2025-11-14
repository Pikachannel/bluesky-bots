# -------- Imports --------
import random
from atproto import Client, client_utils

# -------- Make Post Function --------
async def make_post(client, post_cid, post_uri, user_did, messages, user_data):
    # -- Check if the user has a nickname set
    display_name = user_data.get(user_did, {}).get("nickname", None)

    # -- Get the users name
    if not display_name:
        users_profile = client.get_profile(user_did)
        display_name = users_profile.display_name
        if not display_name:
            display_name = users_profile.handle.split(".")[0] # Set to users handle if no display name is found

    # -- Format the random message with display name
    random_message = random.choice(messages)
    formatted_message = random_message.format(display_name=display_name)

    reply_builder = client_utils.TextBuilder()
    reply_builder.text(formatted_message)

    # -- Send the post
    post = client.send_post(
        reply_builder,
        reply_to={
            "parent": {"cid": post_cid, "uri": post_uri},
            "root": {"cid": post_cid, "uri": post_uri}
        }
    )

    print(f"[Post] Post made ({post.uri})")
