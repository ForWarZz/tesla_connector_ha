"""Base class for Tesla sensors."""

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import utils
from .const import DOMAIN
from .coordinator import TeslaBaseCoordinator


@dataclass
class TeslaSensorDescription:
    """Class to describe a Tesla sensor."""

    name: str
    value_path: str
    unit: str | None = None
    device_class: str | None = None
    icon: str | None = None
    suggested_display_precision: int | None = None
    min_value: int | None = None
    max_value: int | None = None
    step: int | None = None
    on_value: str | None = None
    off_value: str | None = None


class TeslaBaseSensor(CoordinatorEntity):
    """Base class for Tesla sensors."""

    def __init__(
        self,
        coordinator: TeslaBaseCoordinator,
        key: str,
        description: TeslaSensorDescription,
    ) -> None:
        """Initialize the Tesla sensor."""
        super().__init__(coordinator)
        self._key = key
        self._description = description
        self._value_path = description.value_path
        self._device = coordinator.device

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._device.device_id}_{self._key}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._description.name

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return self._description.icon

    @property
    def device_info(self) -> dict:
        """Return device information."""
        return self.coordinator.get_device_info()

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested display precision."""
        return self._description.suggested_display_precision

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement."""
        return self._description.unit

    @property
    def device_class(self) -> str | None:
        """Return the device class of the sensor."""
        return self._description.device_class

    def _get_value(self, data):
        """Extract value from data using the value path."""
        return utils.get_value_from_path(data, self._value_path)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        self._device = self.coordinator.device
        self._update_state(self._get_value(data))
        super()._handle_coordinator_update()

    def _update_state(self, value):
        """Update the state of the sensor."""
        raise NotImplementedError("Must be implemented by subclasses.")


class TeslaBaseBinarySensor(TeslaBaseSensor, BinarySensorEntity):
    """Base class for Tesla switches."""

    @property
    def state(self) -> str:
        """Return the state of the binary sensor."""
        return self._description.on_value if self.is_on else self._description.off_value


class TeslaBaseNumber(TeslaBaseSensor, NumberEntity):
    """Base class for Tesla number entities."""

    @property
    def native_min_value(self) -> int | None:
        """Return the minimum value of the sensor."""
        return self._description.min_value

    @property
    def native_max_value(self) -> int | None:
        """Return the maximum value of the sensor."""
        return self._description.max_value

    @property
    def native_step(self) -> int | None:
        """Return the step value of the sensor."""
        return self._description.step
