"""Tesla Connector Number Entity."""

from homeassistant.components.number import NumberDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_sensor import TeslaBaseNumber, TeslaSensorDescription
from .const import DOMAIN, SENSOR_CHARGE_AMPS, SENSOR_CHARGE_LIMIT_SOC
from .coordinator import TeslaVehicleCoordinator
from .models.vehicle.vehicle import TeslaVehicle

NUMBER_DESCRIPTIONS: dict[str, TeslaSensorDescription] = {
    SENSOR_CHARGE_LIMIT_SOC: TeslaSensorDescription(
        name="Limite de charge",
        value_path="charge_state.charge_limit_soc",
        unit=PERCENTAGE,
        device_class=NumberDeviceClass.BATTERY,
        icon="mdi:battery",
        min_value=0,
        max_value=100,
        step=5,
    ),
    SENSOR_CHARGE_AMPS: TeslaSensorDescription(
        name="Ampères de charge",
        value_path="charge_state.charge_amps",
        unit=None,
        device_class=NumberDeviceClass.CURRENT,
        icon="mdi:flash",
        min_value=1,
        max_value=32,
        step=1,
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    numbers = []

    for number_key, number_description in NUMBER_DESCRIPTIONS.items():
        numbers.append(TeslaNumber(coordinator, number_key, number_description))

    async_add_entities(numbers)


class TeslaNumber(TeslaBaseNumber):
    """Entity to set Tesla charge limit."""

    def __init__(
        self,
        coordinator: TeslaVehicleCoordinator,
        key: str,
        description: TeslaSensorDescription,
    ) -> None:
        """Initialize the Tesla sensor."""
        super().__init__(coordinator, key, description)
        self._vehicle: TeslaVehicle = self._device

    def _update_state(self, value):
        """Update the state of the number entity."""
        self._attr_native_value = value

    async def async_set_native_value(self, value: float) -> None:
        """Set new charge limit."""
        if self._key == SENSOR_CHARGE_LIMIT_SOC:
            await self._vehicle.async_set_charge_limit(int(value))
        elif self._key == SENSOR_CHARGE_AMPS:
            await self._vehicle.async_set_charge_amps(int(value))

        await self.coordinator.async_request_refresh()
