import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from .const import (
    DOMAIN, CONF_START_STATION, CONF_DESTINATION_STATION, CONF_NEXT_DEPARTURES, CONF_UPDATE_INTERVAL,
    DEFAULT_NEXT_DEPARTURES, DEFAULT_UPDATE_INTERVAL, DEFAULT_OFFSET, MAX_SENSORS,
    CONF_HIDE_LOW_DELAY, CONF_SEARCH_FOR_ARRIVAL, CONF_ONLY_REGIONAL, CONF_BIKE,
    CONF_OFFSET, CONF_IGNORED_TRAINTYPES, CONF_DROP_LATE_TRAINS, IGNORED_TRAINTYPES_OPTIONS
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow"""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Build the unique ID from both station and via_stations
            start_station = user_input[CONF_START_STATION]
            destination_station = user_input[CONF_DESTINATION_STATION]
            unique_id = (
                f"bahnvorhersage_{start_station}_{destination_station}"
                .lower()
                .replace(" ", "_")
            )
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            _LOGGER.debug("Initialized new sensor with station: %s", unique_id)

            full_title = f"{user_input[CONF_START_STATION]} to {user_input[CONF_DESTINATION_STATION]}"

            return self.async_create_entry(
                title=full_title,
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema(),
            errors=errors,
        )

    def data_schema(self):
        return vol.Schema(
            {
                vol.Required(CONF_START_STATION): cv.string,
                vol.Required(CONF_DESTINATION_STATION): cv.string,
                vol.Optional(CONF_NEXT_DEPARTURES, default=DEFAULT_NEXT_DEPARTURES): cv.positive_int,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
                vol.Optional(CONF_HIDE_LOW_DELAY, default=False): cv.boolean,
                vol.Optional(CONF_DROP_LATE_TRAINS, default=False): cv.boolean,
                vol.Optional(CONF_SEARCH_FOR_ARRIVAL, default=False): cv.boolean,
                vol.Optional(CONF_ONLY_REGIONAL, default=False): cv.boolean,
                vol.Optional(CONF_BIKE, default=False): cv.boolean,
                vol.Optional(CONF_OFFSET, default=DEFAULT_OFFSET): cv.string,
                vol.Optional(CONF_IGNORED_TRAINTYPES, default=[]): cv.multi_select(IGNORED_TRAINTYPES_OPTIONS),
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry.entry_id)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow"""

    def __init__(self, config_entry_id: str) -> None:
        """Initialize options flow."""
        self.config_entry_id = config_entry_id

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        config_entry = self.hass.config_entries.async_get_entry(self.config_entry_id)
        current_options = config_entry.options or config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_NEXT_DEPARTURES,
                        default=current_options.get(CONF_NEXT_DEPARTURES, DEFAULT_NEXT_DEPARTURES)
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=current_options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
                    ): cv.positive_int,
                    vol.Optional(
                        CONF_HIDE_LOW_DELAY,
                        default=current_options.get(CONF_HIDE_LOW_DELAY, False)
                    ): cv.boolean,
                    vol.Optional(
                        CONF_DROP_LATE_TRAINS,
                        default=current_options.get(CONF_DROP_LATE_TRAINS, False)
                    ): cv.boolean,
                    vol.Optional(
                        CONF_SEARCH_FOR_ARRIVAL,
                        default=current_options.get(CONF_SEARCH_FOR_ARRIVAL, False)
                    ): cv.boolean,
                    vol.Optional(
                        CONF_ONLY_REGIONAL,
                        default=current_options.get(CONF_ONLY_REGIONAL, False)
                    ): cv.boolean,
                    vol.Optional(
                        CONF_BIKE,
                        default=current_options.get(CONF_BIKE, False)
                    ): cv.boolean,
                    vol.Optional(
                        CONF_OFFSET,
                        default=current_options.get(CONF_OFFSET, DEFAULT_OFFSET)
                    ): cv.string,
                    vol.Optional(
                        CONF_IGNORED_TRAINTYPES,
                        default=current_options.get(CONF_IGNORED_TRAINTYPES, [])
                    ): cv.multi_select(IGNORED_TRAINTYPES_OPTIONS),
                }
            ),
        )
