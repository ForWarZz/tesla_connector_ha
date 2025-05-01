"""Tesla Connector Sensor Integration."""

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_sensor import TeslaBaseSensor, TeslaSensorDescription
from .const import BINARY_SENSOR_LOCKED, DOMAIN, SENSOR_CHARGING_STATE
from .coordinator import TeslaVehicleCoordinator
from .models.vehicle.vehicle import TeslaVehicle

SWITCH_DESCRIPTIONS: dict[str, TeslaSensorDescription] = {
    BINARY_SENSOR_LOCKED: TeslaSensorDescription(
        name="Véhicule verrouillé",
        value_path="vehicle_state.locked",
        unit=None,
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:lock",
    ),
    SENSOR_CHARGING_STATE: TeslaSensorDescription(
        name="Véhicule en charge",
        value_path="charge_state.charging_state",
        unit=None,
        device_class=SwitchDeviceClass.SWITCH,
        icon="mdi:car-electric",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    switches = []

    for switch_key, switch_description in SWITCH_DESCRIPTIONS.items():
        switches.append(TeslaSwitch(coordinator, switch_key, switch_description))

    async_add_entities(switches)


class TeslaSwitch(TeslaBaseSensor, SwitchEntity):
    """Representation of a Tesla switch."""

    def __init__(
        self,
        coordinator: TeslaVehicleCoordinator,
        key: str,
        description: TeslaSensorDescription,
    ) -> None:
        """Initialize the Tesla switch."""
        super().__init__(coordinator, key, description)
        self._vehicle: TeslaVehicle = self._device

    def _update_state(self, value):
        """Update the state of the switch."""
        self._attr_is_on = (
            value == "Charging" if self._key == SENSOR_CHARGING_STATE else value
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        if self._key == BINARY_SENSOR_LOCKED:
            await self._vehicle.async_lock_doors()
        elif self._key == SENSOR_CHARGING_STATE:
            await self._vehicle.async_start_charge()

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        if self._key == BINARY_SENSOR_LOCKED:
            await self._vehicle.async_unlock_doors()
        elif self._key == SENSOR_CHARGING_STATE:
            await self._vehicle.async_stop_charge()

        await self.coordinator.async_request_refresh()
