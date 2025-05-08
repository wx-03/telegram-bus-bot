from datetime import datetime
import json

def format_timing(str):
    if str == '':
        return ''
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime('%I:%M %p')
    return formatted

def get_bus_stop_description(code):
    with open('storage/bus_stops.json', 'r') as f:
        bus_stops = json.load(f)
    for stop in bus_stops:
        if stop['BusStopCode'] == code:
            return stop['Description']
    raise Exception('Bus stop not found')
