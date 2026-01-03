# -------- Imports --------
import asyncio

# -------- Command Class --------
class CommandManager:
    def __init__(self, user_data: dict, json_queue: asyncio.Queue) -> None:
        self.user_data = user_data
        self.json_queue = json_queue
    
    # -------------
    # -- To float
    # Converts a string to a float
    def to_float(self, s: str) -> float | None:
        try:
            return float(s)
        except (TypeError, ValueError):
            return None
        
    # -------------
    # -- Remove setting
    # Removes a specific setting
    async def remove_setting(self, user_did: str, setting: str) -> tuple[bool, str]:
        # -- Add to queue
        payload = {
            "type": "update",
            "user_did": user_did,
            setting: "!pop_entry"
        }

        await self.json_queue.put(payload)

        return True, f"The setting '{setting}' has been reset to the default value."

    # -------------
    # -- Nickname
    # A string at max 20 characters
    async def update_nickname(self, user_did: str, nickname: str | None) -> tuple[bool, str]:
        # -- Validation and mormalisation
        if nickname is None:
            return await self.remove_setting(user_did, "nickname") 

        nickname = nickname.strip()[:20]

        # -- Add to queue
        payload = {
            "type": "update",
            "user_did": user_did,
            "nickname": nickname
        }
        await self.json_queue.put(payload)

        return True, f"Your nickname has been updated to {nickname}\nYou can change this at any time by sending the same command.\nUse !help at any time to see all commands."

    # -------------
    # -- Chance
    # A float between 0 and 100
    async def chance(self, user_did: str, chance: str | None) -> tuple[bool, str]:
        # -- Validation and mormalisation
        if chance is None:
            return await self.remove_setting(user_did, "chance")

        chance_value = self.to_float(chance)
        if chance_value is None:
            return False, "An error occurred while updating your chance setting.\nPlease make sure you only use numbers.\nUse !help at any time to see all commands."

        if chance_value < 0 or chance_value > 100:
            return False, "An error occurred while updating your chance setting.\nPlease make sure your chance is in the range 0-100.\nUse !help at any time to see all commands."

        chance_value = round(chance_value, 2)

        # -- Add to queue
        payload = {
            "type": "update",
            "user_did": user_did,
            "chance": chance_value
        }

        await self.json_queue.put(payload)

        return True, f"The chance of a reply under your posts has been updated to '{chance_value}%'\nYou can change this at any time by sending the same command.\nUse !help at any time to see all commands."

    # -------------
    # -- Interval (time)
    # A static interval with max time of 3600 seconds
    # A ranged interval between 0 and 3600 seconds
    async def interval_time(self, user_did: str, interval: str | None) -> tuple[bool, str]:
        # -- Validation and mormalisation
        if interval is None:
            return await self.remove_setting(user_did, "interval")
    
        # -- Check if the interval is a range or static value
        intervalSplit = interval.split("-")

        # -- Range
        if len(intervalSplit) == 2:
            interval_value_1 = self.to_float(intervalSplit[0])
            interval_value_2 = self.to_float(intervalSplit[1])

            if interval_value_1 is None or interval_value_2 is None:
                return False, "An error occurred while updating your interval setting.\nPlease make sure you only use numbers.\nUse !help at any time to see all commands."
           
            interval_format_1, interval_format_2 = round(interval_value_1, 2), round(interval_value_2, 2)
         
            if interval_format_1 > interval_format_2:
                return False, "An error occurred while updating your interval setting.\Please make sure your first value is less then your second value.\nUse !help at any time to see all commands."

            if interval_format_1 < 0 or interval_format_2 < 0:
                return False, "An error occurred while updating your interval setting.\Please make sure your interval is in the range '0-3600'.\nUse !help at any time to see all commands."

            if interval_format_2 > 3600:
                return False, "An error occurred while updating your interval setting.\Please make sure your interval is in the range '0-3600'.\nUse !help at any time to see all commands."

            final_value = [interval_format_1, interval_format_2]
            text_value = f"{interval_format_1}-{interval_format_2}"
        
        # -- Static
        else:
            interval_value = self.to_float(interval)

            if interval_value is None:
                return False, "An error occurred while updating your interval setting.\nPlease make sure you only use numbers.\Use !help at any time to see all commands."

            if interval_value > 3600 or interval_value < 0:
                return False, "An error occurred while updating your interval setting.\nPlease make sure your interval is in the range '0-3600'.\Use !help at any time to see all commands."

            final_value = [round(interval_value, 2)]
            text_value = round(interval_value, 2)
        
        # -- Add to queue
        payload = {
            "type": "update",
            "user_did": user_did,
            "interval": final_value
        }

        await self.json_queue.put(payload)

        return True, f"Your interval has been updated to '{text_value}' seconds\nYou can change this at any time by sending the same command.\nUse !help at any time to see all commands."

    # -------------
    # -- Skip posts
    # A static number of posts the bot will skip, between 0 and 50 posts
    # A ranged interval of posts the bot will skip, between 0 and 50 posts
    async def skip_posts(self, user_did: str, interval: str | None) -> tuple[bool, str]:
        # -- Validation and mormalisation
        if interval is None:
            return await self.remove_setting(user_did, "skip")
    
        # -- Check if the interval is a range or static value
        intervalSplit = interval.split("-")

        # -- Range
        if len(intervalSplit) == 2:
            interval_value_1 = self.to_float(intervalSplit[0])
            interval_value_2 = self.to_float(intervalSplit[1])

            if interval_value_1 is None or interval_value_2 is None:
                return False, "An error occurred while updating your interval setting.\nPlease make sure you only use numbers.\nUse !help at any time to see all commands."
           
            interval_format_1, interval_format_2 = int(interval_value_1), int(interval_value_2)
         
            if interval_format_1 > interval_format_2:
                return False, "An error occurred while updating your interval setting.\nPlease make sure your first value is less then your second value.\nUse !help at any time to see all commands."

            if interval_format_1 < 0 or interval_format_2 < 0:
                return False, "An error occurred while updating your interval setting.\nPlease make sure your interval is in the range '0-50'.\nUse !help at any time to see all commands."

            if interval_format_2 > 50:
                return False, "An error occurred while updating your interval setting.\nPlease make sure your interval is in the range '0-50'.\nUse !help at any time to see all commands."

            final_value = [interval_format_1, interval_format_2]
            text_value = f"{interval_format_1}-{interval_format_2}"
        
        # -- Static
        else:
            interval_value = self.to_float(interval)

            if interval_value is None:
                return False, "An error occurred while updating your interval setting.\nPlease make sure you only use numbers.\nUse !help at any time to see all commands."

            if interval_value > 50 or interval_value < 0:
                return False, "An error occurred while updating your interval setting.\nPlease make sure your interval is in the range '0-50'.\nUse !help at any time to see all commands."

            final_value = [int(interval_value)]
            text_value = int(interval_value)
        
        # -- Add to queue
        payload = {
            "type": "update",
            "user_did": user_did,
            "skip": final_value
        }

        await self.json_queue.put(payload)

        return True, f"Your interval has been updated to '{text_value}' posts\nYou can change this at any time by sending the same command.\nUse !help at any time to see all commands."
        
    # -------------
    # -- Delete
    # Delete all the users' settings
    async def delete_settings(self, user_did: str) -> tuple[bool, str]:
        # -- Add to queue
        payload = {
            "type": "delete",
            "user_did": user_did
        }

        await self.json_queue.put(payload)

        return True, "Your settings have been deleted.\nYour can confirm this by using '!settings'.\nUse !help at any time to see all commands."

    # -------------
    # -- Settings
    # View a users' settings
    async def view_settings(self, user_did: str) -> tuple[bool, str]:
        # -- Settings helper
        def format_value(self, value):
            if isinstance(value, list):
                return f"{value[0]}-{value[1]}" if len(value) == 2 else value[0]
            return value

        # -- Get settings
        user_settings = self.user_data.get(user_did, {})
      
        if not user_settings:
            return False, "You have no settings configured with the bot.\nUse !help to see options for settings!"
      


        format_settings = "\n".join(
            f"{key.capitalize()}: {format_value(value)}"
            for key, value in user_settings.items()
        )
        return True, f"Your settings can be seen below!\n{format_settings}"

    # -------------
    # -- Help
    # Send a help message for the bot
    async def help(self) -> tuple[bool, str, dict]:
        # -- Format help
        text = "Check out the README file for a full list of commands and features."
        link_text = "README file"
        uri = "https://github.com/Pikachannel/positivity-bot"
        byte_start = text.encode("utf-8").find(link_text.encode("utf-8"))
        byte_end = byte_start + len(link_text.encode("utf-8"))

        # -- Create the clickable link
        facet = {
            "index": {
                "byteStart": byte_start,
                "byteEnd": byte_end
            },
            "features": [
                {
                    "$type": "app.bsky.richtext.facet#link",
                    "uri": uri
                }
            ]
        }

        return True, text, facet

