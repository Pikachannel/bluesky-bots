# -------- Imports --------
import asyncio
from datetime import datetime 

# -------- Refresh Followers Function --------
async def refresh_followers(client, followers_set, account_did, per_page=100):
    # -- Start function
    while True:
        try:
            all_followers = []
            cursor = None

            # -- Loop through all pages
            while True:
                params = {"actor": account_did, "limit": per_page}
                if cursor:
                    params["cursor"] = cursor

                # -- Get the followers page
                response = client.app.bsky.graph.get_followers(params=params)
                followers_page = response.followers

                all_followers.extend(followers_page) # Add new followers to the list

                # -- Get the cursor
                next_cursor = getattr(response, "cursor", None)
                if callable(next_cursor):
                    next_cursor = next_cursor()

                if not next_cursor:
                    break # Stop if it's on the last page
                cursor = next_cursor

            # -- Extract all user DIDs and add them to the set
            follower_dids = [f.did for f in all_followers]

            followers_set.clear()      
            followers_set.update(follower_dids)  
            print(f"[Follower Refresh] {len(followers_set)} followers loaded for {client.profile.handle} at {datetime.now()}")
        except Exception as e:
            print(f"[Follower Refresh] Error: {e}")
        await asyncio.sleep(300) # Get followers every 5 minutes
