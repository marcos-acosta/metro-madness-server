import time
from choose_stops import populate_trains
from game_config import GAME_TYPE_TO_ROUTE_IDS
from games_client import GamesClient
from interface import Game, GameEngineConfig, GameStatus, GameType, RouteId, TripStatus
from time_util import (
    get_current_seconds_since_midnight_est,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self, config: GameEngineConfig):
        self.game_data_client = GamesClient()
        self.transiter_client = TransiterClient()
        self.game: Game | None = None
        self.config = config
        self._setup()
        self._select_trains()

    def _log(
        self, message, route_id: RouteId | None = None, trip_id: str | None = None
    ):
        route_id_prefix = f"[{route_id}]" if route_id else ""
        trip_id_prefix = f"[{trip_id}]" if trip_id else ""
        if self.config.get("verbose"):
            print(" ".join(["[game engine]", route_id_prefix, trip_id_prefix, message]))

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

    def _select_trains(self):
        if not self.game:
            self._log("Can't select trains because there's no game to update.")
            return
        route_ids = self._get_routes_for_game(self.game)
        try:
            self.game = populate_trains(self.game, route_ids)
        except:
            # TODO: Handle this case
            pass
        else:
            self.game["game_status"] = GameStatus.GAME_STATUS_UNDERWAY
            self._push_game()

    def _refresh_game_data(self):
        if not self.game:
            return
        for train in self.game.get("trains"):
            route_id = train.get("route_id")
            trip_data = train.get("trip_data")
            if trip_data is None:
                # TODO: Make sure train is DQed
                continue
            trip_id_short = trip_data.get("trip_id_short")
            trip_snapshot = self.transiter_client.get_trip(route_id, trip_id_short)
            if trip_snapshot is None:
                self._log("Transiter did not return any trip data.")
                if trip_data.get("trip_status") == TripStatus.TRIP_STATUS_UNDERWAY:
                    self._log("Trip was underway but now disappeared.")
                    # TODO: Disqualify if destination was never reached
                    trip_data["trip_status"] = TripStatus.TRIP_STATUS_DISAPPEARED
            else:
                self._log("Realtime data fetched successfully.")

    def run_game_loop(self):
        while True:
            self._log("=== TICK ===")
            self._pull_game()
            self._refresh_game_data()
            self._push_game()
            time.sleep(self.config.get("refresh_rate_s"))
