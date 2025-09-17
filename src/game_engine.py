from constants import HOUR_5PM, HOUR_8PM
from game_data_client import GameDataClient
from game_time import get_est_hours_today
from interfaces import MatchStatus, TripData, TripStatus
from game_util import (
    copyTransiterDataToTripData,
    hasTripAssigned,
    isTripComplete,
    isTripOnWayToFirstStation,
    setFirstActualTimeToPredictedTime,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self):
        self.game_data_client = GameDataClient()
        self.transiter_client = TransiterClient()
        self.matchesToUpdate = None

    def setUp(self) -> None:
        self.matchesToUpdate = self.game_data_client.get_matches_for_today()
        for match in self.matchesToUpdate:
            match["matchData"]["matchStatus"] = MatchStatus.ONGOING

    def isSetUp(self) -> bool:
        return self.matchesToUpdate is not None

    def maybeAssignTrip(self, trip: TripData) -> bool:
        current_trips = self.transiter_client.get_trips(trip["routeId"])
        tripOnWayToFirstStation = next(
            (trip for trip in current_trips if isTripOnWayToFirstStation(trip)), None
        )
        if tripOnWayToFirstStation:
            copyTransiterDataToTripData(tripOnWayToFirstStation, trip)
            setFirstActualTimeToPredictedTime(trip)
            trip["tripStatus"] = TripStatus.ONGOING
            print(trip)

    def update(self, bypass_hours=False) -> None:
        est_hours_today = get_est_hours_today()
        if not bypass_hours and est_hours_today < HOUR_5PM:
            return
        elif not bypass_hours and est_hours_today > HOUR_8PM:
            # clean up
            return
        else:
            if not self.isSetUp():
                self.setUp()
            for match in self.matchesToUpdate:
                if not match["matchData"]["matchStatus"] == MatchStatus.ONGOING:
                    continue
                for trip in match["matchData"]["competingTrips"]:
                    if isTripComplete(trip):
                        continue
                    if not hasTripAssigned(trip):
                        self.maybeAssignTrip(trip)
                    if trip["tripStatus"] == TripStatus.ONGOING:
                        pass
