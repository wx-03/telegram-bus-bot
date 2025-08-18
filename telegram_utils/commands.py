import heapq
import json
import logging
import textwrap

import geopy.distance

from exceptions.error_handling import handle_error
from exceptions.exceptions import (
    APIError,
    InvalidCallbackDataError,
    InvalidCommandError,
    NoMoreBusError,
    NoSearchResultsError,
)
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
    search_bus_stop_descriptions,
)
from lta_utils.lta_api import get_bus_services_by_code, get_bus_timing

from .messaging import (
    answerCallbackQuery,
    send_location,
    send_message,
    send_message_inline_keyboard,
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
            raise InvalidCommandError()


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
        try:
            send_bus_services(chat_id, bus_stop_code)
        except (NoSearchResultsError, NoMoreBusError, APIError) as e:
            handle_error(e, chat_id)
            return
    else:
        # Search bus stop descriptions
        search_query = " ".join(args).lower().strip()
        try:
            results = search_bus_stop_descriptions(search_query)
            if len(results) == 1 and len(results[0]) == 1:
                bus_stop = results[0][0]
                print(results)
                send_bus_services(chat_id, bus_stop["BusStopCode"])
                return
            inline_keyboard = []
            for result in results:
                for bus_stop in result:
                    button = {
                        "text": f"{bus_stop['Description']} ({bus_stop['BusStopCode']})",
                        "callback_data": bus_stop["BusStopCode"],
                    }
                    inline_keyboard.append([button])
            send_message_inline_keyboard(chat_id, "Choose bus stop:", inline_keyboard)
        except NoSearchResultsError as e:
            handle_error(e, chat_id)


def sort_bus_services(service: dict) -> str:
    return service["service"].zfill(3)


def send_bus_services(chat_id: str, bus_stop_code: str):
    """Sends a message with buttons for each bus service of the bus stop.

    Args:
        chat_id (str): Chat ID.
        bus_stop_code (str): Code of the bus stop to send bus services for.

    Raises:
        NoMoreBusError: If the bus stop no longer has any bus services.
        APIError: If the API response status code is not 200.
    """
    services: list[str] = sorted(
        get_bus_services_by_code(bus_stop_code), key=sort_bus_services
    )
    bus_stop_description = get_bus_stop_description(bus_stop_code)
    send_bus_stop_location(chat_id, bus_stop_code)
    if not services:
        raise NoMoreBusError()
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
    """Sends the location of the specified bus stop.

    Args:
        chat_id (_type_): Chat ID.
        bus_stop_code (_type_): Code of the bus stop to send the location of.
    """
    try:
        latitude, longitude = get_bus_stop_location(bus_stop_code)
        send_location(chat_id, latitude, longitude)
    except NoSearchResultsError as e:
        handle_error(e, chat_id)


def handle_callback_query(data: dict):
    # busstopcode:serviceno:shouldsendmap -> send bus timing
    # busstopcode -> send bus services
    # serviceno|direction -> send bus route
    chat_id = data["message"]["chat"]["id"]
    callback_data = data["data"]
    if ":" in callback_data:
        # If ":" in callback_data, means data is busstopcode:serviceno:shouldsendmap,
        # where shouldsendmap is 1 if the user has clicked on the button from the bus route
        # and 0 if the user has clicked on the button from bus stop (as map was already sent with
        # bus stop)
        bus_stop_code, service_no, should_send_map = callback_data.split(":")
        if should_send_map == "1":
            send_bus_stop_location(chat_id, bus_stop_code)
        send_bus_timings(chat_id, bus_stop_code, service_no)
    elif is_bus_stop_code(data["data"]):
        bus_stop_code = data["data"]
        try:
            send_bus_services(chat_id, bus_stop_code)
        except (NoSearchResultsError, NoMoreBusError) as e:
            handle_error(e, chat_id)
    elif "|" in data["data"]:
        try:
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
        except NoSearchResultsError as e:
            handle_error(e, chat_id)
    else:
        raise InvalidCallbackDataError()
    answerCallbackQuery(data["id"])


def send_bus_timings(chat_id: str, bus_stop_code: str, service_no: str):
    """Sends a message to the chat containing the arrival timings, load, and type of the
       specified bus service at the specified bus stop.

    Args:
        chat_id (str)
        bus_stop_code (str)
        service_no (str)
    """
    try:
        arrivals = get_bus_timing(bus_stop_code, service_no)
        message = f"<b>{get_bus_stop_description(bus_stop_code)} ({bus_stop_code})\nBus {service_no}</b>\n\n"
        for arrival in arrivals:
            if arrival["EstimatedArrival"] == "":
                continue
            duration = get_time_difference(arrival["EstimatedArrival"])
            timing = format_timing(arrival["EstimatedArrival"])
            if timing == "":
                continue
            load = get_load(arrival["Load"])
            type = get_type(arrival["Type"])
            message += (
                f"<u>{timing} ({format_timedelta(duration)})</u>\n{load}\n{type}\n\n"
            )
        button = {"text": "Refresh", "callback_data": f"{bus_stop_code}:{service_no}:0"}
        send_message_inline_keyboard(chat_id, message, [[button]])
    except (APIError, NoMoreBusError, NoSearchResultsError) as e:
        handle_error(e, chat_id)


class BusStopDistance:
    """Object that contains 2 fields: bus stop and distance, where distance refers to the distance
    from the bus stop to a particular location.

    >, < and == are overloaded to order based on distance. This object is used to order bus stops within
    a min heap based on distance.
    """

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
    """Sends a message with buttons for each of the 10 closest bus stops to the specified location.

    Args:
        chat_id (str): ID of the chat.
        latitude (str): Latitude of the location.
        longitude (str): Longitude of the location.
    """
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
    """Returns a list of k closest bus stops to the specified location.

    Args:
        user_location (tuple[float, float]): tuple containing latitude and longitude of the location.
        k (int)

    Returns:
        list[dict]: List of k closest bus stops.
    """
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
    """Handles the /bus command.

    Args:
        chat_id (str)
        args (list[str])
    """
    if len(args) == 0:
        set_state(chat_id, State.BUS)
        send_message(chat_id, "Please send bus service number:")
        return
    bus_number = args[0]
    try:
        directions = get_bus_directions(bus_number)
        inline_keyboard = []
        for direction in directions:
            button = {
                "text": f"To {get_bus_stop_description(direction['DestinationCode'])}",
                "callback_data": f"{bus_number}|{direction['Direction']}",
            }
            inline_keyboard.append([button])
        send_message_inline_keyboard(
            chat_id, "Please select direction:", inline_keyboard
        )
    except NoSearchResultsError as e:
        handle_error(e, chat_id)
