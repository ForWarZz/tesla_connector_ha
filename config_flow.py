"""Config flow for Tesla Connector."""

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_REFRESH_TOKEN, CONF_VIN, CONF_WALL_CONNECTOR_ID, DOMAIN


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
