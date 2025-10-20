from boto3.dynamodb.conditions import Key
import boto3
import decimal


def replace_decimals(obj):
    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj:
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


class DynamoDbClient:
    def __init__(self, table_name: str, partitionKeyName: str, sortKeyName: str):
        self.dynamodb = boto3.resource("dynamodb")
        self.table = self.dynamodb.Table(table_name)
        self.partitionKeyName = partitionKeyName
        self.sortKeyName = sortKeyName

    def getItem(self, partitionKey: str | int, sortKey: str | int):
        key_data = {self.partitionKeyName: partitionKey, self.sortKeyName: sortKey}
        response = self.table.get_item(Key=key_data)
        return response.get("Item")

    def getItems(self, partitionKey: str | int):
        response = self.table.query(
            KeyConditionExpression=Key(self.partitionKeyName).eq(partitionKey)
        )
        return replace_decimals(response.get("Items"))

    def putItem(self, item):
        return self.table.put_item(Item=item)

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
