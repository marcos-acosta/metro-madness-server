from dynamodb_client import DynamoDbClient
from game_time import get_current_week_str, get_today_date_est_str
from interfaces import Match


class GameDataClient:
    def __init__(self):
        self.dynamodb_client = DynamoDbClient(
            table_name="metrocard-madness-game-data",
            partitionKeyName="bracketId",
            sortKeyName="matchId",
        )

    def get_matches_for_this_week(self) -> list[Match]:
        current_week = get_current_week_str()
        matches = self.dynamodb_client.getItems(current_week)
        return matches

    def get_matches_for_today(self):
        matches_for_this_week = self.get_matches_for_this_week()
        today_est_str = get_today_date_est_str()
        return [
            match
            for match in matches_for_this_week
            if match["matchData"]["date"] == today_est_str
        ]
