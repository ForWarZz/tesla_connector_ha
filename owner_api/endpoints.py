"""Endpoints used by the Tesla Owner API."""

OWNER_API_BASE_URL = "https://owner-api.teslamotors.com/api/1"

WAKE_UP_ENDPOINT = f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/wake_up"

GET_VEHICLE_DATA_ENDPOINT = f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/vehicle_data"

SET_CHARGING_AMPS_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/set_charging_amps"
)

SET_CHARGE_LIMIT_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/set_charge_limit"
)

CHARGE_START_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/charge_start"
)
CHARGE_STOP_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/charge_stop"
)

UNLOCK_DOORS_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/door_unlock"
)
LOCK_DOORS_ENDPOINT = f"{OWNER_API_BASE_URL}/vehicles/{{vehicle_id}}/command/door_lock"

WALL_CONNECTOR_LIVE_STATUS_ENDPOINT = (
    f"{OWNER_API_BASE_URL}/energy_sites/{{site_id}}/charger_live_status"
)
