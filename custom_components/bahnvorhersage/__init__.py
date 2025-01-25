import logging
from datetime import datetime
import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_START_STATION, CONF_DESTINATION_STATION, CONF_SEARCH_FOR_ARRIVAL, CONF_ONLY_REGIONAL, CONF_BIKE

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the integration using the config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Store the config entry in hass.data
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Fetch journey data using the provided config
    from .sensor import async_setup_entry as setup_sensor
    
    # Pass async_add_entities from Home Assistant to your sensor setup
    await setup_sensor(hass, entry, async_add_entities)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def fetch_journeys(hass: HomeAssistant, config: dict) -> dict:
    """Fetch journey information from the Bahnvorhersage API."""
    session = async_get_clientsession(hass)
    url = "https://bahnvorhersage.de/api/journeys"

    # Prepare the request payload
    payload = {
        "start": config[CONF_START_STATION],
        "destination": config[CONF_DESTINATION_STATION],
        "date": datetime.now().strftime("%d.%m.%Y %H:%M"),  # Current date and time
        "search_for_arrival": config.get(CONF_SEARCH_FOR_ARRIVAL, False),
        "only_regional": config.get(CONF_ONLY_REGIONAL, False),
        "bike": config.get(CONF_BIKE, False),
    }

    _LOGGER.debug("Fetching journeys with payload: %s", payload)

    # Send the POST request
    try:
        async with session.post(url, json=payload) as response:
            if response.status == 200:
                result = await response.json()
                _LOGGER.debug("API response: %s", result)
                return result
            else:
                _LOGGER.error("API request failed with status %s: %s", response.status, await response.text())
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to API: %s", err)

    return {}
