"""The Tesla Connector integration."""

from __future__ import annotations

import logging

from config.custom_components.tesla_connector.models.vehicle.vehicle import TeslaVehicle
from config.custom_components.tesla_connector.models.wall_connector.wall_connector import (
    WallConnector,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_REFRESH_TOKEN,
    CONF_VIN,
    DOMAIN,
    PLATFORMS,
    CONF_WALL_CONNECTOR_ID,
)
from .owner_api.client import TeslaAPIClient

from .coordinator import TeslaVehicleCoordinator, TeslaWallConnectorCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tesla Connector from a config entry."""
    tesla_client = TeslaAPIClient(
        entry.data[CONF_REFRESH_TOKEN],
    )

    tesla_vehicle = TeslaVehicle(
        entry.data[CONF_VIN],
        tesla_client,
    )

    wall_connector = WallConnector(
        entry.data[CONF_WALL_CONNECTOR_ID],
        tesla_client,
    )

    tesla_vehicle_coordinator = TeslaVehicleCoordinator(hass, tesla_vehicle)
    tesla_wall_connector_coordinator = TeslaWallConnectorCoordinator(
        hass,
        wall_connector,
    )

    # Store the coordinator in the entry data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "vehicle": tesla_vehicle_coordinator,
        "wall_connector": tesla_wall_connector_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await tesla_vehicle.async_ensure_car_woke_up()

    await tesla_vehicle_coordinator.async_config_entry_first_refresh()
    await tesla_wall_connector_coordinator.async_config_entry_first_refresh()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
