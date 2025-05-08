import json
import os

import dotenv
import requests

dotenv.load_dotenv()
API_KEY = os.getenv("API_KEY")
URL = "https://datamall2.mytransport.sg/ltaodataservice/BusStops"
headers = {"AccountKey": API_KEY, "Accept": "application/json"}

i = 0
all_stops = []
while True:
    response = requests.request("GET", f"{URL}?$skip={i * 500}", headers=headers)
    data = response.json()["value"]
    if not data:
        break
    all_stops.extend(data)
    i += 1

with open("./bus_stops.json", "w") as f:
    json.dump(all_stops, f, indent=4)
