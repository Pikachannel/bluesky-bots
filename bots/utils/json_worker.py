# -------- Imports --------
import json

# -------- Json Worker Function --------
async def json_worker(path, queue, user_data):
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

            # -- Add the new data to the dict
            if update["user_did"] not in data:
                data[update["user_did"]] = {} # Set to empty dict if user was not in the file
            data[update["user_did"]]["nickname"] = update["nickname"]
            user_data.clear()
            user_data.update(data)

            # -- Update the file
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[JSON Worker] An error has occured, {e}")
        finally:
            queue.task_done() # Remove task from queue 
