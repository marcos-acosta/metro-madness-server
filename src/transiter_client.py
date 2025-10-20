import requests

from constants import TRANSITER_URL

from interface import RouteId
from url_util import build_url


class TransiterClient:
    def __init__(self, verbose: bool = False):
        self.transiter_base_url = TRANSITER_URL
        self.system = "us-ny-subway"
        self.verbose = verbose

    def get_subway_url(self) -> str:
        return build_url(self.transiter_base_url, "systems", self.system)

    def get_trips(self, route_id: RouteId):
        trips_url = build_url(self.get_subway_url(), "routes", route_id, "trips")
        try:
            response = requests.get(trips_url)
            response.raise_for_status()
            return response.json()["trips"]
        except Exception as e:
            if self.verbose:
                print(f"Error calling Transiter: {e}")
            return None

    def get_trip(self, route_id: RouteId, trip_id: str):
        trips_url = build_url(
            self.get_subway_url(), "routes", route_id, "trips", trip_id
        )
        try:
            response = requests.get(trips_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if self.verbose:
                print(f"Error calling Transiter: {e}")
            return None
