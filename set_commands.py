import os
import json

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

with open("storage/bot_commands.json") as f:
    commands = json.load(f)
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands",
        params={
            "commands": json.dumps(commands)
        },
    )
    print(response)
