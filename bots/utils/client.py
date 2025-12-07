# -------- Imports --------
from atproto import Client
from typing import Optional

# -------- Login Function --------
async def login(username: str, password: str) -> Optional[Client]:
    try:
        # -- Setup client connection
        client = Client()
        profile = client.login(username, password)
        client.profile = profile
        print(f"[Client] Logged in as {profile.handle} ({profile.did})")
        return client # Return both the client and profile objects
    except Exception as e:
        print(f"[Client] An error occured while creating a client session, {e}")
        return None # Return none if the login failed
