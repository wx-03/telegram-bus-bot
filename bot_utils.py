import os
import dotenv
import requests

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(chat_id, text):
    requests.post(f'{TELEGRAM_API_URL}/sendMessage', json={
        "chat_id": chat_id,
        "text": text
    })
