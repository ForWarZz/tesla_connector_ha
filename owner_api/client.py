"""Client for interacting with the Tesla Owner API."""

import asyncio
from datetime import datetime, timedelta
import logging

import aiohttp

from ..const import OAUTH2_CLIENT_ID, OAUTH2_TOKEN, WAKE_UP_TIMEOUT
from .api_response import TeslaAPIResponse
from .endpoints import (
    CHARGE_START_ENDPOINT,
    CHARGE_STOP_ENDPOINT,
    GET_VEHICLE_DATA_ENDPOINT,
    LOCK_DOORS_ENDPOINT,
    SET_CHARGE_LIMIT_ENDPOINT,
    SET_CHARGING_AMPS_ENDPOINT,
    UNLOCK_DOORS_ENDPOINT,
    WAKE_UP_ENDPOINT,
    WALL_CONNECTOR_LIVE_STATUS_ENDPOINT,
)
from .exceptions import TeslaTokenException

_LOGGER = logging.getLogger(__name__)


class TeslaAPIClient:
    """Client for Owner Tesla API."""

    def __init__(self, refresh_token: str) -> None:
        """Initialize the Tesla API client with authentication."""
        self._refresh_token = refresh_token
        self._access_token = None

    # AUTHENTICATION
    async def _async_request(
        self, endpoint: str, method: str = "GET", **kwargs
    ) -> TeslaAPIResponse:
        """Make a request to the Tesla Owner API."""

        if not self._access_token:
            await self._async_refresh_token()

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Tesla-User-Agent": "TeslaApp/4.43.5-3224/eb0e53992e/ios/18.4.1",
        }
        kwargs["headers"] = headers

        async with (
            aiohttp.ClientSession() as session,
            session.request(method, endpoint, **kwargs) as response,
        ):
            if response.status == 401:
                _LOGGER.debug("Access token expired, refreshing token")

                await self._async_refresh_token()
                headers["Authorization"] = f"Bearer {self._access_token}"

                return await self._async_request(endpoint, method, **kwargs)

            response.raise_for_status()
            data = await response.json()

            _LOGGER.debug("Response from Tesla API: %s", data)

            return TeslaAPIResponse(data.get("response", data))

    async def _async_refresh_token(self) -> None:
        """Refresh the access token if needed."""
        payload = {
            "grant_type": "refresh_token",
            "client_id": OAUTH2_CLIENT_ID,
            "refresh_token": self._refresh_token,
            "scope": "openid email offline_access",
        }

        headers = {
            "Content-Type": "application/json",
        }

        _LOGGER.debug("Refreshing Tesla access token")

        async with (
            aiohttp.ClientSession() as session,
            session.post(OAUTH2_TOKEN, json=payload, headers=headers) as response,
        ):
            if response.status == 401:
                _LOGGER.error("Failed to refresh access token: %s", response)
                raise TeslaTokenException("Failed to refresh access token")
            response.raise_for_status()
            resp = await response.json()

            _LOGGER.debug("Token refreshed")
            self._access_token = resp["access_token"]
            self._refresh_token = resp["refresh_token"]

    # GET VEHICLE DATA
    async def async_get_vehicle_data(self, vehicle_id: str) -> TeslaAPIResponse:
        """Get vehicle data."""
        _LOGGER.debug("Getting vehicle data for VIN %s", vehicle_id)

        endpoint = GET_VEHICLE_DATA_ENDPOINT.format(vehicle_id=vehicle_id)
        return await self._async_request(endpoint)

    # VEHICLE COMMANDS
    async def async_wake_up_car(
        self, vehicle_id: str, timeout=WAKE_UP_TIMEOUT
    ) -> TeslaAPIResponse:
        """Wake up the car and wait until it is online."""
        _LOGGER.debug("Waking up the car with VIN %s", vehicle_id)

        endpoint = WAKE_UP_ENDPOINT.format(vehicle_id=vehicle_id)
        timeout = timedelta(seconds=timeout)
        start_time = datetime.now()

        while datetime.now() - start_time < timeout:
            response = await self._async_request(endpoint, method="POST")
            state = response.data.get("state")

            if state == "online":
                _LOGGER.debug("Car is now online, waiting for 2 seconds to stabilize")
                await asyncio.sleep(2)
                return response

            _LOGGER.debug("Car state is %s, retrying", state)
            await asyncio.sleep(2)

        _LOGGER.debug("Timeout reached while waiting for car to wake up")
        raise TimeoutError("Car did not wake up in time. Check the vehicle connection.")

    async def async_start_charge(self, vehicle_id: str) -> TeslaAPIResponse:
        """Toggle charge state."""
        _LOGGER.debug("Starting charge for VIN %s", vehicle_id)

        endpoint = CHARGE_START_ENDPOINT.format(vehicle_id=vehicle_id)
        return await self._async_request(endpoint, method="POST")

    async def async_stop_charge(self, vehicle_id: str) -> TeslaAPIResponse:
        """Toggle charge state."""
        _LOGGER.debug("Stopping charge for VIN %s", vehicle_id)

        endpoint = CHARGE_STOP_ENDPOINT.format(vehicle_id=vehicle_id)
        return await self._async_request(endpoint, method="POST")

    async def async_set_charge_amps(
        self, vehicle_id: str, amps: int
    ) -> TeslaAPIResponse:
        """Set the charge amps."""
        _LOGGER.debug("Setting charge amps to %s", amps)

        endpoint = SET_CHARGING_AMPS_ENDPOINT.format(vehicle_id=vehicle_id)
        payload = {"charging_amps": amps}

        return await self._async_request(endpoint, method="POST", json=payload)

    async def async_set_charge_limit(
        self, vehicle_id: str, percentage: int
    ) -> TeslaAPIResponse:
        """Set the charge limit."""
        _LOGGER.debug("Setting charge limit to %s", percentage)

        endpoint = SET_CHARGE_LIMIT_ENDPOINT.format(vehicle_id=vehicle_id)
        payload = {"percent": percentage}

        return await self._async_request(endpoint, method="POST", json=payload)

    async def async_unlock_doors(self, vehicle_id: str) -> TeslaAPIResponse:
        """Unlock the doors."""
        _LOGGER.debug("Unlocking doors for VIN %s", vehicle_id)

        endpoint = UNLOCK_DOORS_ENDPOINT.format(vehicle_id=vehicle_id)
        return await self._async_request(endpoint, method="POST")

    async def async_lock_doors(self, vehicle_id: str) -> TeslaAPIResponse:
        """Lock the doors."""
        _LOGGER.debug("Locking doors for VIN %s", vehicle_id)

        endpoint = LOCK_DOORS_ENDPOINT.format(vehicle_id=vehicle_id)
        return await self._async_request(endpoint, method="POST")

    # WALL CONNECTOR
    async def async_get_wall_connector_status(self, site_id: str) -> TeslaAPIResponse:
        """Get the status of the wall connector."""
        _LOGGER.debug("Getting wall connector status for site %s", site_id)

        endpoint = WALL_CONNECTOR_LIVE_STATUS_ENDPOINT.format(site_id=site_id)
        return await self._async_request(endpoint)
