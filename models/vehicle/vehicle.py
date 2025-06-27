"""Vehicle model for Tesla vehicles."""

import asyncio
from collections.abc import Callable
from datetime import datetime, timedelta
from functools import partial
import logging

from aiohttp import ClientResponseError
from asyncio import TimeoutError

from ...const import COMMAND_TIMEOUT, SLEEP_THRESHOLD, WAKE_UP_THRESHOLD
from ...owner_api.api_response import TeslaAPIResponse
from ...owner_api.client import TeslaAPIClient
from ...owner_api.exceptions import TeslaBaseException
from ..device import TeslaBaseDevice
from .vehicle_data import ChargingState, VehicleData

_LOGGER = logging.getLogger(__name__)


class TeslaVehicle(TeslaBaseDevice):
    """Representation of a Tesla vehicle."""

    def __init__(self, vin: str, apiClient: TeslaAPIClient) -> None:
        """Initialize a TeslaVehicle with a VIN and Tesla API client."""
        super().__init__(vin, apiClient)
        self._current_data = None

        self._last_wake_up: datetime = None
        self._last_command_send: datetime = None

    @property
    def vin(self) -> str:
        """Return the VIN of the vehicle."""
        return self._device_id

    @property
    def current_data(self) -> VehicleData:
        """Return the current data of the vehicle (cached)."""
        return self._current_data

    async def async_get_vehicle_data(self) -> VehicleData:
        """Get vehicle data from the Tesla API."""
        if (
            self._last_command_send
            and datetime.now() - self._last_command_send
            > timedelta(minutes=SLEEP_THRESHOLD)
        ) or (
            self._current_data
            and self._current_data.charge_state.charging_state != ChargingState.CHARGING
        ):
            _LOGGER.debug(
                "Skipping vehicle data fetch to allow sleep mode, last command sent at %s",
                self._last_command_send,
            )
            if self._current_data is not None:
                self._current_data.state = "offline"
            return self._current_data

        try:
            vehicle_data = await self._apiClient.async_get_vehicle_data(self.vin)
            self._current_data = VehicleData(vehicle_data.data)
        except ClientResponseError as err:
            if err.status == 408:
                _LOGGER.info(
                    "Request timed out, vehicle is potentially offline.. getting cached data"
                )
                if self._current_data is not None:
                    self._current_data.state = "offline"

        return self._current_data

    async def _async_wake_up(self) -> TeslaAPIResponse:
        """Wake up the vehicle."""
        return await self._apiClient.async_wake_up_car(self.vin)

    async def async_ensure_car_woke_up(self, force=False) -> TeslaAPIResponse:
        """Wake up the vehicle if necessary."""
        should_wake_up = (
            self._last_wake_up is None
            or self._current_data is None
            or self._current_data.state == "offline"
            or datetime.now() - self._last_wake_up
            > timedelta(minutes=WAKE_UP_THRESHOLD)
            or force
        )

        if should_wake_up:
            await self._async_wake_up()
            self._last_wake_up = datetime.now()
            self._last_command_send = datetime.now()

    async def _async_send_command(
        self, command: Callable[..., TeslaAPIResponse]
    ) -> TeslaAPIResponse:
        """Send a command to the vehicle with retries."""
        start_time = datetime.now()
        _LOGGER.debug("Sending command to vehicle: %s", self.vin)

        await self.async_ensure_car_woke_up()

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                async with asyncio.timeout(delay=COMMAND_TIMEOUT):
                    response: TeslaAPIResponse = await command()
                    if not response.result:
                        raise TeslaBaseException(
                            f"Command failed for vehicle vin: {self.vin} REASON: {response.reason}"
                        )
                    break
            except (TimeoutError, TeslaBaseException) as err:
                _LOGGER.warning(
                    "Attempt %d/%d failed for VIN %s: %s",
                    attempt,
                    retries,
                    self.vin,
                    err,
                )
                if attempt == retries:
                    raise
                await asyncio.sleep(5)

        duration = datetime.now() - start_time
        self._last_command_send = datetime.now()

        _LOGGER.info(
            "Command completed for VIN %s in %ss", self.vin, duration.total_seconds()
        )

        return response

    async def async_start_charge(self) -> TeslaAPIResponse:
        """Toggle the charge state of the vehicle."""
        result = await self._async_send_command(
            partial(self._apiClient.async_start_charge, self.vin)
        )

        await self.async_wait_charging_state(ChargingState.CHARGING)

        return result

    async def async_stop_charge(self) -> TeslaAPIResponse:
        """Toggle the charge state of the vehicle."""
        result = await self._async_send_command(
            partial(self._apiClient.async_stop_charge, self.vin)
        )

        await self.async_wait_charging_state(ChargingState.STOPPED)

        return result

    async def async_wait_charging_state(self, state: ChargingState) -> None:
        """Wait for the vehicle to reach a specific charging state."""
        start_time = datetime.now()
        _LOGGER.debug("Waiting for vehicle to reach charging state %s", state)

        while datetime.now() - start_time < timedelta(seconds=30):
            await asyncio.sleep(5)
            await self.async_get_vehicle_data()

            if self.current_data.charge_state.charging_state == state:
                time = datetime.now() - start_time
                _LOGGER.debug(
                    "Vehicle reached charging state %s in %ss",
                    self.current_data.charge_state.charging_state,
                    time.total_seconds(),
                )
                return

        raise TeslaBaseException(
            f"Vehicle did not reach charging state {state} in time"
        )

    async def async_set_charge_limit(self, limit: int) -> TeslaAPIResponse:
        """Set the charge limit of the vehicle."""
        return await self._async_send_command(
            partial(self._apiClient.async_set_charge_limit, self.vin, limit)
        )

    async def async_set_charge_amps(self, amps: int) -> TeslaAPIResponse:
        """Set the charge amps of the vehicle."""
        return await self._async_send_command(
            partial(self._apiClient.async_set_charge_amps, self.vin, amps)
        )

    async def async_lock_doors(self) -> TeslaAPIResponse:
        """Lock the doors of the vehicle."""
        return await self._async_send_command(
            partial(self._apiClient.async_lock_doors, self.vin)
        )

    async def async_unlock_doors(self) -> TeslaAPIResponse:
        """Unlock the doors of the vehicle."""
        return await self._async_send_command(
            partial(self._apiClient.async_unlock_doors, self.vin)
        )
