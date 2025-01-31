[![hacs_badge](https://img.shields.io/badge/HACS-CUSTOM-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Bahnvorhersage Homeassistant Sensor
WORK IN PROGRESS! NOT WORKING YET!

The `bahnvorhersage` sensor will give you the prediction departure time of the next trains for the given start & destination combination, containing many more attribute informations.

This integration works great side-by-side with [ha-db_infoscreen](https://github.com/FaserF/ha-db_infoscreen). 
This is a superior to [ha-deutschebahn](https://github.com/FaserF/ha-deutschebahn).

## Installation
### 1. Using HACS (recommended way)

This integration is NO official HACS Integration right now.

Open HACS then install the "bahnvorhersagen" integration or use the link below.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=FaserF&repository=ha-bahnvorhersage&category=integration)

If you use this method, your component will always update to the latest version.

### 2. Manual

- Download the latest zip release from [here](https://github.com/FaserF/ha-bahnvorhersage/releases/latest)
- Extract the zip file
- Copy the folder "bahnvorhersage" from within custom_components with all of its components to `<config>/custom_components/`

where `<config>` is your Home Assistant configuration directory.

>__NOTE__: Do not download the file by using the link above directly, the status in the "master" branch can be in development and therefore is maybe not working.

## Configuration

Go to Configuration -> Integrations and click on "add integration". Then search for "bahnvorhersage".

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=bahnvorhersage)

### Configuration Variables

| Key                        | Type    | Required | Default | Description |
|----------------------------|---------|----------|---------|-------------|
| `start_station`            | string  | Yes      | -       | The starting station |
| `destination_station`      | string  | Yes      | -       | The destination station |
| `next_departures`          | int     | No       | 2       | Number of upcoming departures to show |
| `update_interval`          | int     | No       | 3       | Update interval in seconds |
| `hide_low_delay`           | boolean | No       | False   | Hide trains with low delays |
| `drop_late_trains`         | boolean | No       | False   | Exclude very late trains |
| `search_for_arrival`       | boolean | No       | False   | Search for arrival times instead of departure times |
| `only_regional`            | boolean | No       | False   | Only show regional trains |
| `bike`                     | boolean | No       | False   | Show bike-friendly trains |
| `offset`                   | string  | No       | 00:00   | Time offset for departure search |
| `ignored_traintypes`       | list    | No       | []      | List of train types to ignore |

## Automation Examples for Home Assistant

### 1. Notify on Next Departure
This automation sends a push notification with the next scheduled departure from **Start** to **Destination**.

```yaml
alias: "Next Train Departure Notification"
trigger:
  - platform: time
    at: "07:00:00"
condition: []
action:
  - service: notify.mobile_app_your_smartphone
    data:
      title: "Train Forecast"
      message: >
        The next train from {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'start_station') }}
        to {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'destination_station') }} 
        departs at {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departure'] }}.
        Estimated arrival: {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['arrival'] }}.
mode: single
```

### 2. Delay Warning for the Next Train
This automation sends a warning notification if the predicted departure delay exceeds 2 minutes.

```yaml
alias: "Train Delay Warning"
trigger:
  - platform: template
    value_template: >
      {% set delay_predictions = state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departureDelayPrediction']['predictions'] %}
      {{ (delay_predictions | sum / delay_predictions | length) > 2 }}
condition: []
action:
  - service: notify.mobile_app_your_smartphone
    data:
      title: "Train Delay Alert"
      message: >
        The train from {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'start_station') }} 
        to {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'destination_station') }} is expected to be delayed.
        Average predicted delay: {{ (state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departureDelayPrediction']['predictions'] | sum / state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departureDelayPrediction']['predictions'] | length) | round(1) }} minutes.
mode: single
```

### 3. Announce Train Departure on Smart Speaker
This automation announces the next departure time using a smart speaker like Google Home or Amazon Echo.

```yaml
alias: "Announce Next Train Departure"
trigger:
  - platform: time_pattern
    minutes: "/5"  # Check every 5 minutes
condition: []
action:
  - service: tts.google_translate_say
    entity_id: media_player.living_room_speaker
    data:
      message: >
        The next train from {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'start_station') }}
        to {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'destination_station') }} 
        departs at {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departure'] }} 
        from platform {{ state_attr('sensor.start_to_destination_bahnvorhersage', 'next_departures')[0]['departurePlatform'] }}.
mode: single
```

## API Data
### Accessing their data
The bahnvorhersage.de data is being accessed with the [API](https://bahnvorhersage.de/api/journeys) and a POST request

```json
{
    "start": "Start Station",
    "destination": "Destination",
    "date": "25.01.2025 12:00",
    "search_for_arrival": false,
    "only_regional": false,
    "bike": false
}
```

### JSON Format
The API returns data in the following json format usually:

```json
[{
    "legs": [{
        "origin": {
            "id": "1234567",
            "name": "Start",
            "location": {
                "id": "1234567",
                "latitude": 12.345678,
                "longitude": 12.345678
            },
            "products": null,
            "type": "station"
        },
        "destination": {
            "id": "1234567",
            "name": "Destination",
            "location": {
                "id": "1234567",
                "latitude": 12.345678,
                "longitude": 12.345678
            },
            "products": null,
            "type": "station"
        },
        "departure": "2025-01-25T12:02:00+01:00",
        "departurePlatform": "5",
        "arrival": "2025-01-25T13:04:00+01:00",
        "arrivalPlatform": "3",
        "cancelled": false,
        "direction": "München-Pasing",
        "stopovers": [{
            "stop": {
                "id": "1234567",
                "name": "Zorneding",
                "location": {
                    "id": "1234567",
                    "latitude": 12.345678,
                    "longitude": 12.345678
                },
                "products": null,
                "type": "station"
            },
            "arrival": null,
            "plannedArrival": null,
            "arrivalPlatform": "5",
            "departure": "2025-01-25T12:02:00+01:00",
            "plannedDeparture": "2025-01-25T12:02:00+01:00",
            "departurePlatform": "5",
            "cancelled": false,
            "type": "stopover"
        },
        [...]
        {
            "stop": {
                "id": "1234567",
                "name": "Starnberg",
                "location": {
                    "id": "1234567",
                    "latitude": 12.345678,
                    "longitude": 12.345678
                },
                "products": null,
                "type": "station"
            },
            "arrival": "2025-01-25T14:04:00+01:00",
            "plannedArrival": "2025-01-25T14:04:00+01:00",
            "arrivalPlatform": "3",
            "departure": null,
            "plannedDeparture": null,
            "departurePlatform": "3",
            "cancelled": false,
            "type": "stopover"
        }],
        "plannedDeparture": "2025-01-25T13:02:00+01:00",
        "plannedDeparturePlatform": "5",
        "departureDelayPrediction": {
            "predictions": [0.00047, 0.00084, 0.00777, 0.32811, 0.29321, 0.12286, 0.05807, 0.04459, 0.03696, 0.02058, 0.01624, 0.01396, 0.01007, 0.00752, 0.00457, 0.00473, 0.00366, 0.00221, 0.00247, 0.00234, 0.00293, 0.00199, 0.00233, 0.00223, 0.00122, 0.00194, 0.00125, 0.00071, 0.00074, 0.00069, 0.00047, 0.0005, 0.00127, 0.0005],
            "offset": 3,
            "type": "delayPrediction"
        },
        "plannedArrival": "2025-01-25T14:04:00+01:00",
        "plannedArrivalPlatform": "3",
        "arrivalDelayPrediction": {
            "predictions": [0.00043, 0.00112, 0.01883, 0.20492, 0.12529, 0.10636, 0.08477, 0.06242, 0.05973, 0.02657, 0.02752, 0.02364, 0.01864, 0.01251, 0.00584, 0.01028, 0.01035, 0.00974, 0.00533, 0.00509, 0.00918, 0.0388, 0.02247, 0.0193, 0.04173, 0.02942, 0.00706, 0.00305, 0.00247, 0.00305, 0.00129, 0.00099, 0.00127, 0.00053],
            "offset": 3,
            "type": "delayPrediction"
        },
        "line": {
            "id": "s-6662",
            "name": "S 1",
            "operator": {
                "type": "operator",
                "id": "db-regio-ag-s-bahn-munchen",
                "name": "DB Regio AG S-Bahn München"
            },
            "isRegio": true,
            "productName": "S",
            "mode": "train",
            "fahrtNr": "6662",
            "adminCode": "800725",
            "type": "line"
        },
        "tripId": "2|#VN#1#ST#1737574886#PI#",
        "type": "leg"
    }],
    "price": null,
    "refreshToken": "1234###",
    "type": "journey"
}]
```

## Bug reporting
Open an issue over at [github issues](https://github.com/FaserF/ha-bahnvorhersage/issues). Please prefer sending over a log with debugging enabled.

To enable debugging enter the following in your configuration.yaml

```yaml
logger:
    logs:
        custom_components.bahnvorhersage: debug
```

You can then find the log in the HA settings -> System -> Logs -> Enter "bahnvorhersage" in the search bar -> "Load full logs"

## Thanks to
The data is coming from the [bahnvorhersage.de/](https://bahnvorhersage.de/) website.