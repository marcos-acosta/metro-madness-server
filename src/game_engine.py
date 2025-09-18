from datetime import datetime
import random
import traceback
import time
from game_data_client import GameDataClient
from game_time import (
    epoch_time_to_seconds_since_midnight_est,
    get_est_hours_today,
    get_est_seconds_since_midnight,
)
from interfaces import (
    GameEngineConfig,
    Match,
    MatchData,
    MatchStatus,
    RouteId,
    TripData,
    TripStatus,
    VictoryType,
)
from game_util import (
    copyTransiterDataToTripData,
    get_latest_assignment_time_seconds_est,
    getArrivalOrDepartureTime,
    hasTripAssigned,
    isTripComplete,
    isTripDisqualified,
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
        if matchData.get("numStopsToFinish") is not None:
            return
        if self.config.get("override_num_stops_to_finish"):
            matchData["numStopsToFinish"] = self.config.get(
                "override_num_stops_to_finish"
            )
            if self.config.get("verbose"):
                print(
                    f"Set minimum number of stops to finish at {matchData['numStopsToFinish']} (overridden)"
                )
            return
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
            tripData["tripStatus"] = TripStatus.DQ_DISAPPEARED
            return
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

    def _maybe_mark_trip_as_completed(
        self, match_data: MatchData, trip_data: TripData
    ) -> bool:
        stops_to_finish = match_data.get("numStopsToFinish")
        if stops_to_finish is None or trip_data.get("stops") is None:
            return False
        stops_after_terminal_with_delay = [
            stop
            for i, stop in enumerate(trip_data.get("stops"))
            if i > 0 and stop.get("delay") is not None
        ]
        if len(stops_after_terminal_with_delay) >= stops_to_finish:
            trip_data["tripStatus"] = TripStatus.FINISHED
            trip_data["finalDelay"] = stops_after_terminal_with_delay[-1].get("delay")
            if self.config.get("verbose"):
                print(
                    f"Marked route {trip_data.get('routeId')} as finished with final delay of {trip_data.get('finalDelay')} seconds"
                )
            return True
        return False

    def _maybe_disqualify_trip(self, trip_data: TripData) -> bool:
        if trip_data.get(
            "tripStatus"
        ) == TripStatus.NOT_ASSIGNED and get_est_seconds_since_midnight() > get_latest_assignment_time_seconds_est(
            self.config
        ):
            trip_data["tripStatus"] = TripStatus.DQ_NEVER_ASSIGNED
            if self.config.get("verbose"):
                print(
                    f"Disqualified route {trip_data.get('routeId')} for never being assigned"
                )
            return True
        elif self.config.get(
            "game_end_time_hours"
        ) and get_est_hours_today() > self.config.get("game_end_time_hours"):
            trip_data["tripStatus"] = TripStatus.DQ_TOOK_TOO_LONG
            if self.config.get("verbose"):
                print(
                    f"Disqualified route {trip_data.get('routeId')} for taking too long"
                )
            return True
        return False

    def _maybe_end_trip(self, match_data: MatchData, trip_data: TripData):
        finished = self._maybe_mark_trip_as_completed(match_data, trip_data)
        if not finished:
            self._maybe_disqualify_trip(trip_data)

    def _set_up(self) -> None:
        self.matchesToUpdate = self.game_data_client.get_matches_for_today()
        for match in self.matchesToUpdate:
            match.get("matchData", {})["matchStatus"] = MatchStatus.ONGOING

    def _maybe_end_match(self, match: Match) -> bool:
        match_data = match.get("matchData")
        if (
            match_data.get("numStopsToFinish") is not None
            and len(match_data.get("competingTrips")) == 2
            and all(
                (
                    isTripComplete(trip_data)
                    for trip_data in match_data.get("competingTrips")
                )
            )
        ):
            first_trip = match_data.get("competingTrips")[0]
            second_trip = match_data.get("competingTrips")[1]
            random_route_id = (
                first_trip.get("routeId")
                if random.random() > 0.5
                else second_trip.get("routeId")
            )
            if isTripDisqualified(first_trip) or isTripDisqualified(second_trip):
                if isTripDisqualified(first_trip) and isTripDisqualified(second_trip):
                    match_data["matchResult"] = {
                        "victoryType": VictoryType.COIN_TOSS_BOTH_DQ,
                        "winner": random_route_id,
                    }
                else:
                    winner = (
                        first_trip.get("routeId")
                        if isTripDisqualified(second_trip)
                        else second_trip.get("routeId")
                    )
                    match_data["matchResult"] = {
                        "victoryType": VictoryType.ONE_DQ,
                        "winner": winner,
                    }
            else:
                first_trip_delay = first_trip.get("finalDelay")
                second_trip_delay = second_trip.get("finalDelay")
                if first_trip_delay == second_trip_delay:
                    match_data["matchResult"] = {
                        "victoryType": VictoryType.COIN_TOSS_SAME_DELAY,
                        "winner": random_route_id,
                    }
                else:
                    winner = (
                        first_trip.get("routeId")
                        if first_trip_delay < second_trip_delay
                        else second_trip.get("routeId")
                    )
                    match_data["matchResult"] = {
                        "victoryType": VictoryType.FAIR_AND_SQUARE,
                        "winner": winner,
                    }
            match_data["matchStatus"] = MatchStatus.ENDED
            match_result = match_data.get("matchResult", {})
            winner = match_result.get("winner")
            self._update_bracket_with_winner(match.get("matchId"), winner)
            if self.config.get("verbose"):
                print(
                    f"Match ended - Winner: {winner}, Victory type: {match_result.get('victoryType')}"
                )
            return True
        return False

    def _update_bracket_with_winner(self, match_id: str, winner: RouteId):
        bracket = self.game_data_client.get_matches_for_this_week()
        modified_match = None
        for match in bracket:
            for trip in match.get("matchData").get("competingTrips"):
                if trip.get("winnerMatchId") == match_id:
                    if self.config.get("verbose"):
                        print(
                            f"Updating a competing trip in match {match.get('matchId')} to the winner of this match, {winner}"
                        )
                    trip["routeId"] = winner
                    modified_match = match
                    break
        if modified_match:
            self.game_data_client.update_match(modified_match)

    def update(self) -> bool:
        est_hours_today = get_est_hours_today()
        if self.config.get(
            "game_start_time_hours"
        ) and est_hours_today < self.config.get("game_start_time_hours"):
            return
        else:
            if not self._is_set_up():
                self._set_up()
            for match in self.matchesToUpdate:
                matchData = match.get("matchData", {})
                if not matchData.get("matchStatus") == MatchStatus.ONGOING:
                    continue
                for trip in matchData.get("competingTrips", []):
                    if not trip.get("routeId"):
                        trip["tripStatus"] = TripStatus.DQ_NO_COMPETITOR
                        continue
                    if isTripComplete(trip):
                        continue
                    if not hasTripAssigned(trip):
                        self._maybeAssignTrip(trip)
                    if trip.get("tripStatus") == TripStatus.ONGOING:
                        self._update_stop_times(trip)
                    self._maybe_end_trip(matchData, trip)
                self._maybe_set_num_stops_to_finish(matchData)
                self._maybe_end_match(match)
                if not self.config.get("skip_write_to_db"):
                    self.game_data_client.update_match(match)
        return all(
            match.get("matchData", {}).get("matchStatus") == MatchStatus.ENDED
            for match in self.matchesToUpdate
        )

    def run_game_loop(self) -> None:
        while True:
            if self.config.get("verbose"):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Update")
            try:
                all_matches_finished = self.update()
                if all_matches_finished:
                    if self.config.get("verbose"):
                        print("All matches completed, exiting...")
                    break
            except Exception as e:
                print(f"[ERROR] In update(): {e}")
                traceback.print_exc()
            if self.config.get("verbose"):
                print()
            time.sleep(self.config.get("refresh_rate_seconds"))
