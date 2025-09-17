from datetime import datetime
import time
from game_data_client import GameDataClient
from game_time import epoch_time_to_seconds_since_midnight_est, get_est_hours_today
from interfaces import GameEngineConfig, MatchData, MatchStatus, TripData, TripStatus
from game_util import (
    copyTransiterDataToTripData,
    getArrivalOrDepartureTime,
    hasTripAssigned,
    isTripComplete,
    isViableCompetingTrip,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self, config: GameEngineConfig):
        self.game_data_client = GameDataClient()
        self.transiter_client = TransiterClient()
        self.matchesToUpdate = None
        self.config = config

    def _is_set_up(self) -> bool:
        return self.matchesToUpdate is not None

    def _maybeAssignTrip(self, trip: TripData) -> None:
        current_trips = self.transiter_client.get_trips(trip.get("routeId"))
        tripOnWayToFirstStation = next(
            (
                trip
                for trip in current_trips
                if isViableCompetingTrip(trip, self.config)
            ),
            None,
        )
        if tripOnWayToFirstStation:
            copyTransiterDataToTripData(tripOnWayToFirstStation, trip)
            trip["tripStatus"] = TripStatus.ONGOING
            if self.config.get("verbose"):
                print(
                    f"Assigned route {trip.get('routeId')} to trip id {trip.get('tripId')}"
                )

    def _maybe_set_num_stops_to_finish(self, matchData: MatchData):
        num_stops = [
            len(trip.get("stops", [])) if hasTripAssigned(trip) else None
            for trip in matchData.get("competingTrips", [])
        ]
        if all(num_stops):
            min_num_stops = min(num_stops) - 1
            for allowed_num_stops_to_finish in self.config.get(
                "allowed_num_stops_to_finish"
            )[::-1]:
                if min_num_stops >= allowed_num_stops_to_finish:
                    matchData["numStopsToFinish"] = allowed_num_stops_to_finish
                    if self.config.get("verbose"):
                        print(
                            f"Set minimum number of stops to finish at {allowed_num_stops_to_finish}"
                        )
                    return

    def _update_stop_times(self, tripData: TripData) -> None:
        trip_transiter_data = self.transiter_client.get_trip(
            tripData.get("routeId"), tripData.get("tripId")
        )
        if trip_transiter_data is None:
            # TODO: Disqualify
            pass
        for stop_time in trip_transiter_data.get("stopTimes", []):
            if stop_time.get("future") == True:
                continue
            relevant_stop = next(
                (
                    stop
                    for stop in tripData.get("stops", [])
                    if stop.get("stopId") == stop_time.get("stop", {}).get("id")
                ),
                None,
            )
            if relevant_stop.get("actualTimeSeconds") is not None:
                continue
            actual_time_seconds = epoch_time_to_seconds_since_midnight_est(
                getArrivalOrDepartureTime(stop_time)
            )
            relevant_stop["actualTimeSeconds"] = actual_time_seconds
            predicted_time_seconds = relevant_stop.get("predictedTimeSeconds")
            relevant_stop["delay"] = actual_time_seconds - predicted_time_seconds
            if self.config.get("verbose"):
                print(
                    f"Set actual arrival time on line {tripData.get('routeId')} for stop {relevant_stop.get('stopName')} to {actual_time_seconds}"
                )

    def set_up(self) -> None:
        self.matchesToUpdate = self.game_data_client.get_matches_for_today()
        for match in self.matchesToUpdate:
            match.get("matchData", {})["matchStatus"] = MatchStatus.ONGOING

    def update(self) -> None:
        est_hours_today = get_est_hours_today()
        if not self.config.get(
            "ignore_game_time"
        ) and est_hours_today < self.config.get("game_start_time_hours"):
            return
        elif not self.config.get(
            "ignore_game_time"
        ) and est_hours_today > self.config.get("game_end_time_hours"):
            # clean up
            return
        else:
            if not self._is_set_up():
                self.set_up()
            for match in self.matchesToUpdate:
                matchData = match.get("matchData", {})
                if not matchData.get("matchStatus") == MatchStatus.ONGOING:
                    continue
                for trip in matchData.get("competingTrips", []):
                    if isTripComplete(trip):
                        continue
                    if not hasTripAssigned(trip):
                        self._maybeAssignTrip(trip)
                    if trip.get("tripStatus") == TripStatus.ONGOING:
                        self._update_stop_times(trip)
                    # maybeConcludeTrip -> maybeDisquality or maybeMarkAsFinished
                if matchData.get("numStopsToFinish") is None:
                    self._maybe_set_num_stops_to_finish(matchData)
                # if numStopsToFinish is set and both are finished, declare winner and update brackets
                if not self.config.get("skip_write_to_db"):
                    self.game_data_client.update_match(match)

    def run_game_loop(self) -> None:
        while True:
            if self.config.get("verbose"):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Update")
            try:
                self.update()
            except Exception as e:
                print(f"ERROR IN UPDATE: {e}")
            if self.config.get("verbose"):
                print()
            time.sleep(self.config.get("refresh_rate_seconds"))
