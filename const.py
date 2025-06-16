"""Constants for the Tesla Connector integration."""

from homeassistant.const import Platform as PLATFORM

DOMAIN = "tesla_connector"

PLATFORMS = [
    PLATFORM.BINARY_SENSOR,
    PLATFORM.NUMBER,
    PLATFORM.SENSOR,
    PLATFORM.SWITCH,
]

OAUTH2_TOKEN = "https://auth.tesla.com/oauth2/v3/token"
OAUTH2_CLIENT_ID = "ownerapi"

CONF_REFRESH_TOKEN = "refresh_token"
CONF_VIN = "vin"
CONF_WALL_CONNECTOR_ID = "wall_connector_id"

UPDATE_INTERVAL = 60  # seconds
COORDINATOR_TIMEOUT = 10  # seconds
WAKE_UP_TIMEOUT = 30  # seconds
WAKE_UP_THRESHOLD = 30  # minutes
COMMAND_TIMEOUT = 10  # seconds
SLEEP_THRESHOLD = 15  # minutes

# Sensor Types
SENSOR_BATTERY_LEVEL = "battery_level"
SENSOR_BATTERY_RANGE = "battery_range"
SENSOR_CHARGE_AMPS = "charge_amps"
SENSOR_CHARGE_CURRENT = "charge_current"
SENSOR_CHARGE_LIMIT_SOC = "charge_limit_soc"
SENSOR_MINUTES_TO_FULL_CHARGE = "minutes_to_full_charge"
SENSOR_CHARGING_STATE = "charging_state"
SENSOR_ODOMETER = "odometer"
SENSOR_CHARGER_VOLTAGE = "charger_voltage"
SENSOR_CHARGE_ENERGY_ADDED = "charge_energy_added"
SENSOR_VEHICLE_STATE = "state"

SENSOR_WALL_CONNECTOR_VIN = "vin"

# Binary Sensor Types
BINARY_SENSOR_LOCKED = "locked"

# Switch Types
# SWITCH_LOCK_DOORS = "lock_doors"
# SWITCH_CHARGE_STATE = "charge_state"

# # Number Types
# NUMBER_CHARGE_LIMIT_SOC = "charge_limit_soc"
# NUMBER_CHARGE_AMPS = "charge_amps"
