"""Coordinator for Tesla Connector integration."""

import asyncio
import logging

from config.custom_components.tesla_connector.models.vehicle.vehicle import TeslaVehicle
from config.custom_components.tesla_connector.models.wall_connector.wall_connector import (
    WallConnector,
)
from config.custom_components.tesla_connector.owner_api.exceptions import (
    TeslaTokenException,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, timedelta

from .const import UPDATE_INTERVAL, DOMAIN, COORDINATOR_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class TeslaVehicleCoordinator(DataUpdateCoordinator):
    """Tesla Vehicle Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, vehicle: TeslaVehicle) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Tesla vehicle coordinator",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            update_method=self._async_update_data,
            always_update=True,
        )

        self._vehicle = vehicle

    async def _async_update_data(self) -> dict:
        try:
            async with asyncio.timeout(COORDINATOR_TIMEOUT):
                return await self._vehicle.async_get_vehicle_data()
        except Exception:
            _LOGGER.exception("Error fetching tesla data")
            return self._vehicle.current_data

    @property
    def vehicle(self) -> TeslaVehicle:
        """Return the Tesla vehicle."""
        return self._vehicle

    def get_vehicle_device_info(self) -> DeviceInfo:
        """Return device information for the vehicle."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._vehicle.vin)},
            manufacturer="Tesla",
            name=f"Tesla {self._vehicle.vin}",
        )


class TeslaWallConnectorCoordinator(DataUpdateCoordinator):
    """Tesla Wall Connector Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, wall_connector: WallConnector) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Tesla wall connector coordinator",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            update_method=self._async_update_data,
            always_update=True,
        )

        self._wall_connector = wall_connector

    async def _async_update_data(self) -> dict:
        try:
            async with asyncio.timeout(COORDINATOR_TIMEOUT):
                return await self._wall_connector.async_get_wall_connector_data()
        except Exception:
            _LOGGER.exception("Error fetching wall connector data")
            return self._wall_connector.current_data

    @property
    def wall_connector(self) -> WallConnector:
        """Return the Tesla Wall Connector."""
        return self._wall_connector

    def get_wall_connector_device_info(self) -> DeviceInfo:
        """Return device information for the wall connector."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._wall_connector.wall_connector_id)},
            manufacturer="Tesla",
            name=f"Tesla Wall Connector {self._wall_connector.wall_connector_id}",
        )
