from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

MAX_LENGTH = 70

class DBInfoSensor(SensorEntity):
    def __init__(self, coordinator, start_station, destination_station):
        self.coordinator = coordinator
        self.start_station = start_station
        self.destination_station = destination_station

        self._attr_name = f"{self.start_station} → {self.destination_station}"

        if len(self._attr_name) > MAX_LENGTH:
            self._attr_name = self._attr_name[:MAX_LENGTH]

        self._attr_unique_id = (
            f"bahnvorhersage_{self.start_station}_{self.destination_station}"
            .lower()
            .replace(" ", "_")
        )

        if len(self._attr_unique_id) > MAX_LENGTH:
            self._attr_unique_id = self._attr_unique_id[:MAX_LENGTH]

        self._attr_icon = "mdi:train"

        _LOGGER.debug(
            "DBInfoSensor initialized for station: %s to destinaton %s, unique_id: %s, name: %s",
            start_station,
            destination_station,
            self._attr_unique_id,
            self._attr_name,
        )

    @property
    def native_value(self):
        if self.coordinator.data:
            departure_time = (
                self.coordinator.data[0].get("departure", "No Data")
            )
            delay_departure_prediction = self.coordinator.data[0].get("departureDelayPrediction")
            
            if delay_departure_prediction:
                delay_departure = delay_departure_prediction.get("offset", 0)
            else:
                delay_departure = 0

            if isinstance(departure_time, int):  # Unix timestamp case
                departure_time = datetime.fromtimestamp(departure_time)

            if delay_departure == 0:
                _LOGGER.debug("Sensor state updated: %s", departure_time)
                return departure_time
            else:
                departure_time_with_delay = departure_time + timedelta(minutes=delay_departure)
                departure_time_with_delay_str = f"{departure_time_with_delay} +{delay_departure}"
                _LOGGER.debug("Sensor state updated with delay: %s", departure_time_with_delay_str)
                return departure_time_with_delay_str
        else:
            _LOGGER.warning("No data received for station: %s to destination: %s", self.start_station, self.destination_station)
            return "No Data"

    @property
    def extra_state_attributes(self):
        attribution = f"Data provided by API https://bahnvorhersage.de/api/journeys"

        next_departures = self.coordinator.data or []
        for departure in next_departures:
            if 'departure' in departure and isinstance(departure['departure'], int):
                departure['departure'] = datetime.fromtimestamp(departure['departure']).strftime('%Y-%m-%d %H:%M:%S')

        last_updated = getattr(self.coordinator, "last_update", None)
        if last_updated:
            last_updated = last_updated.isoformat()
        else:
            last_updated = "Unknown"

        return {
            "next_departures": next_departures,
            "start_station": self.start_station,
            "destination_station": self.destination_station,
            "last_updated": last_updated,
            "attribution": attribution,
        }

    @property
    def available(self):
        return self.coordinator.last_update_success if hasattr(self.coordinator, "last_update_success") else False

    async def async_update(self):
        _LOGGER.debug("Sensor update triggered but not forcing refresh.")

    async def async_added_to_hass(self):
        _LOGGER.debug("Sensor added to Home Assistant for station: %s to destination: %s", self.start_station, self.destination_station)
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )
        _LOGGER.debug("Listener attached for station: %s to destination: %s", self.start_station, self.destination_station)

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    start_station = config_entry.data.get("start_station")
    destination_station = config_entry.data.get("destination_station")

    _LOGGER.debug("Setting up DBInfoSensor for start station: %s to destination: %s", start_station, destination_station)
    async_add_entities([DBInfoSensor(coordinator, start_station, destination_station)])