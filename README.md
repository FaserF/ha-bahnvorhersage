[![hacs_badge](https://img.shields.io/badge/HACS-CUSTOM-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Bahnvorhersage Homeassistant Sensor
The `bahnvorhersage` sensor will give you the prediction departure time of the next trains for the given start & destination combination, containing many more attribute informations.

This integration works great side-by-side with [ha-bahnvorhersage](https://github.com/FaserF/ha-bahnvorhersage).
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
- **station**: The name of the station

### JSON Format
The API returns data in the following json format usually:

```json
{
  "departures": [
    {
      "scheduledArrival": "08:08",
      "destination": "München-Pasing",
      "train": "S 4",
      "platform": "4",
      "delayArrival": 18,
      "messages": {
        "delay": [
          {"text": "delay of a train ahead", "timestamp": "2025-01-21T07:53:00"}
        ]
      }
    }
  ]
}
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