# -------- Imports --------
from atproto import Client, client_utils

# -------- Login Function --------
async def login(username, password):
    try:
        # -- Setup client connection
        client = Client()
        profile = client.login(username, password)
        client.profile = profile
        print(f"[Client] Logged in as {profile.handle} ({profile.did})")
        return client, profile # Return both the client and profile objects
    except Exception as e:
        print(f"[Client] An error occured while creating a client session, {e}")
        return False, False # Return false if the login failed
