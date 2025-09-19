from random import sample
from interfaces import (
    GameEngineConfig,
    Match,
    MatchStatus,
    RouteId,
    Stop,
    TripData,
    TripStatus,
    VictoryType,
)
from game_time import (
    add_n_days,
    epoch_time_to_seconds_since_midnight_est,
    is_epoch_seconds_before_hour,
    minutes_since_epoch_seconds,
)
from constants import (
    MATCH_CONNECTIONS,
    MATCH_ID_DAY_CUTOFFS,
    MAX_MINUTES_SINCE_FIRST_STOP,
    NUM_MATCHES_PER_BRACKET,
)


def isTripDisqualified(trip: TripData) -> bool:
    return trip.get("tripStatus") in [
        TripStatus.DQ_DISAPPEARED,
        TripStatus.DQ_NEVER_ASSIGNED,
        TripStatus.DQ_TOOK_TOO_LONG,
        TripStatus.DQ_NO_COMPETITOR,
    ]


def isTripFinished(trip: TripData) -> bool:
    return trip.get("tripStatus") == TripStatus.FINISHED


def isTripComplete(trip: TripData) -> bool:
    return isTripFinished(trip) or isTripDisqualified(trip)


def hasTripAssigned(trip: TripData) -> bool:
    return trip.get("tripId") is not None and trip.get("stops") is not None


def isViableCompetingTrip(transiterTripData: dict, config: GameEngineConfig) -> bool:
    stop_times = transiterTripData.get("stopTimes", [])
    # Explicitly compare to boolean to avoid truthy / falsy nonsense
    first_stop_time = getArrivalOrDepartureTime(stop_times[0])
    return (
        stop_times
        and len(stop_times[1:]) >= config.allowed_num_stops_to_finish[0]
        and stop_times[0].get("future") == False
        and stop_times[1].get("future") == True
        and (
            (
                not config.game_start_time_hours
                and minutes_since_epoch_seconds(
                    first_stop_time <= MAX_MINUTES_SINCE_FIRST_STOP
                )
            )
            or (
                config.game_start_time_hours
                and is_epoch_seconds_before_hour(
                    first_stop_time,
                    config.game_start_time_hours,
                )
            )
        )
    )


def getArrivalOrDepartureTime(transiterStopTime: dict) -> int | None:
    stopTime = transiterStopTime.get("arrival", {}).get(
        "time"
    ) or transiterStopTime.get("departure", {}).get("time")
    return int(stopTime) if stopTime is not None else None


def convertTransiterStopTimeToStop(transiterStopTime: dict) -> Stop:
    return {
        "stopId": transiterStopTime.get("stop", {}).get("id"),
        "stopName": transiterStopTime.get("stop", {}).get("name"),
        "predictedTimeSeconds": epoch_time_to_seconds_since_midnight_est(
            getArrivalOrDepartureTime(transiterStopTime)
        ),
        "actualTimeSeconds": None,
    }


def copyTransiterDataToTripData(transiterTripData: dict, tripData: TripData) -> None:
    tripData["tripId"] = transiterTripData.get("id")
    tripData["stops"] = [
        convertTransiterStopTimeToStop(stopTime)
        for stopTime in transiterTripData.get("stopTimes", [])
    ]


def get_latest_assignment_time_seconds_est(config: GameEngineConfig) -> int:
    return (
        config.game_start_time_hours * 3600
        + config.assignment_grace_period_minutes * 60
    )


def create_random_bracket(week) -> list[Match]:
    route_ids = sample(list(RouteId), len(RouteId))
    route_index = 0
    matches = []
    for match_id in range(1, 1 + NUM_MATCHES_PER_BRACKET):
        num_days_to_add = 0
        for i, cutoff in enumerate(MATCH_ID_DAY_CUTOFFS):
            if match_id >= cutoff:
                num_days_to_add = 5 - i
                break
        date = add_n_days(week, num_days_to_add)
        match_connections = MATCH_CONNECTIONS[match_id]
        competing_trips: list[TripData] = []
        for connection in match_connections:
            if connection:
                competing_trips.append(
                    {
                        "winnerMatchId": str(connection),
                        "tripStatus": TripStatus.NOT_ASSIGNED,
                    }
                )
            else:
                competing_trips.append(
                    {
                        "routeId": route_ids[route_index],
                        "tripStatus": TripStatus.NOT_ASSIGNED,
                    }
                )
                route_index += 1
        match: Match = {
            "bracketId": week,
            "matchId": str(match_id),
            "matchData": {
                "competingTrips": competing_trips,
                "date": date,
                "matchStatus": MatchStatus.NOT_YET_STARTED,
            },
        }
        matches.append(match)
    return matches


def create_random_complete_bracket(week) -> list[Match]:
    route_ids = sample(list(RouteId), len(RouteId))
    route_index = 0
    matches: list[Match] = []
    for match_id in range(1, 1 + NUM_MATCHES_PER_BRACKET):
        num_days_to_add = 0
        for i, cutoff in enumerate(MATCH_ID_DAY_CUTOFFS):
            if match_id >= cutoff:
                num_days_to_add = 5 - i
                break
        date = add_n_days(week, num_days_to_add)
        match_connections = MATCH_CONNECTIONS[match_id]
        competing_trips: list[TripData] = []
        for connection in match_connections:
            if connection:
                competing_trips.append(
                    {
                        "winnerMatchId": str(connection),
                        "routeId": next(
                            (
                                match["matchData"]["matchResult"]["winner"]
                                for match in matches
                                if match["matchId"] == str(connection)
                            ),
                            None,
                        ),
                        "tripStatus": TripStatus.FINISHED,
                    }
                )
            else:
                competing_trips.append(
                    {
                        "routeId": route_ids[route_index],
                        "tripStatus": TripStatus.FINISHED,
                    }
                )
                route_index += 1
        match: Match = {
            "bracketId": week,
            "matchId": str(match_id),
            "matchData": {
                "competingTrips": competing_trips,
                "date": date,
                "matchStatus": MatchStatus.ENDED,
                "matchResult": {
                    "winner": competing_trips[0]["routeId"],
                    "victoryType": sample(list(VictoryType), 1)[0],
                },
            },
        }
        matches.append(match)
    return matches
