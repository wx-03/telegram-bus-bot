import os

import dotenv
import requests

dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id: str, text: str):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text, "parse_mode": "html"},
    )


def send_message_inline_keyboard(chat_id: str, text: str, buttons: list[list[dict]]):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": {"inline_keyboard": buttons},
            "parse_mode": "html",
        },
    )


def send_message_inline_keyboard_from_list(chat_id: str, text: str, list: list[any]):
    inline_keyboard = []
    for item in list:
        inline_keyboard_button = {"text": item, "callback_data": item}
        inline_keyboard.append([inline_keyboard_button])
    send_message_inline_keyboard(chat_id, text, inline_keyboard)


def answerCallbackQuery(callback_query_id: str):
    requests.post(
        f"{TELEGRAM_API_URL}/answerCallbackQuery",
        json={"callback_query_id": callback_query_id},
    )

def send_location(chat_id: str, latitude: str, longitude: str):
    requests.post(
        f"{TELEGRAM_API_URL}/sendLocation",
        json={
            "chat_id": chat_id,
            "longitude": longitude,
            "latitude": latitude
        }
    )
