"""Config flow for Tesla Connector."""

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import CONF_REFRESH_TOKEN, CONF_VIN, DOMAIN, CONF_WALL_CONNECTOR_ID

_LOGGER = logging.getLogger(__name__)


# class TeslaConnectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
#     """Handle a config flow for Tesla Connector."""

#     def _get_schema(self):
#         """Return the schema for the form."""
#         return vol.Schema(
#             {
#                 vol.Required(CONF_REFRESH_TOKEN): cv.string,
#                 vol.Required(CONF_VIN): cv.string,
#             }
#         )

#     async def async_step_user(self, user_input=None) -> ConfigFlowResult:
#         """Handle the initial step."""
#         errors = {}

#         if user_input is not None:
#             refresh_token = user_input.get(CONF_REFRESH_TOKEN)
#             vin = user_input.get(CONF_VIN)

#             if not refresh_token or not vin:
#                 errors["base"] = "missing_fields"
#             else:
#                 return self.async_create_entry(
#                     title="Tesla Connector",
#                     data={
#                         CONF_REFRESH_TOKEN: refresh_token,
#                         CONF_VIN: vin,
#                     },
#                 )

#         return self.async_show_form(
#             step_id="user",
#             data_schema=self._get_schema(),
#             errors=errors,
#         )


class TeslaConnectorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tesla Connector."""

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.data = {}

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        if user_input is not None:
            self.data[CONF_REFRESH_TOKEN] = user_input[CONF_REFRESH_TOKEN]
            return await self.async_step_vehicle()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REFRESH_TOKEN): str,
                }
            ),
        )

    async def async_step_vehicle(self, user_input=None):
        """Handle the vehicle step."""
        if user_input is not None:
            self.data[CONF_VIN] = user_input[CONF_VIN]
            return await self.async_step_wall_connector()

        return self.async_show_form(
            step_id="vehicle",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_VIN): str,
                }
            ),
        )

    async def async_step_wall_connector(self, user_input=None):
        """Handle the wall connector step."""
        if user_input is not None:
            self.data[CONF_WALL_CONNECTOR_ID] = user_input[CONF_WALL_CONNECTOR_ID]
            return self.async_create_entry(title="Tesla Connector", data=self.data)

        return self.async_show_form(
            step_id="wall_connector",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_WALL_CONNECTOR_ID): str,
                }
            ),
        )
