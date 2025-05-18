import json
import os

import dotenv
import requests


def main():
    def process_data(data):
        for service in data:
            lowercase_service_no = service["ServiceNo"].lower()
            direction_info = {
                "Direction": service["Direction"],
                "Category": service["Category"],
                "OriginCode": service["OriginCode"],
                "DestinationCode": service["DestinationCode"],
                "AM_Peak_Freq": service["AM_Peak_Freq"],
                "AM_Offpeak_Freq": service["AM_Offpeak_Freq"],
                "PM_Peak_Freq": service["PM_Peak_Freq"],
                "PM_Offpeak_Freq": service["PM_Offpeak_Freq"],
            }
            if lowercase_service_no in all_services:
                all_services[lowercase_service_no]["Directions"].append(direction_info)
            else:
                all_services[lowercase_service_no] = {
                    "ServiceNo": service["ServiceNo"],
                    "Operator": service["Operator"],
                    "Directions": [direction_info],
                }

    dotenv.load_dotenv()
    API_KEY = os.getenv("API_KEY")
    URL = "https://datamall2.mytransport.sg/ltaodataservice/BusServices"
    headers = {"AccountKey": API_KEY, "Accept": "application/json"}

    i = 0
    all_services = {}
    while True:
        response = requests.request("GET", f"{URL}?$skip={i * 500}", headers=headers)
        data = response.json()["value"]

        if not data:
            break

        process_data(data)

        i += 1

    with open("./bus_services.json", "w") as f:
        json.dump(all_services, f, indent=4)


if __name__ == "__main__":
    main()
