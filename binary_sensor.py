"""Binary sensor platform for Tesla Connector."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_sensor import TeslaBaseBinarySensor, TeslaSensorDescription
from .const import BINARY_SENSOR_LOCKED, DOMAIN
from .coordinator import TeslaVehicleCoordinator
from .models.vehicle.vehicle import TeslaVehicle

BINARY_SENSOR_DESCRIPTIONS: dict[str, TeslaSensorDescription] = {
    BINARY_SENSOR_LOCKED: TeslaSensorDescription(
        name="Véhicule verrouillé",
        value_path="vehicle_state.locked",
        device_class=BinarySensorDeviceClass.LOCK,
        on_value="Vérrouillé",
        off_value="Déverrouillé",
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id]["vehicle"]
    binary_sensors = []

    for sensor_key, sensor_description in BINARY_SENSOR_DESCRIPTIONS.items():
        binary_sensors.append(
            TeslaBinarySensor(coordinator, sensor_key, sensor_description)
        )

    async_add_entities(binary_sensors)


class TeslaBinarySensor(TeslaBaseBinarySensor):
    """Representation of a Tesla binary sensor."""

    def __init__(
        self, coordinator: TeslaVehicleCoordinator, key: str, description: dict
    ) -> None:
        """Initialize the Tesla sensor."""
        super().__init__(coordinator, key, description)
        self._vehicle: TeslaVehicle = self._device

    async def _update_state(self, value):
        """Update the state of the sensor."""
        self._attr_is_on = value
