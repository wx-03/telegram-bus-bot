import os

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
mode = os.getenv("MODE")
URL = os.getenv("URL") if mode == "prod" else os.getenv("URL_DEV")

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": f"{URL}/webhook"}
)
print(response)
