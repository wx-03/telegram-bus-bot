import json
from datetime import datetime, timedelta, timezone

from exceptions.exceptions import NoSearchResultsError


def format_timing(str: str) -> str:
    if str == "":
        return ""
    dt = datetime.fromisoformat(str)
    formatted = dt.strftime("%I:%M %p")
    return formatted


def get_time_difference(str: str) -> timedelta:
    if str == "":
        return ""
    tz_sgt = timezone(timedelta(hours=8))
    now = datetime.now(tz_sgt)
    later = datetime.fromisoformat(str)
    return later - now


def format_timedelta(timedelta: timedelta) -> str:
    if timedelta.days < 0:
        return "Arr"
    seconds = timedelta.seconds
    minutes = seconds // 60
    if minutes <= 0:
        return "Arr"
    return f"{minutes} min"


def get_load(str: str) -> str:
    match str:
        case "SEA":
            return "Seats available"
        case "SDA":
            return "Standing available"
        case "LSD":
            return "Limited standing"
        case _:
            return ""


def get_type(str: str) -> str:
    match str:
        case "SD":
            return "Single deck"
        case "DD":
            return "Double deck"
        case "BD":
            return "Bendy"


def get_bus_stop_description(code: str) -> str:
    with open("storage/bus_stop_map_code.json", "r") as f:
        bus_stops = json.load(f)
        if not code in bus_stops:
            raise NoSearchResultsError("No bus stops with this code")
        return bus_stops[code]["Description"]


def is_bus_stop_code(str: str) -> bool:
    return str.isnumeric() and (len(str) == 5)


def get_bus_stop_location(code: str) -> tuple[str, str]:
    with open("storage/bus_stop_map_code.json", "r") as f:
        bus_stops = json.load(f)
        if not code in bus_stops:
            raise NoSearchResultsError("No bus stops with this code")
        return bus_stops[code]["Latitude"], bus_stops[code]["Longitude"]


def get_bus_directions(service_no: str) -> list[dict]:
    with open("storage/bus_services.json", "r") as f:
        bus_services = json.load(f)
        if not service_no in bus_services:
            raise NoSearchResultsError("No buses with this service number")
        return bus_services[service_no]["Directions"]


def get_bus_route(service_no: str, direction: str) -> list[str]:
    with open("storage/bus_routes.json", "r") as f:
        bus_routes = json.load(f)
        if not service_no in bus_routes:
            raise NoSearchResultsError("No buses with this service number")
        if not direction in bus_routes[service_no]:
            raise NoSearchResultsError(f"No such direction for bus {service_no}")
        stops = [
            stop["BusStopCode"]
            for stop in sorted(
                bus_routes[service_no][direction], key=lambda x: x["StopSequence"]
            )
        ]
        return stops


def search_bus_stop_descriptions(query: str) -> list:
    search_results = []
    with open("storage/bus_stop_map_description.json", "r") as f:
        stops = json.load(f)
        for stop in stops:
            if query in stop:
                search_results.append(stops[stop])
    if not search_results:
        raise NoSearchResultsError("No bus stops found. Try another search query.")
    return search_results
