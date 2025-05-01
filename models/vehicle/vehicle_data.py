"""Vehicle data model for Tesla vehicles."""


class ChargingState:
    """Class to hold charging state."""

    NOT_CHARGING = "NotCharging"
    CHARGING = "Charging"
    COMPLETE = "Complete"
    SUSPENDED = "Suspended"
    DISCONNECTED = "Disconnected"


class VehicleChargeState:
    """Class to hold vehicle charge state."""

    def __init__(self, data: dict) -> None:
        """Initialize the vehicle charge state with the given data."""
        self.battery_level = data.get("battery_level", 0)
        self.battery_range = data.get("battery_range", 0)
        self.charge_amps = data.get("charge_amps", 0)
        self.charger_actual_current = data.get(
            "charger_actual_current", self.charge_amps
        )
        self.charge_current_request = data.get("charge_current_request", 0)
        self.charge_current_request_max = data.get("charge_current_request_max", 0)
        self.charge_limit_soc = data.get("charge_limit_soc", 0)
        self.minutes_to_full_charge = data.get("minutes_to_full_charge", 0)
        self.charging_state = data.get("charging_state", ChargingState.NOT_CHARGING)
        self.charger_voltage = data.get("charger_voltage", 240)


class VehicleState:
    """Class to hold vehicle state."""

    def __init__(self, data: dict) -> None:
        """Initialize the vehicle state with the given data."""
        self.odometer = int(data.get("odometer", 0))
        self.locked = data.get("locked", False)


class VehicleData:
    """Class to hold vehicle data."""

    def __init__(self, data: dict) -> None:
        """Initialize the vehicle data with the given data."""
        self.state = data.get("state", "offline")
        self.charge_state = VehicleChargeState(data.get("charge_state", {}))
        self.vehicle_state = VehicleState(data.get("vehicle_state", {}))
