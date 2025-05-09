import json
from datetime import datetime, timedelta, timezone


def format_timing(str):
    if str == '':
        return ''
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime('%I:%M %p')
    return formatted

def get_time_difference(str):
    if str == '':
        return ''
    tz_sgt = timezone(timedelta(hours=8))
    now = datetime.now(tz_sgt)
    later = datetime.fromisoformat(str)
    return later - now

def format_timedelta(timedelta):
    if timedelta.days < 0:
        return 'Arr'
    seconds = timedelta.seconds
    minutes = seconds // 60
    if minutes <= 0:
        return 'Arr'
    return f"{minutes} min"

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
        if not code in bus_stops:
            raise Exception('No bus stops with this code')
        return bus_stops[code]['Description']

def is_bus_stop_code(str):
    return str.isnumeric() and (len(str) == 5)
