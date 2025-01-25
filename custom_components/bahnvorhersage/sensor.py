import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, CONF_START_STATION, CONF_DESTINATION_STATION

_LOGGER = logging.getLogger(__name__)

class JourneySensor(CoordinatorEntity, SensorEntity):
    """Representation of a journey sensor."""

    def __init__(self, coordinator, config):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._start_station = config[CONF_START_STATION]
        self._destination_station = config[CONF_DESTINATION_STATION]
        self._attr_name = f"{self._start_station} → {self._destination_station}"
        self._attr_unique_id = (
            f"journey_sensor_{self._start_station}_{self._destination_station}"
            .lower()
            .replace(" ", "_")
        )
        self._attr_icon = "mdi:train"

        _LOGGER.debug(
            "JourneySensor initialized: name=%s, unique_id=%s",
            self._attr_name,
            self._attr_unique_id,
        )

    @property
    def native_value(self):
        """Return the next departure information."""
        if self.coordinator.data:
            next_departure = self.coordinator.data[0]  # First entry as next departure

            departure_time = next_departure.get("departure")
            arrival_time = next_departure.get("arrival")

            if departure_time and arrival_time:
                return f"Departs: {departure_time}, Arrives: {arrival_time}"
            else:
                return "Incomplete Data"
        else:
            return "No Data"

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        if self.coordinator.data:
            return {
                "start_station": self._start_station,
                "destination_station": self._destination_station,
                "next_departure": self.coordinator.data[0],
                "total_journeys": len(self.coordinator.data),
                "last_update": self.coordinator.last_update.isoformat()
                if self.coordinator.last_update
                else "Unknown",
            }
        else:
            return {"error": "No data fetched yet"}

    @property
    def available(self):
        """Return availability based on the coordinator's last update."""
        return self.coordinator.last_update_success

    async def async_added_to_hass(self):
        """Called when the sensor is added to Home Assistant."""
        _LOGGER.debug("Sensor added: %s", self._attr_name)
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up the sensor for the given config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    config = config_entry.data

    _LOGGER.debug(
        "Setting up JourneySensor for route: %s → %s",
        config.get(CONF_START_STATION, "Unknown Start"),
        config.get(CONF_DESTINATION_STATION, "Unknown Destination"),
    )

    async_add_entities([JourneySensor(coordinator, config)])
