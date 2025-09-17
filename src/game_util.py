from interfaces import Stop, TripData, TripStatus
from game_time import (
    epoch_time_to_seconds_since_midnight_est,
    minutes_since_epoch_seconds,
)
from constants import MAX_MINUTES_SINCE_FIRST_STOP, MIN_NUM_STOPS


def isTripComplete(trip: TripData) -> bool:
    return trip["tripStatus"] in [
        TripStatus.DQ_DISAPPEARED,
        TripStatus.DQ_NEVER_ASSIGNED,
        TripStatus.DQ_TOOK_TOO_LONG,
        TripStatus.FINISHED,
    ]


def hasTripAssigned(trip: TripData) -> bool:
    return "tripId" in trip and "stops" in trip


def isTripOnWayToFirstStation(transiterTripData: dict) -> bool:
    stop_times = transiterTripData["stopTimes"]
    # Explicitly compare to boolean to avoid truthy / falsy nonsense
    return (
        stop_times
        and len(stop_times) >= MIN_NUM_STOPS
        and stop_times[0]["future"] == False
        and stop_times[1]["future"] == True
        and minutes_since_epoch_seconds(getArrivalOrDepartureTime(stop_times[0]))
        <= MAX_MINUTES_SINCE_FIRST_STOP
    )


def getArrivalOrDepartureTime(transiterStopTime: dict) -> int:
    return int(
        transiterStopTime["departure"]["time"]
        if "time" in transiterStopTime["departure"]
        else transiterStopTime["arrival"]["time"]
    )


def convertTransiterStopTimeToStop(transiterStopTime: dict) -> Stop:
    return {
        "stopId": transiterStopTime["stop"]["id"],
        "stopName": transiterStopTime["stop"]["name"],
        "predictedTimeSeconds": epoch_time_to_seconds_since_midnight_est(
            getArrivalOrDepartureTime(transiterStopTime)
        ),
        "actualTimeSeconds": None,
    }


def copyTransiterDataToTripData(transiterTripData: dict, tripData: TripData) -> None:
    tripData["tripId"] = transiterTripData["id"]
    tripData["stops"] = [
        convertTransiterStopTimeToStop(stopTime)
        for stopTime in transiterTripData["stopTimes"]
    ]
