"""Wall Connector models."""

from config.custom_components.tesla_connector.models.wall_connector.wall_connector_data import (
    WallConnectorData,
)
from config.custom_components.tesla_connector.owner_api.client import TeslaAPIClient


class WallConnector:
    """Representation of a Tesla Wall Connector."""

    def __init__(self, wall_connector_id: str, apiClient: TeslaAPIClient) -> None:
        """Initialize the Wall Connector."""
        self._wall_connector_id = wall_connector_id
        self._apiClient = apiClient
        self._current_data = None

    @property
    def wall_connector_id(self) -> str:
        """Return the Wall Connector ID."""
        return self._wall_connector_id

    @property
    def current_data(self) -> WallConnectorData:
        """Return the current data of the Wall Connector (cached)."""
        return self._current_data

    async def async_get_wall_connector_data(self) -> dict:
        """Get Wall Connector data."""
        wall_connector_data = await self._apiClient.async_get_wall_connector_status(
            self._wall_connector_id
        )
        self._current_data = WallConnectorData(wall_connector_data.data)

        return self._current_data
