from interfaces import MatchData, Stop, TripData, TripStatus
from game_time import epoch_time_to_seconds_since_midnight_est
from constants import ALLOWED_NUM_STOPS_TO_FINISH


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
    return stop_times[0]["future"] == False and stop_times[1]["future"] == True


def getArrivalOrDepartureTime(transiterStopTime: dict) -> int:
    return int(
        transiterStopTime["arrival"]["time"]
        if "time" in transiterStopTime["arrival"]
        else transiterStopTime["departure"]["time"]
    )


def convertTransiterStopTimeToStop(transiterStopTime: dict) -> Stop:
    return {
        "stopId": transiterStopTime["stop"]["id"],
        "stopName": transiterStopTime["stop"]["name"],
        "predictedTimeSeconds": epoch_time_to_seconds_since_midnight_est(
            getArrivalOrDepartureTime(transiterStopTime)
        ),
    }


def copyTransiterDataToTripData(transiterTripData: dict, tripData: TripData) -> None:
    tripData["tripId"] = transiterTripData["id"]
    tripData["stops"] = [
        convertTransiterStopTimeToStop(stopTime)
        for stopTime in transiterTripData["stopTimes"]
    ]


def setFirstActualTimeToPredictedTime(tripData: TripData) -> None:
    stops = tripData["stops"]
    if stops and len(stops) > 0:
        stops[0]["actualTimeSeconds"] = stops[0]["predictedTimeSeconds"]
