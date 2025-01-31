from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta, datetime
import aiohttp
import async_timeout
import logging
import json
from urllib.parse import quote

from .const import (
    DOMAIN, CONF_START_STATION, CONF_DESTINATION_STATION, CONF_NEXT_DEPARTURES,
    DEFAULT_UPDATE_INTERVAL, DEFAULT_NEXT_DEPARTURES, DEFAULT_OFFSET,
    CONF_HIDE_LOW_DELAY, CONF_OFFSET, MIN_UPDATE_INTERVAL,
    CONF_IGNORED_TRAINTYPES, CONF_DROP_LATE_TRAINS, CONF_UPDATE_INTERVAL,
    CONF_SEARCH_FOR_ARRIVAL, CONF_ONLY_REGIONAL, CONF_BIKE
)

_LOGGER = logging.getLogger(__name__)

class BVCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, start_station: str, destination_station: str, bike: bool, only_regional: bool, search_for_arrival: bool, offset: str, next_departures: int, update_interval: int, hide_low_delay: bool, ignored_train_types: list, drop_late_trains: bool):
        self.start_station = start_station
        self.destination_station = destination_station
        self.next_departures = next_departures
        self.hide_low_delay = hide_low_delay
        self.search_for_arrival = search_for_arrival
        self.only_regional = only_regional
        self.bike = bike
        self.offset = self.convert_offset_to_seconds(offset)
        self.ignored_train_types = ignored_train_types
        self.drop_late_trains = drop_late_trains

        start_station_cleaned = " ".join(start_station.split())
        encoded_start_station = quote(start_station_cleaned, safe=",-")
        encoded_start_station = encoded_start_station.replace(" ", "%20")

        destination_station_cleaned = " ".join(destination_station.split())
        encoded_destination_station = quote(destination_station_cleaned, safe=",-")
        encoded_destination_station = encoded_destination_station.replace(" ", "%20")

        self.api_url = "https://bahnvorhersage.de/api/journeys"

        # Ensure update_interval is passed correctly
        update_interval = max(update_interval, MIN_UPDATE_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=f"BV {start_station} to {destination_station}",
            update_interval=timedelta(minutes=update_interval),
        )
        _LOGGER.debug(
            "Coordinator initialized for station %s to %s with update interval %d minutes",
            start_station, destination_station, update_interval
        )

    def convert_offset_to_seconds(self, offset: str) -> int:
        """
        Converts an offset string in HH:MM or HH:MM:SS format to seconds.
        """
        try:
            time_parts = list(map(int, offset.split(":")))
            if len(time_parts) == 2:  # HH:MM format
                return time_parts[0] * 3600 + time_parts[1] * 60
            elif len(time_parts) == 3:  # HH:MM:SS format
                return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]
            else:
                raise ValueError("Invalid time format")
        except ValueError:
            _LOGGER.error("Invalid offset format: %s", offset)
            return 0

    async def _async_update_data(self):
        """
        Fetches data from the API and processes it based on the configuration.
        """
        _LOGGER.debug("Fetching data for station: %s to %s", self.start_station, self.destination_station)
        async with aiohttp.ClientSession() as session:
            try:
                async with async_timeout.timeout(10):
                    # Prepare the request payload
                    payload = {
                        "start": self.start_station,
                        "destination": self.destination_station,
                        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),  # Current date and time
                        "search_for_arrival": self.search_for_arrival,
                        "only_regional": self.only_regional,
                        "bike": self.bike,
                    }

                    response = await session.post(self.api_url, json=payload)
                    if response.status == 200:
                        result = await response.json()
                        _LOGGER.debug("API response: %s", result)
                        return result
                    else:
                        _LOGGER.error("API request failed with status %s: %s", response.status, await response.text())
                    response.raise_for_status()

                    # Set last_update timestamp
                    self.last_update = datetime.now()

                    # Filter departures based on the offset and ignored products
                    filtered_departures = []
                    ignored_train_types = self.ignored_train_types
                    if ignored_train_types:
                        _LOGGER.debug("Ignoring products: %s", ignored_train_types)

                    MAX_SIZE_BYTES = 16000

                    for departure in data.get("legs", []):
                        _LOGGER.debug("Processing departure: %s", departure)
                        json_size = len(json.dumps(filtered_departures))
                        if json_size > MAX_SIZE_BYTES:
                            _LOGGER.info("Filtered departures JSON size exceeds limit: %d bytes for entry: %s . Ignoring some future departures to keep the size lower.", json_size, self.start_station)
                            break

                        departure_time = departure.get("departure")

                        # If no valid departure time is found, log a warning and continue to the next departure
                        if not departure_time:
                            _LOGGER.warning("No valid departure time found for entry: %s", departure)
                            continue

                        # Convert the departure time to a datetime object
                        if isinstance(departure_time, int):  # Unix timestamp case
                            departure_time = datetime.fromtimestamp(departure_time)
                        else:  # ISO 8601 string case
                            try:
                                departure_time = datetime.strptime(departure_time, "%Y-%m-%dT%H:%M:%S")
                            except ValueError:
                                _LOGGER.warning("Departure time format issue for %s: %s", departure, departure_time)
                                continue

                        # Apply any delay to the departure time, if applicable
                        if not self.drop_late_trains:
                            _LOGGER.debug("Departure time without added delay: %s", departure_time)
                            delay_departure = 0  # Default delay if not available

                            # Sicherstellen, dass delay_departure_prediction nicht None ist
                            if "departureDelayPrediction" in departure and departure["departureDelayPrediction"]:
                                delay_departure_prediction = departure["departureDelayPrediction"]
                                delay_departure = delay_departure_prediction.get("offset", 0)
                            else:
                                _LOGGER.debug("No departure delay prediction found, using default delay: %d", delay_departure)

                            departure_time += timedelta(minutes=delay_departure)
                            _LOGGER.debug("Departure time with added delay: %s", departure_time)

                        # Check if the train class is in the ignored list
                        train_classes = departure.get("productName", [])
                        _LOGGER.debug("Departure train classes: %s", train_classes)
                        if any(train_class in ignored_train_types for train_class in train_classes):
                            _LOGGER.debug("Ignoring departure due to train class: %s", train_classes)
                            continue

                        # Calculate the time offset and only add departures that occur after the offset
                        departure_seconds = (departure_time - datetime.now()).total_seconds()
                        if departure_seconds >= self.offset:  # Only show departures after the offset
                            filtered_departures.append(departure)

                    _LOGGER.debug("Number of departures added to the filtered list: %d", len(filtered_departures))
                    return filtered_departures[:self.next_departures]
            except Exception as e:
                _LOGGER.error("Error fetching data: %s", e)
                return []

async def async_setup_entry(hass: HomeAssistant, config_entry: config_entries.ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    start_station = config_entry.data[CONF_START_STATION]
    destination_station = config_entry.data[CONF_DESTINATION_STATION]
    next_departures = config_entry.data.get(CONF_NEXT_DEPARTURES, DEFAULT_NEXT_DEPARTURES)
    update_interval = max(config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL), MIN_UPDATE_INTERVAL)
    hide_low_delay = config_entry.data.get(CONF_HIDE_LOW_DELAY, False)
    search_for_arrival = config_entry.data.get(CONF_SEARCH_FOR_ARRIVAL, False)
    only_regional = config_entry.data.get(CONF_ONLY_REGIONAL, False)
    bike = config_entry.data.get(CONF_BIKE, False)
    offset = config_entry.data.get(CONF_OFFSET, DEFAULT_OFFSET)
    ignored_train_types = config_entry.data.get(CONF_IGNORED_TRAINTYPES, [])
    drop_late_trains = config_entry.data.get(CONF_DROP_LATE_TRAINS, [])

    coordinator = BVCoordinator(
        hass, start_station, destination_station, bike, only_regional, search_for_arrival,
        offset, next_departures, update_interval, hide_low_delay, ignored_train_types,
        drop_late_trains
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: config_entries.ConfigEntry):
    unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)
    return unload_ok
