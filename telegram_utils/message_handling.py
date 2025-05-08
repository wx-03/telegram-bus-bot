from .messaging import send_message
from .commands import handle_command
import json

def handle_message(data):
    print(json.dumps(data, indent=4))
    if not 'text' in data['message']:
        raise Exception('Sorry, I can only understand text :(')
    chatid = data['message']['chat']['id']
    message_text = data['message']['text']
    
    if message_text.startswith('/'):
        message_text_list = message_text.strip().split() # Split command with whitespace as separator
        command_word = message_text_list[0][1::]
        args = message_text_list[1::]
        handle_command(chatid, command_word, args)