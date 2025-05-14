import json

from .commands import handle_callback_query, handle_command, handle_location, handle_state
from .messaging import send_message

from .state import State, get_state, clear_state


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
                clear_state(chat_id)
                handle_location(chat_id, latitude, longitude)
            if "text" in message:
                message_text = message["text"].strip().lower()

                # If the message is a command, clear state before handling command
                if message_text.startswith("/"):
                    clear_state(chat_id)
                    message_text_list = (
                        message_text.lower().split()
                    )  # Split command with whitespace as separator
                    command_word = message_text_list[0][1::]
                    args = message_text_list[1::]
                    handle_command(chat_id, command_word, args)
                # If the message is not a command and the bot is waiting for a reply (state not none), handle message as a reply
                elif get_state(chat_id) != State.NONE:
                    state = get_state(chat_id)
                    handle_state(chat_id, state, message)
                    clear_state(chat_id)
        except Exception as e:
            send_message(chat_id, str(e))
