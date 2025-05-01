"""Models for Tesla API responses."""


class TeslaAPIResponse:
    """Base class for Tesla API responses."""

    def __init__(self, response: dict) -> None:
        """Initialize the response with the given data."""
        self._result = response.get("result", False)
        self._reason = response.get("reason", "")
        self._data = response

    @property
    def result(self) -> bool:
        """Return the result of the API call."""
        return self._result

    @property
    def reason(self) -> str:
        """Return the reason for the API call result."""
        return self._reason

    @property
    def data(self) -> dict:
        """Return the data from the API response."""
        return self._data
