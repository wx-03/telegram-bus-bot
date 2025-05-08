import os

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
URL = os.getenv("URL")

response = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook", params={"url": URL})
print(response.json())
