from interfaces import GameEngineConfig, Stop, TripData, TripStatus
from game_time import (
    epoch_time_to_seconds_since_midnight_est,
    is_epoch_seconds_before_hour,
    minutes_since_epoch_seconds,
)
from constants import MAX_MINUTES_SINCE_FIRST_STOP


def isTripComplete(trip: TripData) -> bool:
    return trip.get("tripStatus") in [
        TripStatus.DQ_DISAPPEARED,
        TripStatus.DQ_NEVER_ASSIGNED,
        TripStatus.DQ_TOOK_TOO_LONG,
        TripStatus.FINISHED,
    ]


def hasTripAssigned(trip: TripData) -> bool:
    return trip.get("tripId") is not None and trip.get("stops") is not None


def isViableCompetingTrip(transiterTripData: dict, config: GameEngineConfig) -> bool:
    stop_times = transiterTripData.get("stopTimes", [])
    # Explicitly compare to boolean to avoid truthy / falsy nonsense
    first_stop_time = getArrivalOrDepartureTime(stop_times[0])
    return (
        stop_times
        and len(stop_times) >= config.get("min_num_stops_in_trip")
        and stop_times[0].get("future") == False
        and stop_times[1].get("future") == True
        and (
            (
                config.get("ignore_game_time")
                and minutes_since_epoch_seconds(
                    first_stop_time <= MAX_MINUTES_SINCE_FIRST_STOP
                )
            )
            or is_epoch_seconds_before_hour(
                first_stop_time,
                config.get("game_start_time_hours"),
            )
        )
    )


def getArrivalOrDepartureTime(transiterStopTime: dict) -> int:
    return int(
        transiterStopTime.get("departure", {}).get("time")
        if transiterStopTime.get("departure", {}).get("time") is not None
        else transiterStopTime.get("arrival", {}).get("time")
    )


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
