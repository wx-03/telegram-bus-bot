import heapq
import json
import logging
import textwrap

import geopy.distance

from helpers.helpers import (
    format_timedelta,
    format_timing,
    get_bus_directions,
    get_bus_route,
    get_bus_stop_description,
    get_bus_stop_location,
    get_load,
    get_time_difference,
    get_type,
    is_bus_stop_code,
)
from lta_utils.lta_api import get_bus_services_by_code, get_bus_timing

from .messaging import (
    answerCallbackQuery,
    send_location,
    send_message,
    send_message_inline_keyboard,
    send_message_inline_keyboard_from_list,
    typing,
)
from .state import State, set_state

logger = logging.getLogger(__name__)


def handle_command(chat_id: str, command_word: str, args: list[str]):
    match command_word:
        case "busstop":
            busstop(chat_id, args)
        case "help":
            help(chat_id)
        case "start":
            start(chat_id)
        case "bus":
            bus(chat_id, args)
        case _:
            raise Exception("Invalid command 😯")


def handle_state(chat_id: str, state: State, message: dict):
    assert state != State.NONE, "state should not be none"
    match state:
        case state.BUSSTOP:
            args = message["text"].lower().split(" ")
            busstop(chat_id, args)
        case state.BUS:
            args = message["text"].lower().split(" ")
            bus(chat_id, args)


def start(chat_id: str):
    message = textwrap.dedent(
        """
        Welcome to SGNextBus!
        This bot helps you check real-time bus arrival timings in Singapore
        Type /help for a full list of commands and their usage
    """
    )
    send_message(chat_id, message)


def help(chat_id: str):
    message = textwrap.dedent(
        """
        <b>🚌 Get bus timings by stop code:</b>
        <code>/busstop 12345</code>
        • You can also type /busstop, then send the code after
        
        <b>🔍 Get bus timings by stop name:</b>
        <code>/busstop ang mo kio int</code>
        • You can also type /busstop, then send the name after
        • If the name isn't exact, you'll get a list of similar matches  
        • If multiple stops have the same name, a list of codes will be shown

        <b>🚍 Get bus timings by bus service number:</b>
        <code>/bus 123</code>
        • You can also type /bus, then send the service number after

        <b>📍 Find nearby bus stops:</b>
        • Just send a location, and the 10 nearest stops will be shown
    """
    )
    send_message(chat_id, message)


def busstop(chat_id: str, args: list[str]):
    if len(args) == 0:
        set_state(chat_id, State.BUSSTOP)
        send_message(chat_id, "Please send your bus stop code or bus stop name:")
        return
    if len(args) == 1 and is_bus_stop_code(args[0]):
        bus_stop_code = args[0]
        send_bus_services(chat_id, bus_stop_code)
    else:
        # Search bus stop descriptions
        search_query = " ".join(args).lower().strip()
        with open("storage/bus_stop_map_description.json", "r") as f:
            stops = json.load(f)
            # If there is an exact match
            if search_query in stops:
                if len(stops[search_query]) > 1:
                    send_message_inline_keyboard_from_list(
                        chat_id,
                        "Select bus stop:",
                        [stop["BusStopCode"] for stop in stops[search_query]],
                    )
                else:
                    send_bus_services(chat_id, stops[search_query][0]["BusStopCode"])
            else:
                search_results = []
                # Search for descriptions that contain query
                for stop in stops:
                    if search_query in stop:
                        search_results.append(stops[stop])

                if not search_results:
                    send_message(
                        chat_id, "No bus stops found. Try another search query."
                    )
                    return

                inline_keyboard = []
                for result in search_results:
                    for bus_stop in result:
                        button = {
                            "text": f"{bus_stop['Description']} ({bus_stop['BusStopCode']})",
                            "callback_data": bus_stop["BusStopCode"],
                        }
                        inline_keyboard.append([button])
                send_message_inline_keyboard(
                    chat_id, "Choose bus stop:", inline_keyboard
                )


def sort_bus_services(service: dict) -> str:
    return service["service"].zfill(3)


def send_bus_services(chat_id: str, bus_stop_code: str):
    services: list[str] = sorted(
        get_bus_services_by_code(bus_stop_code), key=sort_bus_services
    )
    bus_stop_description = get_bus_stop_description(bus_stop_code)
    send_bus_stop_location(chat_id, bus_stop_code)
    if not services:
        raise Exception("No more bus liao :(")
    inline_keyboard = []
    for service in services:
        inline_keyboard_button = {
            "text": f'{service["service"]} ({format_timedelta(get_time_difference(service["next_arrival"]))})',
            "callback_data": f"{bus_stop_code}:{service['service']}:0",
        }
        inline_keyboard.append([inline_keyboard_button])
    message = (
        f"<b>{bus_stop_description} ({bus_stop_code})</b>\nPlease select bus service:"
    )
    send_message_inline_keyboard(chat_id, message, inline_keyboard)


def send_bus_stop_location(chat_id, bus_stop_code):
    latitude, longitude = get_bus_stop_location(bus_stop_code)
    send_location(chat_id, latitude, longitude)


def handle_callback_query(data: dict):
    chat_id = data["message"]["chat"]["id"]
    callback_data = data["data"]
    if ":" in callback_data:
        bus_stop_code, service_no, should_send_map = callback_data.split(":")
        if should_send_map == "1":
            send_bus_stop_location(chat_id, bus_stop_code)
        send_bus_timings(chat_id, bus_stop_code, service_no)
    elif is_bus_stop_code(data["data"]):
        bus_stop_code = data["data"]
        send_bus_services(chat_id, bus_stop_code)
    elif "|" in data["data"]:
        service_no, direction = callback_data.split("|")
        bus_stop_codes = get_bus_route(service_no, direction)
        inline_keyboard = []
        for code in bus_stop_codes:
            button = {
                "text": get_bus_stop_description(code),
                "callback_data": f"{code}:{service_no}:1",
            }
            inline_keyboard.append([button])
        send_message_inline_keyboard(chat_id, "Choose bus stop: ", inline_keyboard)
    else:
        raise Exception("invalid callback data")
    answerCallbackQuery(data["id"])


def send_bus_timings(chat_id, bus_stop_code, service_no):
    arrivals = get_bus_timing(bus_stop_code, service_no)
    message = f"<b>{get_bus_stop_description(bus_stop_code)} ({bus_stop_code})\nBus {service_no}</b>\n\n"
    for arrival in arrivals:
        duration = get_time_difference(arrival["EstimatedArrival"])
        timing = format_timing(arrival["EstimatedArrival"])
        if timing == "":
            continue
        load = get_load(arrival["Load"])
        type = get_type(arrival["Type"])
        message += f"<u>{timing} ({format_timedelta(duration)})</u>\n{load}\n{type}\n\n"
    send_message(chat_id, message)


class BusStopDistance:
    def __init__(self, distance: float, bus_stop: dict):
        self.distance = distance
        self.bus_stop = bus_stop

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance

    def __eq__(self, other):
        return self.distance == other.distance


def handle_location(chat_id: str, latitude: str, longitude: str):
    typing(chat_id)
    user_location = (float(latitude), float(longitude))

    top_k_closest = get_closest_k_stops(user_location, 10)
    inline_keyboard = []
    for stop in top_k_closest:
        button = {
            "text": f"{stop['Description']} ({stop['BusStopCode']})",
            "callback_data": stop["BusStopCode"],
        }
        inline_keyboard.append([button])
    send_message_inline_keyboard(chat_id, "Nearest bus stops:", inline_keyboard)


def get_closest_k_stops(user_location: tuple[float, float], k: int) -> list[dict]:
    stops_dist: list[BusStopDistance] = []
    with open("storage/bus_stops.json", "r") as f:
        bus_stops = json.load(f)
        for stop in bus_stops:
            bus_stop_location = (float(stop["Latitude"]), float(stop["Longitude"]))
            dist = geopy.distance.distance(user_location, bus_stop_location)
            stops_dist.append(BusStopDistance(dist, stop))
    heapq.heapify(stops_dist)
    top_k_closest = []
    for i in range(k):
        top_k_closest.append(stops_dist[0].bus_stop)
        heapq.heappop(stops_dist)
    return top_k_closest


def bus(chat_id: str, args: list[str]):
    if len(args) == 0:
        set_state(chat_id, State.BUS)
        send_message(chat_id, "Please send bus service number:")
        return
    bus_number = args[0]
    directions = get_bus_directions(bus_number)
    inline_keyboard = []
    for direction in directions:
        button = {
            "text": f"To {get_bus_stop_description(direction['DestinationCode'])}",
            "callback_data": f"{bus_number}|{direction['Direction']}",
        }
        inline_keyboard.append([button])
    send_message_inline_keyboard(chat_id, "Please select direction:", inline_keyboard)
