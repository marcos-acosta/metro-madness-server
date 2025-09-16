from constants import RouteId
import game_data_client as gdc
import transiter_client as tc


def main():
    game_data_client = gdc.GameDataClient()
    transiter_client = tc.TransiterClient()
    trips = transiter_client.get_trips(RouteId.ROUTE_A)
    trip_ids = [trip["id"] for trip in trips]
    print(trip_ids)
    # game_data_client.putItem("testBracketId", "testMatchId", {"testData": trip_ids})
    print("Completed test program.")


if __name__ == "__main__":
    main()
