"""Binary sensor platform for Tesla Connector."""

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import utils
from .const import BINARY_SENSOR_LOCKED, DOMAIN
from .coordinator import TeslaVehicleCoordinator

BINARY_SENSOR_MAPPING = {
    BINARY_SENSOR_LOCKED: {
        "name": "Véhicule verrouillé",
        "on_value": "Vérrouillé",
        "off_value": "Déverrouillé",
        "device_class": BinarySensorDeviceClass.LOCK,
        "value_path": "vehicle_state.locked",
    }
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    binary_sensors = []

    for sensor_key, sensor_description in BINARY_SENSOR_MAPPING.items():
        binary_sensors.append(
            TeslaBinarySensor(coordinator, sensor_key, sensor_description)
        )

    async_add_entities(binary_sensors)


class TeslaBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Tesla binary sensor."""

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
    def state(self) -> str:
        """Return the state of the binary sensor in French."""
        return (
            self._description["on_value"]
            if self.is_on
            else self._description["off_value"]
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._vehicle.vin}_{self._key}"

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        self._vehicle = self._vehicle
        self._attr_is_on = utils.get_value_from_path(data, self._value_path)

        return super()._handle_coordinator_update()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return self.coordinator.get_vehicle_device_info()

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        """Return the device class of the sensor."""
        return self._description["device_class"]

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._description["name"]
