import os

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
HEADERS = {
    'AccountKey': API_KEY,
    'Accept': 'application/json'
}

def get_bus_services_by_code(code):
    url = 'https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival'
    res = requests.get(f'{url}?BusStopCode={code}', headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f'Error occurred. Response status code: {res.status_code}')
    services = res.json()['Services']
    service_numbers = []
    for service in services:
        service_numbers.append(service['ServiceNo'])
    return service_numbers

def get_bus_timing(code, service):
    url = 'https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival'
    res = requests.get(f'{url}?BusStopCode={code}&ServiceNo={service}', headers=HEADERS)
    data = res.json()['Services'][0]
    arrivals = []
    if 'NextBus' in data:
        arrivals.append(data['NextBus'])
    if 'NextBus2' in data:
        arrivals.append(data['NextBus2'])
    if 'NextBus3' in data:
        arrivals.append(data['NextBus3'])
    return arrivals
