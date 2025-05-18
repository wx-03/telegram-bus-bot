import json
import os

import dotenv
import requests


def main():
    dotenv.load_dotenv()
    API_KEY = os.getenv("API_KEY")
    URL = "https://datamall2.mytransport.sg/ltaodataservice/BusRoutes"
    headers = {"AccountKey": API_KEY, "Accept": "application/json"}

    i = 0
    all_services = {}

    def process_data(data):
        for stop in data:
            bus_stop_dict = {
                "StopSequence": stop["StopSequence"],
                "BusStopCode": stop["BusStopCode"],
            }
            direction_string = str(stop["Direction"])
            service_number = stop["ServiceNo"]
            if not service_number.lower() in all_services:
                all_services[service_number.lower()] = {
                    "ServiceNo": service_number,
                    direction_string: [bus_stop_dict],
                }
            else:
                if direction_string in all_services[service_number.lower()]:
                    # Append stop to current list
                    all_services[service_number.lower()][direction_string].append(
                        bus_stop_dict
                    )
                else:
                    # Create new direction for bus service
                    all_services[service_number.lower()][direction_string] = [
                        bus_stop_dict
                    ]

    while True:
        response = requests.request("GET", f"{URL}?$skip={i * 500}", headers=headers)
        data = response.json()["value"]
        if not data:
            break
        process_data(data)
        i += 1

    with open("./bus_routes.json", "w") as f:
        json.dump(all_services, f, indent=4)


if __name__ == "__main__":
    main()
