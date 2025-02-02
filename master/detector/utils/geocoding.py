import geocoder
from typing import Optional, Tuple

class Geocoder:
    def __init__(self, update_interval: int = 60):
        """
        Initializes the Geocoder with the specified update interval for location checks.
        :param update_interval: Interval (in seconds) between location updates (default is 60 seconds).
        """
        self.update_interval = update_interval
        self.last_location: Optional[Tuple[float, float]] = None
        self.last_update_time: float = 0

    def get_location(self) -> Optional[Tuple[float, float]]:
        """
        Retrieves the current location based on IP address.
        :return: A tuple containing (latitude, longitude) if successful, else None.
        """
        try:
            g = geocoder.ip('me')
            if g.ok:
                # If geocoding is successful, store and return location
                self.last_location = (g.lat, g.lng)
                self.last_update_time = g.timestamp
                return self.last_location
            else:
                print("Failed to retrieve location.")
                return None
        except Exception as e:
            print(f"Error getting location: {str(e)}")
            return None

    def is_location_fresh(self, current_time: float) -> bool:
        """
        Checks if the location information is still fresh based on the update interval.
        :param current_time: Current time in seconds (e.g., using `time.time()`).
        :return: True if the location information is fresh, otherwise False.
        """
        return (current_time - self.last_update_time) <= self.update_interval

    def get_cached_location(self, current_time: float) -> Optional[Tuple[float, float]]:
        """
        Returns the cached location if it's fresh, otherwise retrieves a new one.
        :param current_time: Current time in seconds (e.g., using `time.time()`).
        :return: A tuple containing (latitude, longitude), or None if no valid location.
        """
        if self.last_location and self.is_location_fresh(current_time):
            return self.last_location
        else:
            return self.get_location()

