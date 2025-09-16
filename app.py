from constants import RouteId
import game_data_client as gdc
import transiter_client as tc


def main():
    # game_data_client = gdc.GameDataClient()
    # game_data_client.putItem("2025-09-15", "2", {"testData": 15})
    # data = game_data_client.getItem("2025-09-15", "2")
    # print(data)
    transiter_client = tc.TransiterClient()
    trips = transiter_client.get_trips(RouteId.ROUTE_A)
    print(trips)


if __name__ == "__main__":
    main()
