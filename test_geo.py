import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from app.core.config import settings
from app.db.session import get_db
from app.repositories.post_repo import PostRepository


# Define coordinates list
coordinates_list = [
    (41.3851, 2.1734),                 # Barcelona
    # (47.6577979, 3.3141205),          # Levis, France
    # (36.0490926, 103.8438890),        # Lanzhou, China
    # (-37.7907866, 145.0656676),       # Melbourne, Australia
    # (35.8828227, -97.4475356),        # Oklahoma, USA
    # (40.8016447, -124.1653281),       # California, USA
    # (46.446935159246344, -114.13403455371103),
    # (54.98651107717162, 82.8641811064169)
]

def get_location_details(lat, lon, geolocator):
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

if __name__ == "__main__":
    geolocator = Nominatim(user_agent=settings.user_agent)
    locations = []

    for lat, lon in coordinates_list:
        details = get_location_details(lat, lon, geolocator)
        locations.append(details['city'].lower())
        print(f"→ ({lat}, {lon})")
        print(f"   City:    {details['city']}")
        print(f"   County:  {details['county']}")
        print(f"   Region:  {details['region']}")
        print(f"   State:   {details['state']}")
        print(f"   Country: {details['country']}")
        print("-" * 40)
        time.sleep(1)

    db = next(get_db())
    post_repo = PostRepository(db)
    result = post_repo.get_nearby_sites(locations)
    for item in result:
        print(f"Site ID: {item.id}, Name: {item.name}, Address: {item.address}, City: {item.city}")
