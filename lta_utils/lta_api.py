import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
HEADERS = {"AccountKey": API_KEY, "Accept": "application/json"}


def get_bus_services_by_code(code: str) -> list[str]:
    url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
    res = requests.get(f"{url}?BusStopCode={code}", headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Error occurred. Response status code: {res.status_code}")
    if not "Services" in res.json():
        return []
    services = res.json()["Services"]
    service_numbers = []
    for service in services:
        service_numbers.append({
            "service": service["ServiceNo"],
            "next_arrival": service["NextBus"]["EstimatedArrival"]
        })
    return service_numbers


def get_bus_timing(code: str, service: str) -> list[dict]:
    url = "https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival"
    res = requests.get(f"{url}?BusStopCode={code}&ServiceNo={service}", headers=HEADERS)
    data = res.json()["Services"][0]
    arrivals = [data["NextBus"], data["NextBus2"], data["NextBus3"]]
    return arrivals
