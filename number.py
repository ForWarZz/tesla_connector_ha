"""Tesla Connector Number Entity."""

from config.custom_components.tesla_connector.coordinator import TeslaVehicleCoordinator
from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import utils
from .const import DOMAIN, SENSOR_CHARGE_LIMIT_SOC, SENSOR_CHARGE_AMPS

NUMBER_MAPPING = {
    SENSOR_CHARGE_LIMIT_SOC: {
        "name": "Limite de charge",
        "unit": PERCENTAGE,
        "device_class": NumberDeviceClass.BATTERY,
        "icon": "mdi:battery",
        "value_path": "charge_state.charge_limit_soc",
        "min_value": 0,
        "max_value": 100,
        "step": 5,
    },
    SENSOR_CHARGE_AMPS: {
        "name": "Ampères de charge",
        "unit": None,
        "device_class": NumberDeviceClass.CURRENT,
        "icon": "mdi:flash",
        "value_path": "charge_state.charge_amps",
        "min_value": 1,
        "max_value": 32,
        "step": 1,
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    numbers = []

    for number_key, number_description in NUMBER_MAPPING.items():
        numbers.append(TeslaNumber(coordinator, number_key, number_description))

    async_add_entities(numbers)


class TeslaNumber(CoordinatorEntity, NumberEntity):
    """Entity to set Tesla charge limit."""

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
    def name(self) -> str:
        """Return the name of the entity."""
        return self._description["name"]

    @property
    def native_min_value(self) -> int:
        """Return the minimum value of the entity."""
        return self._description["min_value"]

    @property
    def native_max_value(self) -> int:
        """Return the maximum value of the entity."""
        return self._description["max_value"]

    @property
    def native_step(self) -> int:
        """Return the step value of the entity."""
        return self._description["step"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._description["unit"]

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self.coordinator.get_vehicle_device_info()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        value = utils.get_value_from_path(data, self._value_path)
        self._vehicle = self.coordinator.vehicle

        self._attr_native_value = value

        return super()._handle_coordinator_update()

    async def async_set_native_value(self, value: float) -> None:
        """Set new charge limit."""
        if self._key == SENSOR_CHARGE_LIMIT_SOC:
            await self._vehicle.async_set_charge_limit(int(value))
        elif self._key == SENSOR_CHARGE_AMPS:
            await self._vehicle.async_set_charge_amps(int(value))

        await self.coordinator.async_request_refresh()
