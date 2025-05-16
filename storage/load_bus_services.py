import json
import os

import dotenv
import requests

def main():
    dotenv.load_dotenv()
    API_KEY = os.getenv("API_KEY")
    URL = "https://datamall2.mytransport.sg/ltaodataservice/BusServices"
    headers = {"AccountKey": API_KEY, "Accept": "application/json"}

    i = 0
    all_services = []
    while True:
        response = requests.request("GET", f"{URL}?$skip={i * 500}", headers=headers)
        data = response.json()["value"]
        
        if not data:
            break
        all_services.extend(data)
        i += 1

    with open("./bus_services.json", "w") as f:
        json.dump(all_services, f, indent=4)

if __name__ == "__main__":
    main()
