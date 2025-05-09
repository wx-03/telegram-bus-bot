import json
import textwrap

from helpers.helpers import (format_timedelta, format_timing,
                             get_bus_stop_description, get_load,
                             get_time_difference, get_type, is_bus_stop_code)
from lta_utils.lta_api import get_bus_services_by_code, get_bus_timing

from .messaging import (answerCallbackQuery, send_message,
                        send_message_inline_keyboard,
                        send_message_inline_keyboard_from_list)


def handle_command(chat_id: str, command_word: str, args: list[str]):
    match command_word:
        case "busstop":
            busstop(chat_id, args)
        case "help":
            help(chat_id)
        case "start":
            start(chat_id)
        case _:
            raise Exception("Invalid command 😯")


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
        <b>Commands:</b>

        <code>/busstop {bus stop code}</code>
        Get bus timings using bus stop code
        
        <code>/busstop {bus stop name}</code>
        Search for bus stops with names that contain the search query
    """
    )
    send_message(chat_id, message)


def busstop(chat_id: str, args: list[str]):
    if len(args) == 0:
        raise Exception("Please provide bus stop number or name")
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
    services = sorted(get_bus_services_by_code(bus_stop_code), key=sort_bus_services)
    bus_stop_description = get_bus_stop_description(bus_stop_code)
    inline_keyboard = []
    for service in services:
        inline_keyboard_button = {
            "text": f'{service["service"]} ({format_timedelta(get_time_difference(service["next_arrival"]))})',
            "callback_data": f"{bus_stop_code}:{service['service']}",
        }
        inline_keyboard.append([inline_keyboard_button])
    message = (
        f"<b>{bus_stop_description} ({bus_stop_code})</b>\nPlease select bus service:"
    )
    send_message_inline_keyboard(chat_id, message, inline_keyboard)


def handle_callback_query(data: dict):
    chat_id = data["message"]["chat"]["id"]
    if ":" in data["data"]:
        bus_stop_code, service_no = data["data"].split(":")
        arrivals = get_bus_timing(bus_stop_code, service_no)
        message = f"<b>{get_bus_stop_description(bus_stop_code)} ({bus_stop_code})\nBus {service_no}</b>\n\n"
        for arrival in arrivals:
            duration = get_time_difference(arrival["EstimatedArrival"])
            timing = format_timing(arrival["EstimatedArrival"])
            if timing == "":
                continue
            load = get_load(arrival["Load"])
            type = get_type(arrival["Type"])
            message += (
                f"<u>{timing} ({format_timedelta(duration)})</u>\n{load}\n{type}\n\n"
            )
        send_message(chat_id, message)
    elif data["data"].isnumeric():
        bus_stop_code = data["data"]
        send_bus_services(chat_id, bus_stop_code)
    answerCallbackQuery(data["id"])
