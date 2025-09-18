from interfaces import GameEngineConfig, Stop, TripData, TripStatus
from game_time import (
    epoch_time_to_seconds_since_midnight_est,
    is_epoch_seconds_before_hour,
    minutes_since_epoch_seconds,
)
from constants import MAX_MINUTES_SINCE_FIRST_STOP


def isTripDisqualified(trip: TripData) -> bool:
    return trip.get("tripStatus") in [
        TripStatus.DQ_DISAPPEARED,
        TripStatus.DQ_NEVER_ASSIGNED,
        TripStatus.DQ_TOOK_TOO_LONG,
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
        and len(stop_times[1:]) >= config.get("allowed_num_stops_to_finish")[0]
        and stop_times[0].get("future") == False
        and stop_times[1].get("future") == True
        and (
            (
                not config.get("game_start_time_hours")
                and minutes_since_epoch_seconds(
                    first_stop_time <= MAX_MINUTES_SINCE_FIRST_STOP
                )
            )
            or (
                config.get("game_start_time_hours")
                and is_epoch_seconds_before_hour(
                    first_stop_time,
                    config.get("game_start_time_hours"),
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
        config.get("game_start_time_hours") * 3600
        + config.get("assignment_grace_period_minutes") * 60
    )
