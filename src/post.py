# -------- Imports --------
import random
from atproto import Client, client_utils
import time

# -------- Post Manager Class --------
class PostManager:
    def __init__(self) -> None:
        self.post_times: dict[str, float] = {}
        self.post_numbers: dict[str, int] = {}

    # -------------
    # -- Interval (time) check
    def interval_time_check(self, user_did: str, user_data: dict) -> bool:
        intervals = user_data.get(user_did, {}).get("interval", [])
        if not intervals:
            return True

        now = time.time()
        next_allowed = self.post_times.get(user_did, 0)

        if now < next_allowed:
            remaining = next_allowed - now
            print(f"[Post] Skipping post for {user_did} ({remaining:.2f}s remaining)")
            return False

        interval = intervals[0] if len(intervals) == 1 else random.uniform(intervals[0], intervals[1])
        self.post_times[user_did] = now + interval
        return True

    # -------------
    # -- Interval (posts) check
    def interval_posts_check(self, user_did: str, user_data: dict) -> bool:
        intervals = user_data.get(user_did, {}).get("interval_posts", [])
        if not intervals:
            return True

        # -- Setup posts counter
        if user_did not in self.post_numbers:
            skip = intervals[0] if len(intervals) == 1 else random.randint(intervals[0], intervals[1])
            self.post_numbers[user_did] = skip

        # -- Check if the post should be skipped
        if self.post_numbers[user_did] > 0:
            self.post_numbers[user_did] -= 1
            print(f"[Post] Skipping post for {user_did} ({self.post_numbers[user_did]} posts remaining)")
            return False

        # -- Reset counter
        skip = intervals[0] if len(intervals) == 1 else random.randint(intervals[0], intervals[1])
        self.post_numbers[user_did] = skip

        return True        

    # -------------
    # -- Chance check
    def chance_check(self, user_did: str, user_data: dict) -> bool:
        post_chance = user_data.get(user_did, {}).get("chance", 100)
        if random.uniform(0, 100) > post_chance:
            print(f"[Post] Skipping post for {user_did} due to post chance ({post_chance}%)")
            return False
        return True

    # -------------
    # -- Get nickname
    def get_nickname(self, client: Client, user_did: str, user_data: dict) -> str:
        nickname = user_data.get(user_did, {}).get("nickname")

        if nickname:
            return nickname

        profile = client.get_profile(user_did)
        return (
            profile.display_name
            or profile.handle.split(".")[0]
        )

    # -------------
    # -- Make post
    async def make_post(self, client: Client, post_cid: str, post_uri: str, user_did: str, post_text: str, messages: dict, user_data: dict, lang: str = "en") -> None:
        messages = messages[lang]

        # -- Check if the post can be made
        if not self.interval_time_check(user_did, user_data):
            return

        if not self.interval_posts_check(user_did, user_data):
            return

        if not self.chance_check(user_did, user_data):
            return

        # -- Buld the post
        nickname = self.get_nickname(client, user_did, user_data)

        random_message = random.choice(messages)
        formatted_message = random_message.format(display_name=nickname)

        builder = client_utils.TextBuilder()
        builder.text(formatted_message)

        # -- Make the post
        post = client.send_post(
            builder,
            reply_to={
                "parent": {"cid": post_cid, "uri": post_uri},
                "root": {"cid": post_cid, "uri": post_uri}
            }
        )

        print(f"[Post] Post made ({post.uri})")
    
    # -------------
    # -- Delete post
    async def delete_post(self, client: Client, message: dict, account_did: str, user_did: str) -> None:
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
