from game_constants import WEEKDAY_NAMES
from gtfs_loader import GTFSLoader
from pathlib import Path
from datetime import date
from collections import defaultdict, namedtuple
import random
import pandas as pd

from interface import (
    PopulateTrainsConfig,
    RouteId,
    Stop,
    TripStatus,
    RankingStatus,
    Game,
    Train,
    TripData,
)

CandidateStopTime = namedtuple(
    "CandidateStopTime", ["scheduled_arrival_s", "trips_by_route"]
)


class TrainRecruiter:
    def __init__(self, config: PopulateTrainsConfig):
        self.config = config
        save_path = Path(config.get("savedir"))
        self.gtfs_loader = GTFSLoader(
            save_path, verbose=config.get("verboseStaticDataLoader")
        )
        self.gtfs_loader.fetch_static_supplemented_gtfs_data(
            skip_if_exists=(not config.get("overwriteStaticFiles"))
        )

    def _log(self, message: str):
        if self.config.get("verboseRecruiter"):
            print(f"[train recruiter] {message}")

    def recruit_trains(self, game: Game, route_ids: list[RouteId]) -> Game:
        game_date = date.fromisoformat(game.get("date_iso"))
        start_time = game.get("start_time_s")
        end_time = game.get("end_time_s")
        trips = self.gtfs_loader.load_csv_as_dataframe(
            "trips.txt", dtype={"route_id": str}
        )
        self._log(f"Num trips at load: {len(trips)}")

        # Filter trips that aren't in our desired list of routes
        trips = self._filter_trips_by_route_id(trips, route_ids)
        self._log(f"Num trips after route id filter: {len(trips)}")

        # Filter trips that have a regular schedule but don't cover the relevant day of the week
        calendar = self.gtfs_loader.load_csv_as_dataframe(
            "calendar.txt", dtype={"route_id": str, "start_date": str, "end_date": str}
        )
        trips_w_calendar = self._join_trips_with_calendar(trips, calendar)
        trips_w_calendar = self._filter_by_weekday(trips_w_calendar, game_date)
        self._log(f"Num trips after weekday filter: {len(trips_w_calendar)}")

        # Filter out trips that have removal exceptions on the game_date
        calendar_dates = self.gtfs_loader.load_csv_as_dataframe(
            "calendar_dates.txt", dtype={"date": str}
        )
        trips_filtered = self._filter_removed_trips(
            trips_w_calendar, calendar_dates, game_date
        )
        self._log(f"Num trips after filtering removed trips: {len(trips_filtered)}")

        # Filter out trips that don't have a regular schedule and were not added
        trips_filtered = self._filter_not_added_trips(
            trips_filtered, calendar_dates, game_date
        )
        self._log(f"Num trips after filtering dateless trips: {len(trips_filtered)}")

        # Load stop times
        stop_times = self.gtfs_loader.load_csv_as_dataframe("stop_times.txt")
        stop_times = self._add_numeric_stop_times(stop_times)
        self._log(f"Num stop times at load: {len(stop_times)}")

        # Filter stops by time
        stop_times_filtered = self._filter_stop_times_by_time(
            stop_times, start_time, end_time
        )
        self._log(f"Num stop times after time filter: {len(stop_times_filtered)}")

        # Join stop times with remaining trips (implicit filter by inner join)
        stop_times_for_trips = self._join_trips_with_stop_times(
            trips_filtered, stop_times_filtered
        )
        self._log(
            f"Num stop times after joining with trips: {len(stop_times_for_trips)}"
        )

        # TODO: Check / filter out duplicate trips (e.g. are there duplicate short trip ids?

        # Check the coverage of every possible scheduled stop time
        candidate_times = self._get_candidate_stop_times(
            stop_times_for_trips, start_time, end_time
        )
        # Narrow down to those that have the most unique routes (ideally all)
        best_candidate_times = self._get_best_candidate_stop_times(candidate_times)
        if len(candidate_times) == 0:
            raise Exception("No candidate times found")
        # Randomly choose the time
        selected_candidate_time = random.choice(best_candidate_times)
        self._log(
            f"Num unique routes in selected candidate time: {len(selected_candidate_time.trips_by_route)}"
        )

        # Convert to dict
        stops_data = self.gtfs_loader.load_csv_as_dataframe("stops.txt")
        game_dict = self._convert_selected_time_to_game_dict(
            selected_candidate_time, stop_times, stops_data
        )
        return game | game_dict

    def _get_short_trip_id_from_full_trip_id(self, trip_id: str) -> str:
        return "_".join(trip_id.split("_")[-2:])

    def _join_trips_with_calendar(
        self, trips: pd.DataFrame, calendar: pd.DataFrame
    ) -> pd.DataFrame:
        return trips.merge(calendar, how="left", on="service_id")

    def _filter_by_weekday(
        self, trips_w_calendar: pd.DataFrame, game_date: date
    ) -> pd.DataFrame:
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

    def _filter_removed_trips(
        self, df: pd.DataFrame, calendar_dates: pd.DataFrame, game_date: date
    ) -> pd.DataFrame:
        game_date_str = game_date.strftime("%Y%m%d")

        # Find service_ids that have exception_type == 2 on the specific game_date
        removed_on_game_date = calendar_dates[
            (calendar_dates["date"] == game_date_str)
            & (calendar_dates["exception_type"] == 2)
        ]["service_id"].unique()

        # Filter out trips with those service_ids
        mask = ~df["service_id"].isin(removed_on_game_date)
        return df[mask]

    def _filter_not_added_trips(
        self, df: pd.DataFrame, calendar_dates: pd.DataFrame, game_date: date
    ) -> pd.DataFrame:
        game_date_str = game_date.strftime("%Y%m%d")
        # Find service_ids that have exception_type == 1 on the specific game_date
        added_on_game_date = calendar_dates[
            (calendar_dates["date"] == game_date_str)
            & (calendar_dates["exception_type"] == 1)
        ]["service_id"].unique()
        # Only keep rows that either have start / end date data, or which were explicitly added
        mask = df["start_date"].notnull() | df["service_id"].isin(added_on_game_date)
        return df[mask]

    def _hhmmss_to_seconds(self, hhmmss: str) -> int:
        parts = hhmmss.split(":")
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

    def _add_numeric_stop_times(self, stop_times: pd.DataFrame) -> pd.DataFrame:
        stop_times["scheduled_arrival_s"] = stop_times["arrival_time"].apply(
            self._hhmmss_to_seconds
        )
        return stop_times

    def _filter_stop_times_by_time(
        self, stop_times: pd.DataFrame, start_time: int, end_time: int
    ) -> pd.DataFrame:
        mask = (stop_times["scheduled_arrival_s"] >= start_time) & (
            stop_times["scheduled_arrival_s"] <= end_time
        )
        return stop_times[mask]

    def _filter_trips_by_route_id(
        self, trips: pd.DataFrame, route_ids_to_keep: list[str]
    ) -> pd.DataFrame:
        return trips[trips["route_id"].isin(route_ids_to_keep)]

    def _join_trips_with_stop_times(
        self, trips: pd.DataFrame, stop_times: pd.DataFrame
    ) -> pd.DataFrame:
        return trips.merge(stop_times, how="inner", on="trip_id")

    def _get_possible_scheduled_times_in_window(
        self, start_time_s: int, end_time_s: int
    ):
        return range(start_time_s, end_time_s, 30)

    def _sort_and_filter_trips_per_route(self, trips: list):
        return sorted(trips, key=lambda t: t["stop_sequence"], reverse=True)[
            : self.config.get("maxTripsToKeep")
        ]

    def _get_candidate_stop_times(
        self, stop_times: pd.DataFrame, start_time_s: int, end_time_s: int
    ) -> list[CandidateStopTime]:
        candidate_times = []
        for scheduled_time in self._get_possible_scheduled_times_in_window(
            start_time_s, end_time_s
        ):
            matching_stop_times = stop_times[
                (stop_times["scheduled_arrival_s"] == scheduled_time)
                & (
                    stop_times["stop_sequence"]
                    >= self.config.get("minTargetStopSequence")
                )
            ]
            if len(matching_stop_times) == 0:
                continue
            trips_by_route = defaultdict(list)
            for _, row in matching_stop_times[
                ["route_id", "trip_id", "stop_id", "stop_sequence"]
            ].iterrows():
                trips_by_route[row["route_id"]].append(row.to_dict())
            for route_id, trips in trips_by_route.items():
                trips_by_route[route_id] = self._sort_and_filter_trips_per_route(trips)
            candidate_times.append(CandidateStopTime(scheduled_time, trips_by_route))
        return candidate_times

    def _get_best_candidate_stop_times(
        self, candidates: list[CandidateStopTime]
    ) -> list[CandidateStopTime]:
        if len(candidates) == 0:
            return []
        max_routes = max([len(candidate.trips_by_route) for candidate in candidates])
        return [
            candidate
            for candidate in candidates
            if len(candidate.trips_by_route) == max_routes
        ]

    def _get_stops_from_trip_id(
        self, trip_id: str, stop_times: pd.DataFrame, stops_data: pd.DataFrame
    ) -> list[Stop]:
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
                    "stop_sequence": int(row["stop_sequence"]),
                    "scheduled_arrival_time_s": row["scheduled_arrival_s"],
                }
            )
        return stops

    def _create_trip_data(
        self,
        trip: dict,
        stop_times: pd.DataFrame,
        stops_data: pd.DataFrame,
    ) -> TripData:
        """Create a TripData object from a trip dict."""
        stops = self._get_stops_from_trip_id(trip["trip_id"], stop_times, stops_data)
        target_stop = next((s for s in stops if s["stop_id"] == trip["stop_id"]), None)
        return {
            "trip_id": trip["trip_id"],
            "trip_id_short": self._get_short_trip_id_from_full_trip_id(trip["trip_id"]),
            "trip_status": TripStatus.TRIP_STATUS_NOT_SEEN_YET,
            "stops": stops,
            "target_stop": target_stop,
        }

    def _convert_selected_time_to_game_dict(
        self,
        stop_time: CandidateStopTime,
        stop_times: pd.DataFrame,
        stops_data: pd.DataFrame,
    ) -> Game:
        trains: list[Train] = []
        for route_id, trips in stop_time.trips_by_route.items():
            # trips is now a list of trip dicts, not a single trip
            candidate_trips = []
            for trip in trips:
                trip_data = self._create_trip_data(trip, stop_times, stops_data)
                candidate_trips.append(trip_data)

            train: Train = {
                "route_id": route_id,
                "candidate_trips": candidate_trips,
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
