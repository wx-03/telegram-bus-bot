from datetime import datetime
import json

def format_timing(str):
    if str == '':
        return ''
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime('%I:%M %p')
    return formatted

def get_bus_stop_description(code):
    with open('storage/bus_stop_map_code.json', 'r') as f:
        bus_stops = json.load(f)
        return bus_stops[code]['Description']
    raise Exception('Bus stop not found')
