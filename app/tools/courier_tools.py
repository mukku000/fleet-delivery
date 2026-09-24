def check_courier_telemetry(courier_name: str) -> dict:
    """Fetch live telemetry for an active courier (e.g. 'Elena Rostova', 'Marcus Vance', 'Kai Chen'), returning battery level, vehicle type, current speed, and GPS coordinates."""
    courier_data = {
        "Elena Rostova": {
            "courier_id": "CR-101",
            "vehicle": "E-Bike",
            "battery_percent": 88,
            "current_speed_kmh": 22.4,
            "lat": 37.7891,
            "lng": -122.4014,
            "status": "Active - In Transit"
        },
        "Marcus Vance": {
            "courier_id": "CR-102",
            "vehicle": "Cargo Scooter",
            "battery_percent": 42,
            "current_speed_kmh": 18.0,
            "lat": 37.7831,
            "lng": -122.4182,
            "status": "Active - Picked Up Order"
        },
        "Kai Chen": {
            "courier_id": "CR-103",
            "vehicle": "EV Pod",
            "battery_percent": 95,
            "current_speed_kmh": 0.0,
            "lat": 37.7915,
            "lng": -122.3980,
            "status": "Idle - At Hub 03"
        }
    }
    
    info = courier_data.get(courier_name)
    if not info:
        return {
            "courier_name": courier_name,
            "status": "Active",
            "vehicle": "E-Bike",
            "battery_percent": 75,
            "current_speed_kmh": 20.0,
            "lat": 37.7850,
            "lng": -122.4050,
            "note": "Default telemetry profile returned for courier."
        }
    return info
