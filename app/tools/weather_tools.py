import urllib.request
import json
import os

def get_route_weather(latitude: float = 37.7749, longitude: float = -122.4194) -> dict:
    """Fetch live weather conditions for delivery route coordinates using Open-Meteo free API."""
    # Read custom API key from environment variable if configured (otherwise free endpoint used)
    api_key = os.environ.get("OPEN_METEO_API_KEY", "")
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,wind_speed_10m"
    if api_key:
        url += f"&apikey={api_key}"
        
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VelocityTrack/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            current = data.get("current", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature_c": current.get("temperature_2m"),
                "apparent_temperature_c": current.get("apparent_temperature"),
                "precipitation_mm": current.get("precipitation"),
                "wind_speed_kmh": current.get("wind_speed_10m"),
                "humidity_percent": current.get("relative_humidity_2m"),
                "source": "Open-Meteo Public API"
            }
    except Exception as e:
        return {
            "error": f"Failed to fetch route weather: {str(e)}",
            "latitude": latitude,
            "longitude": longitude
        }
