from .messaging import send_message_inline_keyboard, send_message, answerCallbackQuery, send_message_inline_keyboard_from_list
from lta_utils.lta_api import get_bus_services_by_code, get_bus_timing
from helpers.helpers import format_timing, get_bus_stop_description
import json

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
        send_bus_services(chatid, bus_stop_code)
    else:
        # Search bus stop descriptions
        search_query = " ".join(args).lower().strip()
        print(search_query)
        with open('storage/bus_stop_map_description.json', 'r') as f:
            stops = json.load(f)
            # If there is an exact match
            if search_query in stops:
                if len(stops[search_query]) > 1:
                    send_message_inline_keyboard_from_list(chatid, 'Select bus stop:', [stop['BusStopCode'] for stop in stops[search_query]])
                else:
                    send_bus_services(chatid, stops[search_query][0]['BusStopCode'])

def send_bus_services(chatid, bus_stop_code):
    services = get_bus_services_by_code(bus_stop_code) 
    inline_keyboard = []
    for service in services:
        inline_keyboard_button = {
                "text": service,
                "callback_data": f'{bus_stop_code}:{service}'
            }
        inline_keyboard.append([inline_keyboard_button])
    bus_stop_description = get_bus_stop_description(bus_stop_code)
    message = f'<b>{bus_stop_description} ({bus_stop_code})</b>\nPlease select bus service:'
    send_message_inline_keyboard(chatid, message, inline_keyboard)


def handle_callback_query(data):
    chat_id = data['message']['chat']['id']
    if ':' in data['data']:
        bus_stop_code, service_no = data['data'].split(':')
        arrivals = get_bus_timing(bus_stop_code, service_no)
        message = ""
        for arrival in arrivals:
            timing = format_timing(arrival['EstimatedArrival'])
            message += f'<b>{timing}</b>\n'
        send_message(chat_id, message)
    elif data['data'].isnumeric():
        bus_stop_code = data['data']
        send_bus_services(chat_id, bus_stop_code)
    answerCallbackQuery(data['id'])
