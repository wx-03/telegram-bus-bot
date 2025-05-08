import json

with open('bus_stops.json', 'r') as json_file:
    bus_stops = json.load(json_file)
    with open('bus_stop_map_code.json', 'w') as f:
        dict = {}
        for stop in bus_stops:
            key = stop['BusStopCode']
            info = {
                "RoadName": stop['RoadName'],
                "Description": stop['Description'],
                "Latitude": stop['Latitude'],
                "Longitude": stop['Longitude']
            }
            dict[key] = info
        json.dump(dict, f, indent=4)
    with open('bus_stop_map_description.json', 'w') as f:
        dict = {}
        for stop in bus_stops:
            key = stop['Description']
            info = {
                "BusStopCode": stop['BusStopCode'],
                "RoadName": stop['RoadName'],
                "Latitude": stop['Latitude'],
                "Longitude": stop['Longitude']
            }
            if not key in dict:
                dict[key] = [info]
            else:
                dict[key].append(info)
        json.dump(dict, f, indent=4)

