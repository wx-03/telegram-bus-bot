import json
from .commands import handle_callback_query, handle_command, handle_location
from .messaging import send_message


def handle_message(data: dict):
    if "callback_query" in data:
        chat_id = data["callback_query"]["message"]["chat"]["id"]
        try:
            handle_callback_query(data["callback_query"])
        except Exception as e:
            send_message(chat_id, str(e))

    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        try:
            if "location" in message:
                location = message["location"]
                latitude = location["latitude"]
                longitude = location["longitude"]
                handle_location(chat_id, latitude, longitude)
            if "text" in message:
                message_text = message["text"]

                if message_text.startswith("/"):
                    message_text_list = (
                        message_text.strip().lower().split()
                    )  # Split command with whitespace as separator
                    command_word = message_text_list[0][1::]
                    args = message_text_list[1::]
                    handle_command(chat_id, command_word, args)
        except Exception as e:
            send_message(chat_id, str(e))
