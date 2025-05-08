import json

from .commands import handle_callback_query, handle_command
from .messaging import send_message


def handle_message(data):
    if 'callback_query' in data:
        chat_id = data['callback_query']['message']['chat']['id']
        try:
            handle_callback_query(data['callback_query'])
        except Exception as e:
            send_message(chat_id, str(e))

    if 'message' in data:
        chat_id = data['message']['chat']['id']
        try:
            if not 'text' in data['message']:
                raise Exception('Sorry, I can only understand text :(')
            message_text = data['message']['text']
        
            if message_text.startswith('/'):
                message_text_list = message_text.strip().split() # Split command with whitespace as separator
                command_word = message_text_list[0][1::]
                args = message_text_list[1::]
                handle_command(chat_id, command_word, args)
        except Exception as e:
            send_message(chat_id, str(e))

