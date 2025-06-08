import time
from functools import lru_cache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from app.core.config import settings
from app.db.session import get_db
from sqlalchemy.orm import Session


@lru_cache(maxsize=1)
def get_geolocator() -> Nominatim:
    return Nominatim(user_agent=settings.user_agent)

def get_location_details(lat: float, lon: float) -> dict:
    """
    Retrieves detailed location information for given latitude and longitude coordinates.

    Uses the Nominatim geocoding service to reverse geocode the coordinates and extract
    address components such as city, county, region, state, and country.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.

    Returns:
        dict: A dictionary containing the following keys:
            - city: Name of the city, town, village, hamlet, municipality, or locality (if available).
            - county: Name of the county (if available).
            - region: Name of the state district or region (if available).
            - state: Name of the state (if available).
            - country: Name of the country (if available).
        If the location cannot be determined, returns an empty dictionary.
        If a timeout or geocoding service error occurs, returns a dictionary with all values set to "Timeout".
    """
    geolocator = get_geolocator()
    try:
        location = geolocator.reverse((lat, lon), language='en', timeout=10)
        if not location:
            return {}

        address = location.raw.get("address", {})

        return {
            "city": (
                address.get("city") or address.get("town") or
                address.get("village") or address.get("hamlet") or
                address.get("municipality") or address.get("locality")
            ),
            "county": address.get("county"),
            "region": address.get("state_district") or address.get("region"),
            "state": address.get("state"),
            "country": address.get("country")
        }

    except (GeocoderTimedOut, GeocoderUnavailable):
        return {
            "city": "Timeout",
            "county": "Timeout",
            "region": "Timeout",
            "state": "Timeout",
            "country": "Timeout"
        }
