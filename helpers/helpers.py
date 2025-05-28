import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from exceptions.exceptions import NoSearchResultsError


def format_timing(iso_string: str) -> Optional[str]:
    """Converts an ISO 8601 datetime string to a 12-hour time format (HH:MM AM/PM).

    Args:
        iso_string (str): A datetime string in ISO 8601 format.

    Returns:
        Optional[str]: The formatted time string in HH:MM AM/PM format.
                       Returns None if the input string is empty.
    """
    if iso_string == "":
        return None
    dt = datetime.fromisoformat(iso_string)
    formatted = dt.strftime("%I:%M %p")
    return formatted


def get_time_difference(iso_string: str) -> Optional[timedelta]:
    """Calculates the time difference between the current time (SGT) and a given ISO 8601 datetime string.

    Args:
        iso_string (str): A datetime string in ISO 8601 format.

    Returns:
        Optional[timedelta]: The time difference between the current time (in Singapore Time, UTC+8)
                             and the provided datetime. Returns None if the input string is empty.
    """
    if iso_string == "":
        return None
    tz_sgt = timezone(timedelta(hours=8))
    now = datetime.now(tz_sgt)
    later = datetime.fromisoformat(iso_string)
    return later - now


def format_timedelta(delta: timedelta) -> str:
    """Formats a timedelta object into a human-readable string representing minutes until arrival.

    Args:
        delta (timedelta): The time difference to format.

    Returns:
        str: A string in the form "X min" if the timedelta is positive and non-zero.
             Returns "Arr" if the timedelta is negative or less than 1 minute.
    """
    if delta.days < 0:
        return "Arr"
    seconds = delta.seconds
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
    """Returns the bus stop description corresponding to the given bus stop code.

    Args:
        code (str): The bus stop code to look up.

    Raises:
        NoSearchResultsError: If the bus stop code is not found in the data.

    Returns:
        str: The description of the bus stop.
    """
    with open("storage/bus_stop_map_code.json", "r") as f:
        bus_stops = json.load(f)
        if not code in bus_stops:
            raise NoSearchResultsError("No bus stops with this code")
        return bus_stops[code]["Description"]


def is_bus_stop_code(str: str) -> bool:
    return str.isnumeric() and (len(str) == 5)


def get_bus_stop_location(code: str) -> tuple[str, str]:
    """Returns the location of the bus stop specified by the given bus stop code.

    Args:
        code (str): The bus stop code to look up.

    Raises:
        NoSearchResultsError: If the bus stop code is not found in the data.

    Returns:
        tuple[str, str]: A tuple of latitude and longitude of the bus stop location.
    """
    with open("storage/bus_stop_map_code.json", "r") as f:
        bus_stops = json.load(f)
        if not code in bus_stops:
            raise NoSearchResultsError("No bus stops with this code")
        return bus_stops[code]["Latitude"], bus_stops[code]["Longitude"]


def get_bus_directions(service_no: str) -> list[dict]:
    """Returns a list of directions for the specified bus service. Each direction is represented as a
       dictionary containing the following keys:

        {
        "Direction": int,
        "Category": str,
        "OriginCode": str,
        "DestinationCode": str,
        "AM_Peak_Freq": str,
        "AM_Offpeak_Freq": str,
        "PM_Peak_Freq": str,
        "PM_Offpeak_Freq": str
        }

    Args:
        service_no (str): The bus service number to get directions of.

    Raises:
        NoSearchResultsError: If the service number is not found in the data.

    Returns:
        list[dict]: A list of direction dictionaries.
    """
    with open("storage/bus_services.json", "r") as f:
        bus_services = json.load(f)
        if not service_no in bus_services:
            raise NoSearchResultsError("No buses with this service number")
        return bus_services[service_no]["Directions"]


def get_bus_route(service_no: str, direction: str) -> list[str]:
    """Returns a list of bus stop codes ordered by stop sequence for the specified bus service and direction.

    Args:
        service_no (str): Bus service number.
        direction (str): Direction number.

    Raises:
        NoSearchResultsError: If the service number or direction does not exist in the data.

    Returns:
        list[str]: List of bus stop codes ordered by stop sequence.
    """
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
    """Returns a list of bus stops that match the search query.

    Args:
        query (str): Search query to match descriptions.

    Raises:
        NoSearchResultsError: If the search query does not match any bus stop descriptions.

    Returns:
        list: List of bus stops that have descriptions matching the search query
    """
    search_results = []
    with open("storage/bus_stop_map_description.json", "r") as f:
        stops = json.load(f)
        for stop in stops:
            if query in stop:
                search_results.append(stops[stop])
    if not search_results:
        raise NoSearchResultsError("No bus stops found. Try another search query.")
    return search_results
