import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from .const import (
    DOMAIN,
    CONF_START_STATION,
    CONF_DESTINATION_STATION,
    CONF_UPDATE_INTERVAL,
    CONF_SEARCH_FOR_ARRIVAL,
    CONF_ONLY_REGIONAL,
    CONF_BIKE,
    DEFAULT_UPDATE_INTERVAL,
    MAX_SENSORS,
)

_LOGGER = logging.getLogger(__name__)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check for the maximum number of sensors
            existing_entries = self.hass.config_entries.async_entries(DOMAIN)
            if len(existing_entries) >= MAX_SENSORS:
                errors["base"] = "max_sensors_reached"
            else:
                try:
                    unique_id = f"{user_input[CONF_START_STATION]}_{user_input[CONF_DESTINATION_STATION]}"
                    await self.async_set_unique_id(unique_id)
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"{user_input[CONF_START_STATION]} → {user_input[CONF_DESTINATION_STATION]}",
                        data=user_input,
                    )
                except Exception as e:
                    _LOGGER.error("Error during setup: %s", e)
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=self.data_schema(),
            errors=errors,
        )

    def data_schema(self):
        """Define the data schema for user input."""
        return vol.Schema(
            {
                vol.Required(CONF_START_STATION): cv.string,
                vol.Required(CONF_DESTINATION_STATION): cv.string,
                vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.positive_int,
                vol.Optional(CONF_SEARCH_FOR_ARRIVAL, default=False): cv.boolean,
                vol.Optional(CONF_ONLY_REGIONAL, default=False): cv.boolean,
                vol.Optional(CONF_BIKE, default=False): cv.boolean,
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Define the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_options = self.config_entry.options
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_UPDATE_INTERVAL, default=current_options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): cv.positive_int,
                    vol.Optional(CONF_SEARCH_FOR_ARRIVAL, default=current_options.get(CONF_SEARCH_FOR_ARRIVAL, False)): cv.boolean,
                    vol.Optional(CONF_ONLY_REGIONAL, default=current_options.get(CONF_ONLY_REGIONAL, False)): cv.boolean,
                    vol.Optional(CONF_BIKE, default=current_options.get(CONF_BIKE, False)): cv.boolean,
                }
            ),
        )
