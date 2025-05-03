"""Wall Connector models."""


class WallConnectorData:
    """Representation of Wall Connector data."""

    def __init__(self, response: dict) -> None:
        """Initialize the Wall Connector data."""

        self._data = (
            response.get("wall_connectors", [])[0]
            if response.get("wall_connectors")
            else {}
        )

        self.vin = self._data.get("vin", "")
