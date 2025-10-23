import datetime
import time
import traceback
from train_recruiter import TrainRecruiter
from game_config import DEFAULT_DEV_POPULATE_TRAINS_CONFIG, GAME_TYPE_TO_ROUTE_IDS
from games_client import GamesClient
from interface import (
    Game,
    GameEngineConfig,
    GameStatus,
    GameType,
    RankingStatus,
    Route,
    RouteId,
    TripData,
    TripStatus,
)
from time_util import (
    epoch_seconds_to_seconds_since_midnight_est,
    get_current_seconds_since_midnight_est,
    get_unix_timestamp,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self, config: GameEngineConfig):
        self.game_data_client = GamesClient()
        self.transiter_client = TransiterClient()
        self.train_recruiter = TrainRecruiter(DEFAULT_DEV_POPULATE_TRAINS_CONFIG)
        self.game: Game | None = None
        self.config = config
        self._setup()
        self._populate_routes()

    def _log(
        self,
        message,
        route_id: RouteId | None = None,
        trip_id: str | None = None,
        prefix=True,
    ):
        route_id_prefix = f"[{route_id}] " if route_id else ""
        trip_id_prefix = f"[{trip_id}] " if trip_id else ""
        prefix = "[game engine] " if prefix else ""
        if self.config.get("verbose"):
            print("".join([prefix, route_id_prefix, trip_id_prefix, message]))

    def _setup(self):
        games_today = self.game_data_client.get_games_for_today()
        upcoming_games = sorted(
            [
                g
                for g in games_today
                if (
                    g.get("start_time_s") > get_current_seconds_since_midnight_est()
                    and g.get("game_status") == GameStatus.GAME_STATUS_NOT_STARTED
                )
            ],
            key=lambda g: g.get("start_time_s"),
        )
        if len(upcoming_games):
            self.game = upcoming_games[0]
            self._log(f"Set current game to: {self.game.get('game_id')}.")
        else:
            self._log("No upcoming games found for today.")

    @staticmethod
    def _get_routes_for_game(game: Game) -> list[RouteId]:
        route_ids = []
        if game.get("game_type") == GameType.GAME_TYPE_SYSTEM_CHAMPIONSHIP:
            # TODO: implement
            pass
        else:
            route_ids = GAME_TYPE_TO_ROUTE_IDS[game.get("game_type")]
        return route_ids

    def _pull_game(self):
        if self.game:
            self.game = self.game_data_client.get_game(
                self.game.get("week_number"),
                self.game.get("game_id"),
            )
            self._log("Pulled game from DynamoDB.")

    def _push_game(self):
        if self.game:
            self.game_data_client.write_game(self.game)
            self._log("Pushed game to DynamoDB.")

    def _populate_routes(self):
        if not self.game:
            self._log("Can't populate routes because there's no game to update.")
            return
        route_ids = self._get_routes_for_game(self.game)
        try:
            self.game = self.train_recruiter.recruit_trains(self.game, route_ids)
        except Exception:
            traceback.print_exc()
            # TODO: Handle this case
            pass
        else:
            self._push_game()

    def _is_trip_permanently_disappeared(self, trip: TripData):
        return (not trip.get("last_seen_timestamp")) or get_unix_timestamp() - trip.get(
            "last_seen_timestamp"
        ) >= self.config.get("minutes_before_permamently_disappeared") * 60

    @staticmethod
    def _is_trip_final(trip: TripData):
        return trip.get("actual_target_arrival_time_s") is not None or trip.get(
            "trip_status"
        ) in [
            TripStatus.TRIP_STATUS_PERMANENTLY_DISAPPEARED,
            TripStatus.TRIP_STATUS_REACHED_TARGET,
        ]

    @staticmethod
    def _get_actual_time(transiter_stop: object):
        if transiter_stop.get("arrival", {}).get("time"):
            return int(transiter_stop.get("arrival", {}).get("time"))
        elif transiter_stop.get("departure", {}).get("time"):
            return int(transiter_stop.get("departure", {}).get("time"))
        else:
            return None

    def _update_stop_times(
        self, trip: TripData, trip_snapshot: object, route_id: RouteId
    ):
        # Both `stops` lists should have the same stops, but this is more robust to unexpected differences
        trip_stop_id_to_index = {
            stop.get("stop_id"): i for (i, stop) in enumerate(trip.get("stops"))
        }
        for stop_time in trip_snapshot.get("stopTimes", []):
            if stop_time.get("future") == True:
                continue
            actual_time = epoch_seconds_to_seconds_since_midnight_est(
                int(self._get_actual_time(stop_time))
            )
            stop_id = stop_time.get("stop", {}).get("id")
            trip_index = (
                None
                if stop_id not in trip_stop_id_to_index
                else trip_stop_id_to_index[stop_id]
            )
            if not trip_index:
                continue
            trip_stop = trip.get("stops")[trip_index]
            # We don't want to ever update the actual arrival time
            if trip_stop.get("actual_arrival_time_s"):
                continue
            trip_stop["actual_arrival_time_s"] = actual_time
            self._log(
                f"Updated arrival/destination time at {trip_stop.get('stop_name')} to {actual_time}.",
                route_id,
                trip.get("trip_id_short"),
            )
            if trip_stop.get("stop_id") == trip.get("target_stop", {}).get("stop_id"):
                self._log(
                    f"Reached target stop; marking as completed.",
                    route_id,
                    trip.get("trip_id_short"),
                )
                trip["actual_target_arrival_time_s"] = actual_time
                trip["trip_status"] = TripStatus.TRIP_STATUS_REACHED_TARGET

    def _process_trip(self, route_id: RouteId, trip: TripData):
        """
        Process a single trip by fetching realtime data and updating status.
        Returns the trip snapshot from transiter, or None if no data available.
        """
        if self._is_trip_final(trip):
            return None
        trip_id_short = trip.get("trip_id_short")
        trip_snapshot = self.transiter_client.get_trip(route_id, trip_id_short)

        if trip_snapshot is None:
            self._log(
                "Transiter did not return any trip data.",
                route_id,
                trip_id_short,
            )
            if trip.get("trip_status") == TripStatus.TRIP_STATUS_UNDERWAY:
                self._log(
                    "Trip was underway but now disappeared.",
                    route_id,
                    trip_id_short,
                )
                trip["trip_status"] = TripStatus.TRIP_STATUS_DISAPPEARED
                if self._is_trip_permanently_disappeared(trip):
                    self._log(
                        "Trip marked as permanently disappeared.",
                        route_id,
                        trip.get("trip_id_short"),
                    )
                    trip["trip_status"] = TripStatus.TRIP_STATUS_PERMANENTLY_DISAPPEARED
        else:
            self._log("Realtime data fetched successfully.", route_id, trip_id_short)
            trip["trip_status"] = TripStatus.TRIP_STATUS_UNDERWAY
            trip["last_seen_timestamp"] = get_unix_timestamp()
            self._update_stop_times(trip, trip_snapshot, route_id)

        return trip_snapshot

    def _refresh_game_data(self):
        if not self.game:
            return
        self.game["game_status"] = GameStatus.GAME_STATUS_UNDERWAY
        for route in self.game.get("routes"):
            route_id = route.get("route_id")
            selected_trip = route.get("selected_trip")
            candidate_trips = route.get("candidate_trips")

            # Check that we have either selected_trip or candidate_trips
            if selected_trip is None and not candidate_trips:
                self._log(
                    "Route has neither selected_trip nor candidate_trips.", route_id
                )
                continue

            # If we have a selected trip, process it
            if selected_trip is not None:
                self._process_trip(route_id, selected_trip)
            else:
                # Check candidate trips for realtime data
                for candidate_trip in candidate_trips:
                    trip_snapshot = self._process_trip(route_id, candidate_trip)
                    if trip_snapshot is not None:
                        self._log(
                            f"Promoting candidate trip to selected_trip.",
                            route_id,
                            candidate_trip.get("trip_id_short"),
                        )
                        route["selected_trip"] = candidate_trip
                        del route["candidate_trips"]
                        break

    def _update_rankings(self):
        if not self.game:
            return

        # Collect all routes with actual arrival times
        completed_routes = []
        for route in self.game.get("routes"):
            selected_trip = route.get("selected_trip")
            if (
                selected_trip
                and selected_trip.get("actual_target_arrival_time_s") is not None
            ):
                actual_time = selected_trip.get("actual_target_arrival_time_s")
                completed_routes.append(
                    {
                        "route": route,
                        "actual_time": actual_time,
                        "route_id": route.get("route_id"),
                    }
                )

        if not completed_routes:
            return

        # Sort by actual arrival time (earliest first)
        completed_routes.sort(key=lambda x: x["actual_time"])

        # Assign rankings
        for rank, route_data in enumerate(completed_routes, start=1):
            route: Route = route_data["route"]
            old_rank = route.get("ranking", {}).get("rank")
            if old_rank != rank:
                route["ranking"]["rank"] = rank
                route["ranking"]["ranking_status"] = RankingStatus.RANKING_STATUS_RANKED
                self._log(
                    f"Updated rank to {rank} (arrival time: {route_data['actual_time']}s).",
                    route_data["route_id"],
                )

    def run_game_loop(self):
        while True:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log(f"\n=== {now_str} ===\n", prefix=False)
            if self.config.get("pull_before_push"):
                self._pull_game()
            self._refresh_game_data()
            self._update_rankings()
            self._push_game()
            time.sleep(self.config.get("refresh_rate_s"))
