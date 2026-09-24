import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

# Load environment variables from standard locations
load_dotenv()
_app_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(_app_env):
    load_dotenv(_app_env)

def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key or key == "PASTE_KEY_HERE":
        for path in [
            _app_env,
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        ]:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        for line in f:
                            if line.startswith("GOOGLE_MAPS_API_KEY="):
                                val = line.strip().split("=", 1)[1].strip('"').strip("'")
                                if val and val != "PASTE_KEY_HERE":
                                    return val
                except Exception:
                    pass
    return key or ""

def geocode_address(address: str) -> dict:
    """Geocode an address or street name into geographic coordinates (latitude, longitude) using the Google Maps Geocoding API."""
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set or contains placeholder value.", "address": address}

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "VelocityTrack/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            status = data.get("status")
            if status != "OK" or not data.get("results"):
                return {"error": f"Geocoding failed with status: {status}", "address": address}
            
            result = data["results"][0]
            geometry = result.get("geometry", {})
            location = geometry.get("location", {})
            
            return {
                "address": address,
                "formatted_address": result.get("formatted_address"),
                "location": {
                    "latitude": location.get("lat"),
                    "longitude": location.get("lng")
                },
                "place_id": result.get("place_id")
            }
    except Exception as e:
        return {"error": f"Failed to call Geocoding API: {str(e)}", "address": address}


def find_nearby_places(latitude: float, longitude: float, place_type: str = "restaurant", radius_meters: float = 1000.0) -> list[dict]:
    """Find nearby points of interest (e.g. 'restaurant', 'cafe', 'grocery_store') near a location using the Google Places API (New)."""
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return [{"error": "GOOGLE_MAPS_API_KEY environment variable is not set or contains placeholder value."}]

    url = "https://places.googleapis.com/v1/places:searchNearby"
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.primaryType"
    }

    body = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius_meters
            }
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            places = data.get("places", [])
            
            results = []
            for place in places:
                display_name = place.get("displayName", {}).get("text", "")
                formatted_address = place.get("formattedAddress", "")
                loc = place.get("location", {})
                primary_type = place.get("primaryType", "")
                
                results.append({
                    "name": display_name,
                    "address": formatted_address,
                    "location": {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude")
                    },
                    "type": primary_type
                })
            
            return results
    except Exception as e:
        return [{"error": f"Failed to call Places API (New): {str(e)}"}]


def generate_route_map(origin_address: str = "Downtown Express Hub #1, San Francisco, CA", destination_address: str = "120 Market St, San Francisco, CA") -> dict:
    """Generate a visual route map image URL between a dispatch hub and a delivery destination using Google Maps Static API."""
    api_key = _get_api_key()
    if not api_key or api_key == "PASTE_KEY_HERE":
        return {"error": "GOOGLE_MAPS_API_KEY environment variable is not set or contains placeholder value."}

    encoded_origin = urllib.parse.quote(origin_address)
    encoded_dest = urllib.parse.quote(destination_address)
    
    map_url = (
        f"https://maps.googleapis.com/maps/api/staticmap?"
        f"size=600x350&scale=2&maptype=roadmap&"
        f"markers=color:blue%7Clabel:H%7C{encoded_origin}&"
        f"markers=color:red%7Clabel:D%7C{encoded_dest}&"
        f"path=color:0x4f46e5ff%7Cweight:5%7C{encoded_origin}%7C{encoded_dest}&"
        f"key={api_key}"
    )

    return {
        "map_url": map_url,
        "origin": origin_address,
        "destination": destination_address,
        "description": f"Delivery Route Map from {origin_address} to {destination_address}"
    }
