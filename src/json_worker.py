# -------- Imports --------
import json
import asyncio

# -------- Json Worker Function --------
async def json_worker(path: str, queue: asyncio.Queue[dict], user_data: dict) -> None:
    # -- Start function
    print("[JSON Worker] Worker starting")
    while True:
        try:
            # -- Get new update
            update = await queue.get()
            try:
                # -- Load the data from the path
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {} # Set to empty if no file found

            # -- Get the update data
            if update.get("type") == "update":
                user_did = update["user_did"]
                update_data = {}
                for key, value in update.items():
                    if key not in ["type", "user_did"]:
                        if value == "!pop_entry": # Check if the value is a pop instruction
                            if data.get(user_did, {}).get(key, None):
                                data[user_did].pop(key) # Pop an entry if a pop command was recieved
                        else:
                            update_data[key] = value 
                        
                if user_did not in data:
                    data[user_did] = {} # Set to empty dict if user was not in the file
                data[user_did].update(update_data)
                user_data.clear()
                user_data.update(data)
            
            # -- Delete a user's data
            elif update.get("type") == "delete":
                user_did = update["user_did"]
                if user_did in data:
                    del data[user_did]
                    user_data.clear()
                    user_data.update(data)

            # -- Update the file
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[JSON Worker] An error has occured, {e}")
        finally:
            queue.task_done() # Remove task from queue 
