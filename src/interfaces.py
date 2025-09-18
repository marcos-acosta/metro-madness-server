from dataclasses import dataclass
from typing import TypedDict
from enum import StrEnum


class RouteId(StrEnum):
    ROUTE_1 = "1"
    ROUTE_2 = "2"
    ROUTE_3 = "3"
    ROUTE_4 = "4"
    ROUTE_5 = "5"
    ROUTE_6 = "6"
    ROUTE_7 = "7"
    ROUTE_A = "A"
    ROUTE_B = "B"
    ROUTE_C = "C"
    ROUTE_D = "D"
    ROUTE_E = "E"
    ROUTE_F = "F"
    ROUTE_G = "G"
    ROUTE_J = "J"
    ROUTE_L = "L"
    ROUTE_M = "M"
    ROUTE_N = "N"
    ROUTE_Q = "Q"
    ROUTE_R = "R"
    ROUTE_W = "W"
    ROUTE_Z = "Z"


class MatchStatus(StrEnum):
    NOT_YET_STARTED = "NOT_YET_STARTED"
    ONGOING = "ONGOING"
    ENDED = "ENDED"


class VictoryType(StrEnum):
    COIN_TOSS_BOTH_DQ = "COIN_TOSS_BOTH_DQ"
    COIN_TOSS_SAME_DELAY = "COIN_TOSS_SAME_DELAY"
    ONE_DQ = "ONE_DQ"
    FAIR_AND_SQUARE = "FAIR_AND_SQUARE"


class TripStatus(StrEnum):
    NOT_ASSIGNED = "NOT_ASSIGNED"
    ONGOING = "ONGOING"
    DQ_NEVER_ASSIGNED = "DQ_NEVER_ASSIGNED"
    DQ_TOOK_TOO_LONG = "DQ_TOOK_TOO_LONG"
    DQ_DISAPPEARED = "DQ_DISAPPEARED"
    DQ_NO_COMPETITOR = "DQ_NO_COMPETITOR"
    FINISHED = "FINISHED"


class MatchResult(TypedDict):
    winner: RouteId
    victoryType: VictoryType


class Stop(TypedDict):
    stopId: str
    stopName: str
    predictedTimeSeconds: int
    actualTimeSeconds: int | None
    delay: int | None


class TripData(TypedDict):
    routeId: str | None
    winnerMatchId: str | None
    tripStatus: TripStatus | None
    tripId: str | None
    stops: list[Stop] | None
    finalDelay: int | None


class MatchData(TypedDict):
    date: str
    matchStatus: MatchStatus
    matchResult: MatchResult | None
    competingTrips: list[TripData]
    numStopsToFinish: int | None


class Match(TypedDict):
    bracketId: str
    matchId: str
    matchData: MatchData


@dataclass
class GameEngineConfig:
    assignment_grace_period_minutes: int = 30
    allowed_num_stops_to_finish: list[int] = None
    refresh_rate_seconds: int = 30
    game_start_time_hours: float | None = None
    game_end_time_hours: float | None = None
    verbose: bool = False
    min_num_stops_in_trip: int = 10
    skip_write_to_db: bool = False
    override_num_stops_to_finish: int | None = None

    def __post_init__(self):
        if self.allowed_num_stops_to_finish is None:
            self.allowed_num_stops_to_finish = [10, 15, 20, 25]
