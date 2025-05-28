import os

import requests
from dotenv import load_dotenv

from exceptions.exceptions import APIError, NoMoreBusError

load_dotenv()

API_KEY = os.getenv("API_KEY")
HEADERS = {"AccountKey": API_KEY, "Accept": "application/json"}


def get_bus_services_by_code(code: str) -> list[dict]:
    """Returns a list of bus service numbers and their next estimated arrival timings for the specified bus stop.

    Args:
        code (str): Code of the bus stop to get bus services for.

    Raises:
        APIError: If response status code is not 200.

    Returns:
        list[dict]: List of bus service numbers and their next estimated arrival timings.
    """
    url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
    res = requests.get(f"{url}?BusStopCode={code}", headers=HEADERS)
    if res.status_code != 200:
        raise APIError(res.status_code)
    if not "Services" in res.json():
        return []
    services = res.json()["Services"]
    service_numbers = []
    for service in services:
        if "NextBus" in service:
            service_numbers.append(
                {
                    "service": service["ServiceNo"],
                    "next_arrival": service["NextBus"]["EstimatedArrival"],
                }
            )
    return service_numbers


def get_bus_timing(code: str, service: str) -> list[dict]:
    """Returns the arrival information of the next 3 buses of the specified service number
       at the given bus stop.

    Args:
        code (str): The code of the bus stop to check.
        service (str): The bus service number.

    Raises:
        APIError: If response status code is not 200.
        NoMoreBusError: If there are no upcoming buses for the given service at the bus stop.

    Returns:
        list[dict]: A list of up to 3 dictionaries, each representing an arriving bus.
    """
    url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
    res = requests.get(f"{url}?BusStopCode={code}&ServiceNo={service}", headers=HEADERS)
    if res.status_code != 200:
        raise APIError(res.status_code)
    if not "Services" in res.json():
        raise NoMoreBusError()
    if res.json()["Services"] == []:
        raise NoMoreBusError()
    data = res.json()["Services"][0]
    arrivals = [data["NextBus"], data["NextBus2"], data["NextBus3"]]
    return arrivals
