"""Tesla Connector Sensor Integration."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfLength,
    UnitOfTime,
    UnitOfElectricPotential,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import utils
from .const import (
    DOMAIN,
    SENSOR_BATTERY_LEVEL,
    SENSOR_BATTERY_RANGE,
    SENSOR_CHARGE_AMPS,
    SENSOR_CHARGE_LIMIT_SOC,
    SENSOR_CHARGING_STATE,
    SENSOR_MINUTES_TO_FULL_CHARGE,
    SENSOR_ODOMETER,
    SENSOR_CHARGER_VOLTAGE,
    SENSOR_CHARGE_CURRENT,
    SENSOR_WALL_CONNECTOR_VIN,
)
from .coordinator import TeslaVehicleCoordinator, TeslaWallConnectorCoordinator

SENSOR_MAPPING = {
    SENSOR_BATTERY_LEVEL: {
        "name": "Niveau batterie",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "icon": "mdi:battery",
        "value_path": "charge_state.battery_level",
    },
    SENSOR_BATTERY_RANGE: {
        "name": "Autonomie batterie",
        "unit": UnitOfLength.KILOMETERS,
        "device_class": SensorDeviceClass.DISTANCE,
        "icon": "mdi:car-electric",
        "value_path": "charge_state.battery_range",
    },
    SENSOR_CHARGE_AMPS: {
        "name": "Ampères de charge",
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:flash",
        "value_path": "charge_state.charge_amps",
    },
    SENSOR_CHARGE_CURRENT: {
        "name": "Courant de charge",
        "unit": UnitOfElectricCurrent.AMPERE,
        "icon": "mdi:flash",
        "value_path": "charge_state.charge_current_request",
    },
    SENSOR_MINUTES_TO_FULL_CHARGE: {
        "name": "Minutes restantes",
        "unit": UnitOfTime.MINUTES,
        "icon": "mdi:clock-outline",
        "value_path": "charge_state.minutes_to_full_charge",
    },
    SENSOR_ODOMETER: {
        "name": "Odomètre",
        "unit": UnitOfLength.KILOMETERS,
        "device_class": SensorDeviceClass.DISTANCE,
        "icon": "mdi:counter",
        "value_path": "vehicle_state.odometer",
        "suggested_display_precision": 1,
    },
    SENSOR_CHARGING_STATE: {
        "name": "État de charge",
        "icon": "mdi:ev-plug-ccs2",
        "value_path": "charge_state.charging_state",
    },
    SENSOR_CHARGE_LIMIT_SOC: {
        "name": "Limite de charge",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "icon": "mdi:battery-charging-80",
        "value_path": "charge_state.charge_limit_soc",
    },
    SENSOR_CHARGER_VOLTAGE: {
        "name": "Tension du chargeur",
        "unit": UnitOfElectricPotential.VOLT,
        "device_class": SensorDeviceClass.VOLTAGE,
        "icon": "mdi:flash",
        "value_path": "charge_state.charger_voltage",
    },
}

WALL_CONNECTOR_SENSOR_MAPPING = {
    SENSOR_WALL_CONNECTOR_VIN: {
        "name": "VIN connecté",
        "icon": "mdi:car-key",
        "value_path": "vin",
    },
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tesla Connector sensors from a config entry."""
    vehicle_coordinator: TeslaVehicleCoordinator = hass.data[DOMAIN][entry.entry_id][
        "vehicle"
    ]
    wall_connector_coordinator: TeslaWallConnectorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]["wall_connector"]

    sensors = []

    for sensor_key, sensor_description in SENSOR_MAPPING.items():
        sensors.append(
            TeslaVehicleSensor(vehicle_coordinator, sensor_key, sensor_description)
        )

    for sensor_key, sensor_description in WALL_CONNECTOR_SENSOR_MAPPING.items():
        sensors.append(
            TeslaWallConnectorSensor(
                wall_connector_coordinator, sensor_key, sensor_description
            )
        )

    async_add_entities(sensors)


class TeslaVehicleSensor(CoordinatorEntity, SensorEntity):
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
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return self._description.get("device_class", None)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._description["name"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._description.get("unit", None)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return self._description["icon"]

    @property
    def suggested_display_precision(self) -> int:
        """Return the suggested display precision."""
        return self._description.get("suggested_display_precision", None)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        value = utils.get_value_from_path(data, self._value_path)
        self._vehicle = self.coordinator.vehicle

        self._attr_native_value = value

        return super()._handle_coordinator_update()


class TeslaWallConnectorSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tesla Wall Connector sensor."""

    def __init__(
        self, coordinator: TeslaWallConnectorCoordinator, key: str, description: dict
    ) -> None:
        """Initialize the Tesla Wall Connector sensor."""
        super().__init__(coordinator)
        self._key = key
        self._description = description
        self._value_path = description["value_path"]
        self._wall_connector = coordinator.wall_connector

    @property
    def unique_id(self) -> str:
        """Return a unique ID for the sensor."""
        return f"{DOMAIN}_{self._wall_connector.wall_connector_id}_{self._key}"

    @property
    def device_info(self) -> dict:
        """Return device information."""
        return self.coordinator.get_wall_connector_device_info()

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return self._description.get("device_class", None)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._description["name"]

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._description.get("unit", None)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return self._description["icon"]

    @property
    def suggested_display_precision(self) -> int:
        """Return the suggested display precision."""
        return self._description.get("suggested_display_precision", None)

    @callback
    def _handle_coordinator_update(self):
        """Handle updated data from the coordinator."""
        data = self.coordinator.data
        value = utils.get_value_from_path(data, self._value_path)
        self._wall_connector = self.coordinator.wall_connector

        self._attr_native_value = value

        return super()._handle_coordinator_update()
