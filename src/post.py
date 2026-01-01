# -------- Imports --------
import random
from atproto import Client, client_utils
import time

post_dict = {}

# -------- Make Post Function --------
async def make_post(client: Client, post_cid: str, post_uri: str, user_did: str, post_text: str, messages: dict, user_data: dict, lang: str = "en") -> None:
    global post_dict

    messages = messages[lang]

    # -- Check the post interval (time)
    post_interval_time = user_data.get(user_did, {}).get("interval", [])
    if user_did in post_dict and len(post_interval_time) > 0:
        last_post_time = post_dict[user_did]
        current_time = time.time()
        
        interval = post_interval_time[0]
        if len(post_interval_time) == 2:
            interval = random.uniform(post_interval_time[0], post_interval_time[1])
        
        if current_time - last_post_time < interval:
            print(f"[Post] Skipping post for {user_did} due to post interval ({interval} seconds)")
            return
    if len(post_interval_time) > 0:
        post_dict[user_did] = time.time()

    # -- Check the post chance
    post_chance = user_data.get(user_did, {}).get("chance", 100)
    if random.uniform(0, 100) > post_chance:
        print(f"[Post] Skipping post for {user_did} due to post chance ({post_chance}%)")
        return

    # -- Check if the user has a nickname set
    display_name = user_data.get(user_did, {}).get("nickname", None)

    # -- Get the users name
    if not display_name:
        users_profile = client.get_profile(user_did)
        display_name = users_profile.display_name
        if not display_name:
            display_name = users_profile.handle.split(".")[0] # Set to users handle if no display name is found

    # -- Check mode and generate message
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
