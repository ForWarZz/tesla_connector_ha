"""Tesla Connector Sensor Integration."""

from homeassistant.components.switch import SwitchEntity, SwitchDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import utils
from .const import DOMAIN, BINARY_SENSOR_LOCKED, SENSOR_CHARGING_STATE
from .coordinator import TeslaVehicleCoordinator

SWITCH_MAPPING = {
    BINARY_SENSOR_LOCKED: {
        "name": "Véhicule verrouillé",
        "unit": None,
        "device_class": SwitchDeviceClass.SWITCH,
        "icon": "mdi:lock",
        "value_path": "vehicle_state.locked",
    },
    SENSOR_CHARGING_STATE: {
        "name": "Véhicule en charge",
        "unit": None,
        "device_class": SwitchDeviceClass.SWITCH,
        "icon": "mdi:car-electric",
        "value_path": "charge_state.charging_state",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    switches = []

    for switch_key, switch_description in SWITCH_MAPPING.items():
        switches.append(TeslaSwitch(coordinator, switch_key, switch_description))

    async_add_entities(switches)


class TeslaSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Tesla sensor."""

    def __init__(
        self, coordinator: TeslaVehicleCoordinator, key: str, description: dict
    ) -> None:
        """Initialize the Tesla sensor."""
        super().__init__(coordinator)
        self._key = key
        self._description = description
        self._value_path = description["value_path"]
        self._vehicle = coordinator.vehicle

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._vehicle.vin}_{self._key}"

    @property
    def device_info(self) -> dict:
        """Return device information."""
        return self.coordinator.get_vehicle_device_info()

    @property
    def device_class(self) -> SwitchDeviceClass:
        """Return the device class of the sensor."""
        return self._description["device_class"]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._description["name"]

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return self._description["icon"]

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

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        value = utils.get_value_from_path(data, self._value_path)
        self._vehicle = self.coordinator.vehicle

        if self._key == SENSOR_CHARGING_STATE:
            self._attr_is_on = value == "Charging"
        else:
            self._attr_is_on = value

        return super()._handle_coordinator_update()
