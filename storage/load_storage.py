import create_maps
import load_bus_routes
import load_bus_services
import load_stops

load_bus_routes.main()
print("Loaded bus routes in bus_routes.json")

load_bus_services.main()
print("Loaded bus services in bus_services.json")

load_stops.main()
print("Loaded bus stops in bus_stops.json")

create_maps.main()
print("Created bus_stop_map_code.json and bus_stop_map_description.json")
