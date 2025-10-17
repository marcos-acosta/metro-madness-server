from google.protobuf import json_format
from compiled import headway_pb2

pot = headway_pb2.Pot()
stake = pot.stakes.add()
stake.game_id = "exgid"

json_string = json_format.MessageToJson(pot)
print(json_string)
