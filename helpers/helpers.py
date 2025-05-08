from datetime import datetime
import json

def format_timing(str):
    if str == '':
        return ''
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime('%I:%M %p')
    return formatted

def get_load(str):
    match str:
        case 'SEA':
            return 'Seats available'
        case 'SDA':
            return 'Standing available'
        case 'LSD':
            return 'Limited standing'
        case _:
            return ''

def get_type(str):
    match str:
        case 'SD':
            return 'Single deck'
        case 'DD':
            return 'Double deck'
        case 'BD':
            return 'Bendy'

def get_bus_stop_description(code):
    with open('storage/bus_stop_map_code.json', 'r') as f:
        bus_stops = json.load(f)
        return bus_stops[code]['Description']
    raise Exception('Bus stop not found')
