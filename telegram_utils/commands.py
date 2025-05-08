from .messaging import send_message

def handle_command(chatid, command_word, args):
    match command_word:
        case 'busstop':
            busstop(chatid, args)
        case _:
            raise Exception('Invalid command 😯')

def busstop(chatid, args):
    if len(args) == 0:
        raise Exception('Please provide bus stop number or name')
    if len(args) == 1 and args[0].isnumeric():
        send_message(chatid, args[0])
