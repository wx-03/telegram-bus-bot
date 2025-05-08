from .messaging import send_message_inline_keyboard, send_message, answerCallbackQuery
from lta_utils.lta_api import get_bus_services_by_code, get_bus_timing
from helpers.helpers import format_timing

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
        bus_stop_code = args[0]
        services = get_bus_services_by_code(bus_stop_code) 
        inline_keyboard = []
        for service in services:
            inline_keyboard_button = {
                "text": service,
                "callback_data": f'{bus_stop_code}:{service}'
            }
            inline_keyboard.append([inline_keyboard_button])
        send_message_inline_keyboard(chatid, "Please select bus service:", inline_keyboard)

def handle_callback_query(data):
    chat_id = data['message']['chat']['id']
    bus_stop_code, service_no = data['data'].split(':')
    arrivals = get_bus_timing(bus_stop_code, service_no)
    message = ""
    for arrival in arrivals:
        timing = format_timing(arrival['EstimatedArrival'])
        message += f'<b>{timing}</b>\n'
    send_message(chat_id, message)
    answerCallbackQuery(data['id'])
