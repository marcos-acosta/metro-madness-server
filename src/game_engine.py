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
    RouteId,
    TripData,
    TripStatus,
)
from time_util import (
    get_current_seconds_since_midnight_est,
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

    def _get_routes_for_game(self, game: Game) -> list[RouteId]:
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

    def _process_trip(self, route_id: RouteId, trip: TripData):
        """
        Process a single trip by fetching realtime data and updating status.
        Returns the trip snapshot from transiter, or None if no data available.
        """
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
                # TODO: Disqualify if destination was never reached
                trip["trip_status"] = TripStatus.TRIP_STATUS_DISAPPEARED
        else:
            self._log("Realtime data fetched successfully.", route_id, trip_id_short)

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

    def run_game_loop(self):
        while True:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._log(f"\n=== {now_str} ===\n", prefix=False)
            if self.config.get("pull_before_push"):
                self._pull_game()
            self._refresh_game_data()
            self._push_game()
            time.sleep(self.config.get("refresh_rate_s"))
