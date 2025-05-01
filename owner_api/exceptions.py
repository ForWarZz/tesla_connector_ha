"""Tesla API exceptions module."""

from homeassistant.exceptions import HomeAssistantError


class TeslaBaseException(HomeAssistantError):
    """Base exception for all Tesla API errors."""


class TeslaTokenException(TeslaBaseException):
    """Exception raised for token-related errors."""
