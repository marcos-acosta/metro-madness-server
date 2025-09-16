import boto3


class GameDataClient:
    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb")
        self.game_data_table = self.dynamodb.Table("metrocard-madness-game-data")

    def getItem(self, bracketId: str, matchId: str):
        key_data = {"bracketId": bracketId, "matchId": matchId}
        response = self.game_data_table.get_item(Key=key_data)
        return response.get("Item")

    def putItem(self, bracketId: str, matchId: str, data):
        item_data = {"bracketId": bracketId, "matchId": matchId, "data": data}
        response = self.game_data_table.put_item(Item=item_data)
        return response
