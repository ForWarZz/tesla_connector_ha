"""Coordinator for Tesla Connector integration."""

import asyncio
import logging

from .owner_api.exceptions import (
    TeslaTokenException,
)

from .models.device import TeslaBaseDevice
from .models.vehicle.vehicle import TeslaVehicle
from .models.wall_connector.wall_connector import (
    WallConnector,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, timedelta
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import UPDATE_INTERVAL, DOMAIN, COORDINATOR_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class TeslaBaseCoordinator(DataUpdateCoordinator):
    """Base class for Tesla coordinators."""

    def __init__(self, hass: HomeAssistant, device: TeslaBaseDevice, name: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=name,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
            update_method=self._async_update_data,
            always_update=True,
        )

        self._device = device

    @property
    def device(self) -> TeslaBaseDevice:
        """Return the Tesla device."""
        return self._device

    async def _async_update_data(self) -> dict:
        """Update data from the API."""
        raise NotImplementedError("This method should be overridden in subclasses.")

    def get_device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device.device_id)},
            manufacturer="Tesla",
            name=f"Tesla {self._device.device_id}",
        )


class TeslaVehicleCoordinator(TeslaBaseCoordinator):
    """Tesla Vehicle Data Update Coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        vehicle: TeslaVehicle,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, vehicle, name="Tesla Vehicle Coordinator")

    @property
    def vehicle(self) -> TeslaVehicle:
        """Return the Tesla vehicle."""
        return self._device

    async def _async_update_data(self) -> dict:
        try:
            async with asyncio.timeout(COORDINATOR_TIMEOUT):
                return await self.vehicle.async_get_vehicle_data()
        except TeslaTokenException:
            _LOGGER.error("Tesla token expired, re-authentication required")
            raise ConfigEntryAuthFailed
        except Exception:
            _LOGGER.exception("Error fetching tesla data")
            return self.vehicle.current_data


class TeslaWallConnectorCoordinator(TeslaBaseCoordinator):
    """Tesla Wall Connector Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, wall_connector: WallConnector) -> None:
        """Initialize the coordinator."""
        super().__init__(hass, wall_connector, name="Tesla Wall Connector Coordinator")

    @property
    def wall_connector(self) -> WallConnector:
        """Return the Tesla Wall Connector."""
        return self._device

    async def _async_update_data(self) -> dict:
        try:
            async with asyncio.timeout(COORDINATOR_TIMEOUT):
                return await self.wall_connector.async_get_wall_connector_data()
        except TeslaTokenException:
            _LOGGER.error("Tesla token expired, re-authentication required")
            raise ConfigEntryAuthFailed
        except Exception:
            _LOGGER.exception("Error fetching wall connector data")
            return self.wall_connector.current_data
