from dynamodb_client import DynamoDbClient
from interface import Game
from time_util import get_current_week_number, get_today_est_iso_format


class GamesClient:
    def __init__(self):
        self.dynamodb_client = DynamoDbClient(
            table_name="HeadwayGames",
            partitionKeyName="week_number",
            sortKeyName="game_id",
        )

    def get_game(self, week_number: int, game_id: str) -> Game:
        game = self.dynamodb_client.getItem(week_number, game_id)
        return game

    def get_games_for_week(self, week_number: int) -> list[Game]:
        games = self.dynamodb_client.getItems(week_number)
        return games

    def get_games_for_this_week(self) -> list[Game]:
        week_number = get_current_week_number()
        return self.get_games_for_week(week_number)

    def get_games_for_today(self):
        games_for_this_week = self.get_games_for_this_week()
        today_est_iso = get_today_est_iso_format()
        return [
            game for game in games_for_this_week if game["date_iso"] == today_est_iso
        ]

    def write_game(self, game: Game):
        return self.dynamodb_client.putItem(game)
