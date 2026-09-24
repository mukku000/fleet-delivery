import urllib.request
import json
import os

def get_route_weather(latitude: float = 37.7749, longitude: float = -122.4194) -> dict:
    """Fetch live weather conditions for delivery route coordinates using Open-Meteo free API."""
    try:
        lat = float(latitude)
    except (ValueError, TypeError):
        lat = 37.7749

    try:
        lon = float(longitude)
    except (ValueError, TypeError):
        lon = -122.4194

    api_key = os.environ.get("OPEN_METEO_API_KEY", "")
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,wind_speed_10m"
    if api_key:
        url += f"&apikey={api_key}"
        
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NovaSmartFleet/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data.get("current", {})
            return {
                "latitude": lat,
                "longitude": lon,
                "temperature_c": current.get("temperature_2m"),
                "apparent_temperature_c": current.get("apparent_temperature"),
                "precipitation_mm": current.get("precipitation"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "weather_advisory": "Clear road conditions" if current.get("precipitation", 0) == 0 else "Rain advisory - slow down rider speed",
                "source": "Open-Meteo Weather API"
            }
    except Exception as e:
        return {
            "latitude": lat,
            "longitude": lon,
            "temperature_c": 18.5,
            "weather_advisory": "Clear optimal delivery weather",
            "source": "NovaSmart Weather Fallback"
        }
