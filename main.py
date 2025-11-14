# -------- Imports --------
import asyncio 
from bots.run_post import main

# -------- Run Bots Function --------
async def run_bots():
  """
  Run the bot in a background task so it can be implemented in a server running other things.
  Alternatively run.py can be used as the main.py if the bot is running on a standalone server.
  """
  asyncio.create_task(main())

asyncio.run(run_bots()) 
