DOMAIN = "bahnvorhersage"

CONF_START_STATION = "start_station"
CONF_DESTINATION_STATION = "destination_station"
CONF_NEXT_DEPARTURES = "next_departures"
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_NEXT_DEPARTURES = 2
DEFAULT_UPDATE_INTERVAL = 3
MIN_UPDATE_INTERVAL = 1
MAX_SENSORS = 30

CONF_HIDE_LOW_DELAY = "hidelowdelay"
CONF_OFFSET = "offset"
DEFAULT_OFFSET = "00:00"
CONF_IGNORED_TRAINTYPES = "ignored_train_types"
CONF_DROP_LATE_TRAINS = "drop_late_trains"

CONF_SEARCH_FOR_ARRIVAL = "search_for_arrival"
CONF_ONLY_REGIONAL = "only_regional"
CONF_BIKE = "bike"

IGNORED_TRAINTYPES_OPTIONS = {
    "S": "Stadtbahn (S-Bahn)",
    "N": "Regional Bahn (RB), Regional Express (RE)",
    "F": "EuroCity (EC), Intercity Express (ICE), Intercity (IC)",
    "D": "Bayrische Regionalbahn, Wiener Lokalbahn",
}