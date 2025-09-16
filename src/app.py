from constants import RouteId
import game_data_client as gdc
import transiter_client as tc
from datetime import datetime


def main():
    game_data_client = gdc.GameDataClient()
    transiter_client = tc.TransiterClient()
    trips = transiter_client.get_trips(RouteId.ROUTE_A)
    trip_ids = [trip["id"] for trip in trips]
    print(trip_ids)
    game_data_client.putItem("testBracketId", "testMatchId", {"testData": trip_ids})
    print(f"Completed test program at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.")


if __name__ == "__main__":
    main()
