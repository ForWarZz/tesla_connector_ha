"""Tesla device model."""

from ..owner_api.client import TeslaAPIClient


class TeslaBaseDevice:
    """Base class for Tesla devices."""

    def __init__(self, device_id: str, apiClient: TeslaAPIClient) -> None:
        """Initialize the device with an ID and name."""
        self._device_id = device_id
        self._apiClient = apiClient

    @property
    def device_id(self) -> str:
        """Return the device ID."""
        return self._device_id
