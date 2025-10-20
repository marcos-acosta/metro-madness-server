import datetime
import json
from choose_stops import populate_trains
from game_config import GAME_TYPE_TO_ROUTE_IDS
from games_client import GamesClient
from interface import Game, GameEngineConfig, GameStatus, GameType, RouteId
from time_util import (
    get_current_seconds_since_midnight_est,
)
from transiter_client import TransiterClient


class GameEngine:
    def __init__(self, config: GameEngineConfig):
        self.game_data_client = GamesClient()
        self.transiter_client = TransiterClient()
        self.game_to_update: Game | None = None
        self.config = config
        self._setup()
        self._select_trains()

    def _log(self, message):
        if self.config.get("verbose"):
            print(f"[{datetime.datetime.now()}] {message}")

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
            self.game_to_update = upcoming_games[0]
            self._log(f"Set current game to: {self.game_to_update.get('game_id')}.")
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

    def _select_trains(self):
        if not self.game_to_update:
            self._log("Can't select trains because there's no game to update.")
            return
        route_ids = self._get_routes_for_game(self.game_to_update)
        self.game_to_update = populate_trains(self.game_to_update, route_ids)
        self.game_to_update["game_status"] = GameStatus.GAME_STATUS_UNDERWAY
        # with open("game_to_update.json", "w") as f:
        #     json.dump(self.game_to_update, f, indent=2)
