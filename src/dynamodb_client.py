from boto3.dynamodb.conditions import Key
import boto3


class DynamoDbClient:
    def __init__(self, table_name: str, partitionKeyName: str, sortKeyName: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.partitionKeyName = partitionKeyName
        self.sortKeyName = sortKeyName

    def getItem(self, partitionKey: str, sortKey: str):
        key_data = {self.partitionKeyName: partitionKey, self.sortKeyName: sortKey}
        response = self.table.get_item(Key=key_data)
        return response.get("Item")

    def getItems(self, partitionKey: str):
        response = self.table.query(
            KeyConditionExpression=Key(self.partitionKeyName).eq(partitionKey)
        )
        return response.get("Items")

    def putItem(self, partitionKey: str, sortKey: str, **kwargs):
        item_data = {
            self.partitionKeyName: partitionKey,
            self.sortKeyName: sortKey,
            **kwargs,
        }
        response = self.table.put_item(Item=item_data)
        return response

    def batchPutItems(self, data: list[tuple]):
        with self.table.batch_writer() as batch:
            for entry in data:
                batch.put_item(
                    Item={
                        self.partitionKeyName: entry[0],
                        self.sortKeyName: entry[1],
                        **entry[2],
                    }
                )
