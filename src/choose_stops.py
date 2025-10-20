from game_constants import WEEKDAY_NAMES
from gtfs_loader import GTFSLoader
from pathlib import Path
from datetime import date
from collections import defaultdict, namedtuple
import random
import pandas as pd

from interface import (
    RouteId,
    Stop,
    TripStatus,
    RankingStatus,
    GameType,
    GameVariant,
    GameStatus,
    Game,
    Train,
)

CandidateStopTime = namedtuple(
    "CandidateStopTime", ["scheduled_arrival_s", "trips_by_route"]
)


def get_short_trip_id_from_full_trip_id(trip_id):
    return "_".join(trip_id.split("_")[-2:])


def join_trips_with_calendar(trips: pd.DataFrame, calendar: pd.DataFrame):
    return trips.merge(calendar, how="left", on="service_id")


def filter_by_weekday(trips_w_calendar: pd.DataFrame, game_date: date):
    weekday_name = WEEKDAY_NAMES[game_date.weekday()]
    # Filter out if the scheduled trip is not on the game date weekday,
    # or if the schedule does not include the game date
    filter_out_mask = (
        (trips_w_calendar[weekday_name] < 1)
        | (
            pd.to_datetime(trips_w_calendar["start_date"], format="%Y%m%d").dt.date
            > game_date
        )
        | (
            pd.to_datetime(trips_w_calendar["end_date"], format="%Y%m%d").dt.date
            < game_date
        )
    )
    return trips_w_calendar[~filter_out_mask]


def join_with_calendar_dates(df: pd.DataFrame, calendar_dates: pd.DataFrame):
    return df.merge(calendar_dates, how="left", on="service_id")


def filter_removed_trips(
    df: pd.DataFrame, calendar_dates: pd.DataFrame, game_date: date
):
    game_date_str = game_date.strftime("%Y%m%d")

    # Find service_ids that have exception_type == 2 on the specific game_date
    removed_on_game_date = calendar_dates[
        (calendar_dates["date"] == game_date_str)
        & (calendar_dates["exception_type"] == 2)
    ]["service_id"].unique()

    # Filter out trips with those service_ids
    mask = ~df["service_id"].isin(removed_on_game_date)
    return df[mask]


def filter_not_added_trips(
    df: pd.DataFrame, calendar_dates: pd.DataFrame, game_date: date
):
    game_date_str = game_date.strftime("%Y%m%d")
    # Find service_ids that have exception_type == 1 on the specific game_date
    added_on_game_date = calendar_dates[
        (calendar_dates["date"] == game_date_str)
        & (calendar_dates["exception_type"] == 1)
    ]["service_id"].unique()
    # Only keep rows that either have start / end date data, or which were explicitly added
    mask = df["start_date"].notnull() | df["service_id"].isin(added_on_game_date)
    return df[mask]


def hhmmss_to_seconds(hhmmss: str):
    parts = hhmmss.split(":")
    return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])


def add_numeric_stop_times(stop_times: pd.DataFrame):
    stop_times["scheduled_arrival_s"] = stop_times["arrival_time"].apply(
        hhmmss_to_seconds
    )
    return stop_times


def filter_stop_times_by_time(stop_times: pd.DataFrame, start_time: int, end_time: int):
    mask = (stop_times["scheduled_arrival_s"] >= start_time) & (
        stop_times["scheduled_arrival_s"] <= end_time
    )
    return stop_times[mask]


def filter_trips_by_route_id(trips: pd.DataFrame, route_ids_to_keep: list[str]):
    return trips[trips["route_id"].isin(route_ids_to_keep)]


def sample_rows(df, n=20):
    print(df.sample(n=n))


def join_trips_with_stop_times(trips: pd.DataFrame, stop_times: pd.DataFrame):
    return trips.merge(stop_times, how="inner", on="trip_id")


def get_possible_scheduled_times_in_window(start_time_s, end_time_s):
    return range(start_time_s, end_time_s, 30)


def get_candidate_stop_times(
    stop_times: pd.DataFrame, start_time_s: int, end_time_s: int
) -> list[CandidateStopTime]:
    candidate_times = []
    for scheduled_time in get_possible_scheduled_times_in_window(
        start_time_s, end_time_s
    ):
        matching_stop_times = stop_times[
            stop_times["scheduled_arrival_s"] == scheduled_time
        ]
        if len(matching_stop_times) == 0:
            continue
        trips_by_route = defaultdict(list)
        for _, row in matching_stop_times[
            ["route_id", "trip_id", "stop_id"]
        ].iterrows():
            trips_by_route[row["route_id"]].append(row.to_dict())
        candidate_times.append(CandidateStopTime(scheduled_time, trips_by_route))
    return candidate_times


def get_best_candidate_stop_times(candidates: list[CandidateStopTime]):
    max_routes = max([len(candidate.trips_by_route) for candidate in candidates])
    return [
        candidate
        for candidate in candidates
        if len(candidate.trips_by_route) == max_routes
    ]


def randomly_select_trip_for_each_route(stop_time: CandidateStopTime):
    for route_id, trips in stop_time.trips_by_route.items():
        stop_time.trips_by_route[route_id] = random.choice(trips)


def get_stops_from_trip_id(
    trip_id: str, stop_times: pd.DataFrame, stops_data: pd.DataFrame
):
    trip_stop_times = stop_times[stop_times["trip_id"] == trip_id]
    # TODO: Dedupe to make sure there's only one of each stop
    trip_stop_times_w_name = trip_stop_times.merge(
        stops_data[["stop_id", "stop_name"]], how="left", on="stop_id"
    ).sort_values(by="stop_sequence")
    stops: list[Stop] = []
    for _, row in trip_stop_times_w_name.iterrows():
        stops.append(
            {
                "stop_id": row["stop_id"],
                "stop_name": row["stop_name"],
                "scheduled_arrival_time_s": row["scheduled_arrival_s"],
            }
        )
    return stops


def convert_selected_time_to_game_dict(
    stop_time: CandidateStopTime, stop_times: pd.DataFrame, stops_data: pd.DataFrame
) -> Game:
    trains: list[Train] = []
    for route_id, trip in stop_time.trips_by_route.items():
        train: Train = {
            "route_id": route_id,
            "trip_data": {
                "trip_id": trip["trip_id"],
                "trip_id_short": get_short_trip_id_from_full_trip_id(trip["trip_id"]),
                "trip_status": TripStatus.TRIP_STATUS_NOT_SEEN_YET,
                "stops": get_stops_from_trip_id(
                    trip["trip_id"], stop_times, stops_data
                ),
                "target_stop_id": trip["stop_id"],
            },
            "ranking": {
                "ranking_status": RankingStatus.RANKING_STATUS_PENDING,
            },
        }
        trains.append(train)

    game: Game = {
        "scheduled_arrival_time_s": stop_time.scheduled_arrival_s,
        "trains": trains,
    }
    return game


def construct_game(
    game: Game,
    gtfs_loader: GTFSLoader,
    route_ids: list[RouteId],
):
    game_date = date.fromisoformat(game.get("date_iso"))
    start_time = game.get("start_time_s")
    end_time = game.get("end_time_s")
    trips = gtfs_loader.load_csv_as_dataframe("trips.txt", dtype={"route_id": str})
    print(f":: Num trips at load: {len(trips)}")

    # Filter trips that aren't in our desired list of routes
    trips = filter_trips_by_route_id(trips, route_ids)
    print(f":: Num trips after route id filter: {len(trips)}")

    # Filter trips that have a regular schedule but don't cover the relevant day of the week
    calendar = gtfs_loader.load_csv_as_dataframe(
        "calendar.txt", dtype={"route_id": str, "start_date": str, "end_date": str}
    )
    trips_w_calendar = join_trips_with_calendar(trips, calendar)
    trips_w_calendar = filter_by_weekday(trips_w_calendar, game_date)
    print(f":: Num trips after weekday filter: {len(trips_w_calendar)}")

    # Filter out trips that have removal exceptions on the game_date
    calendar_dates = gtfs_loader.load_csv_as_dataframe(
        "calendar_dates.txt", dtype={"date": str}
    )
    trips_filtered = filter_removed_trips(trips_w_calendar, calendar_dates, game_date)
    print(f":: Num trips after filtering removed trips: {len(trips_filtered)}")

    # Filter out trips that don't have a regular schedule and were not added
    trips_filtered = filter_not_added_trips(trips_filtered, calendar_dates, game_date)
    print(f":: Num trips after filtering dateless trips: {len(trips_filtered)}")

    # Load stop times
    stop_times = gtfs_loader.load_csv_as_dataframe("stop_times.txt")
    stop_times = add_numeric_stop_times(stop_times)
    print(f":: Num stop times at load: {len(stop_times)}")

    # Filter stops by time
    stop_times_filtered = filter_stop_times_by_time(stop_times, start_time, end_time)
    print(f":: Num stop times after time filter: {len(stop_times_filtered)}")

    # Join stop times with remaining trips (implicit filter by inner join)
    stop_times_for_trips = join_trips_with_stop_times(
        trips_filtered, stop_times_filtered
    )
    print(f":: Num stop times after joining with trips: {len(stop_times_for_trips)}")

    # TODO: Check / filter out duplicate trips (e.g. are there duplicate short trip ids?

    # Check the coverage of every possible scheduled stop time
    candidate_times = get_candidate_stop_times(
        stop_times_for_trips, start_time, end_time
    )
    # Narrow down to those that have the most unique routes (ideally all)
    best_candidate_times = get_best_candidate_stop_times(candidate_times)
    if len(candidate_times) == 0:
        raise Exception("No candidate times found")
    # Randomly choose the time
    selected_candidate_time = random.choice(best_candidate_times)
    print(
        f":: Num unique routes in selected candidate time: {len(selected_candidate_time.trips_by_route)}"
    )
    # Mutates the object
    randomly_select_trip_for_each_route(selected_candidate_time)

    # Convert to dict
    stops_data = gtfs_loader.load_csv_as_dataframe("stops.txt")
    game_dict = convert_selected_time_to_game_dict(
        selected_candidate_time, stop_times, stops_data
    )
    return game | game_dict


def populate_trains(game: Game, route_ids: list[RouteId]):
    save_path = Path("./tmp/static_gtfs")
    gtfs_loader = GTFSLoader(save_path, verbose=False)
    gtfs_loader.fetch_static_supplemented_gtfs_data(skip_if_exists=True)
    game = construct_game(game, gtfs_loader, route_ids)
    return game
