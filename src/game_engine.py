from constants import ALLOWED_NUM_STOPS_TO_FINISH, HOUR_5PM, HOUR_8PM
from game_data_client import GameDataClient
from game_time import get_est_hours_today
from interfaces import MatchData, MatchStatus, TripData, TripStatus
from game_util import (
    copyTransiterDataToTripData,
    hasTripAssigned,
    isTripComplete,
    isTripOnWayToFirstStation,
    setFirstActualTimeToPredictedTime,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self, verbose=False):
        self.game_data_client = GameDataClient()
        self.transiter_client = TransiterClient()
        self.matchesToUpdate = None
        self.verbose = verbose

    def _isSetUp(self) -> bool:
        return self.matchesToUpdate is not None

    def _maybeAssignTrip(self, trip: TripData) -> None:
        current_trips = self.transiter_client.get_trips(trip["routeId"])
        tripOnWayToFirstStation = next(
            (trip for trip in current_trips if isTripOnWayToFirstStation(trip)), None
        )
        if tripOnWayToFirstStation:
            copyTransiterDataToTripData(tripOnWayToFirstStation, trip)
            setFirstActualTimeToPredictedTime(trip)
            trip["tripStatus"] = TripStatus.ONGOING
            if self.verbose:
                print(f"Assigned route {trip['routeId']} to trip id {trip['tripId']}")

    def _maybeSetNumStopsToWin(self, matchData: MatchData):
        num_stops = [
            len(trip["stops"]) if hasTripAssigned(trip) else None
            for trip in matchData["competingTrips"]
        ]
        if all(num_stops):
            min_num_stops = min(num_stops) - 1
            for allowed_num_stops_to_finish in ALLOWED_NUM_STOPS_TO_FINISH[::-1]:
                if min_num_stops >= allowed_num_stops_to_finish:
                    matchData["numStopsToFinish"] = allowed_num_stops_to_finish
                    if self.verbose:
                        print(
                            f"Set minimum number of stops to finish at {allowed_num_stops_to_finish}"
                        )
                    return

    def setUp(self) -> None:
        self.matchesToUpdate = self.game_data_client.get_matches_for_today()
        for match in self.matchesToUpdate:
            match["matchData"]["matchStatus"] = MatchStatus.ONGOING

    def update(self, bypass_hours=False) -> None:
        est_hours_today = get_est_hours_today()
        if not bypass_hours and est_hours_today < HOUR_5PM:
            return
        elif not bypass_hours and est_hours_today > HOUR_8PM:
            # clean up
            return
        else:
            if not self._isSetUp():
                self.setUp()
            for match in self.matchesToUpdate:
                matchData = match["matchData"]
                if not matchData["matchStatus"] == MatchStatus.ONGOING:
                    continue
                for trip in matchData["competingTrips"]:
                    if isTripComplete(trip):
                        continue
                    if not hasTripAssigned(trip):
                        self._maybeAssignTrip(trip)
                    if trip["tripStatus"] == TripStatus.ONGOING:
                        pass
                if "numStopsToFinish" not in matchData:
                    self._maybeSetNumStopsToWin(matchData)
