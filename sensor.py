"""Tesla Connector Sensor Integration."""

from config.custom_components.tesla_connector.models.vehicle.vehicle import TeslaVehicle
from config.custom_components.tesla_connector.models.wall_connector.wall_connector import (
    WallConnector,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_sensor import TeslaBaseSensor, TeslaSensorDescription
from .const import (
    DOMAIN,
    SENSOR_BATTERY_LEVEL,
    SENSOR_BATTERY_RANGE,
    SENSOR_CHARGE_AMPS,
    SENSOR_CHARGE_CURRENT,
    SENSOR_CHARGE_LIMIT_SOC,
    SENSOR_CHARGER_VOLTAGE,
    SENSOR_CHARGING_STATE,
    SENSOR_MINUTES_TO_FULL_CHARGE,
    SENSOR_ODOMETER,
    SENSOR_WALL_CONNECTOR_SESSION_CHARGE,
    SENSOR_WALL_CONNECTOR_VIN,
)
from .coordinator import TeslaVehicleCoordinator, TeslaWallConnectorCoordinator

SENSOR_DESCRIPTIONS: dict[str, TeslaSensorDescription] = {
    SENSOR_BATTERY_LEVEL: TeslaSensorDescription(
        name="Niveau batterie",
        value_path="charge_state.battery_level",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery",
    ),
    SENSOR_BATTERY_RANGE: TeslaSensorDescription(
        name="Autonomie batterie",
        value_path="charge_state.battery_range",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        icon="mdi:car-electric",
    ),
    SENSOR_CHARGE_AMPS: TeslaSensorDescription(
        name="Ampères de charge voulus",
        value_path="charge_state.charge_amps",
        unit=UnitOfElectricCurrent.AMPERE,
        icon="mdi:flash",
    ),
    SENSOR_CHARGE_CURRENT: TeslaSensorDescription(
        name="Ampères de charge",
        value_path="charge_state.charge_current_request",
        unit=UnitOfElectricCurrent.AMPERE,
        icon="mdi:flash",
    ),
    SENSOR_MINUTES_TO_FULL_CHARGE: TeslaSensorDescription(
        name="Minutes restantes",
        value_path="charge_state.minutes_to_full_charge",
        unit=UnitOfTime.MINUTES,
        icon="mdi:clock-outline",
    ),
    SENSOR_ODOMETER: TeslaSensorDescription(
        name="Odomètre",
        value_path="vehicle_state.odometer",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        icon="mdi:counter",
    ),
    SENSOR_CHARGING_STATE: TeslaSensorDescription(
        name="État de charge",
        value_path="charge_state.charging_state",
        icon="mdi:ev-plug-ccs2",
    ),
    SENSOR_CHARGE_LIMIT_SOC: TeslaSensorDescription(
        name="Limite de charge",
        value_path="charge_state.charge_limit_soc",
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        icon="mdi:battery-charging-80",
    ),
    SENSOR_CHARGER_VOLTAGE: TeslaSensorDescription(
        name="Tension du chargeur",
        value_path="charge_state.charger_voltage",
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:flash",
    ),
}

WALL_CONNECTOR_SENSOR_DESCRIPTIONS: dict[str, TeslaSensorDescription] = {
    SENSOR_WALL_CONNECTOR_VIN: TeslaSensorDescription(
        name="VIN connecté",
        value_path="vin",
        icon="mdi:car-key",
    ),
    SENSOR_WALL_CONNECTOR_SESSION_CHARGE: TeslaSensorDescription(
        name="Charge de la session",
        value_path="wall_connector_power",
        unit=UnitOfEnergy.WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:car-electric",
    ),
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

    for sensor_key, sensor_description in SENSOR_DESCRIPTIONS.items():
        sensors.append(
            TeslaVehicleSensor(vehicle_coordinator, sensor_key, sensor_description)
        )

    for sensor_key, sensor_description in WALL_CONNECTOR_SENSOR_DESCRIPTIONS.items():
        sensors.append(
            TeslaWallConnectorSensor(
                wall_connector_coordinator, sensor_key, sensor_description
            )
        )

    async_add_entities(sensors)


class TeslaVehicleSensor(TeslaBaseSensor, SensorEntity):
    """Representation of a Tesla vehicle sensor."""

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
        """Update the state of the sensor."""
        self._attr_native_value = value


class TeslaWallConnectorSensor(TeslaBaseSensor, SensorEntity):
    """Representation of a Tesla Wall Connector sensor."""

    def __init__(
        self,
        coordinator: TeslaWallConnectorCoordinator,
        key: str,
        description: TeslaSensorDescription,
    ) -> None:
        """Initialize the Tesla Wall Connector sensor."""
        super().__init__(coordinator, key, description)
        self._wall_connector: WallConnector = self._device

    def _update_state(self, value):
        """Update the state of the sensor."""
        self._attr_native_value = value
