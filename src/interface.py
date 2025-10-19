"""
Python type definitions translated from headway.proto.
"""

from enum import StrEnum
from typing import NotRequired, TypedDict
from collections import namedtuple


class RouteId(StrEnum):
    """Route identifiers for NYC Subway lines."""

    ROUTE_ID_UNSPECIFIED = ""
    ROUTE_ID_1 = "1"
    ROUTE_ID_2 = "2"
    ROUTE_ID_3 = "3"
    ROUTE_ID_4 = "4"
    ROUTE_ID_5 = "5"
    ROUTE_ID_6 = "6"
    ROUTE_ID_7 = "7"
    ROUTE_ID_A = "A"
    ROUTE_ID_B = "B"
    ROUTE_ID_C = "C"
    ROUTE_ID_D = "D"
    ROUTE_ID_E = "E"
    ROUTE_ID_F = "F"
    ROUTE_ID_G = "G"
    ROUTE_ID_J = "J"
    ROUTE_ID_L = "L"
    ROUTE_ID_M = "M"
    ROUTE_ID_N = "N"
    ROUTE_ID_Q = "Q"
    ROUTE_ID_R = "R"
    ROUTE_ID_W = "W"
    ROUTE_ID_Z = "Z"


class GameType(StrEnum):
    """Types of games available."""

    GAME_TYPE_UNSPECIFIED = "GAME_TYPE_UNSPECIFIED"
    GAME_TYPE_IRT_SYSTEM = "GAME_TYPE_IRT_SYSTEM"  # All IRT trains
    GAME_TYPE_BMT_SYSTEM = "GAME_TYPE_BMT_SYSTEM"  # All BMT trains
    GAME_TYPE_IND_SYSTEM = "GAME_TYPE_IND_SYSTEM"  # All IND trains
    GAME_TYPE_SYSTEM_CHAMPIONSHIP = (
        "GAME_TYPE_SYSTEM_CHAMPIONSHIP"  # Best of each system competes
    )
    GAME_TYPE_FREE_FOR_ALL = "GAME_TYPE_FREE_FOR_ALL"  # All trains compete


class GameVariant(StrEnum):
    """Game timing variants."""

    GAME_VARIANT_UNSPECIFIED = "GAME_VARIANT_UNSPECIFIED"
    GAME_VARIANT_WEEKDAY = "GAME_VARIANT_WEEKDAY"
    GAME_VARIANT_WEEKEND = "GAME_VARIANT_WEEKEND"


class GameStatus(StrEnum):
    """Current status of a game."""

    GAME_STATUS_UNSPECIFIED = "GAME_STATUS_UNSPECIFIED"
    GAME_STATUS_NOT_STARTED = "GAME_STATUS_NOT_STARTED"
    GAME_STATUS_UNDERWAY = "GAME_STATUS_UNDERWAY"
    GAME_STATUS_FINISHED = "GAME_STATUS_FINISHED"


class TripStatus(StrEnum):
    """Current status of a train trip."""

    TRIP_STATUS_UNSPECIFIED = "TRIP_STATUS_UNSPECIFIED"
    TRIP_STATUS_NOT_SEEN_YET = "TRIP_STATUS_NOT_SEEN_YET"
    TRIP_STATUS_UNDERWAY = "TRIP_STATUS_UNDERWAY"
    TRIP_STATUS_DISAPPEARED = "TRIP_STATUS_DISAPPEARED"  # The trip appeared at some point, but no longer exists
    TRIP_STATUS_REACHED_TARGET = "TRIP_STATUS_REACHED_TARGET"


class RankingStatus(StrEnum):
    """Status of a train's ranking in a game."""

    RANKING_STATUS_UNSPECIFIED = "RANKING_STATUS_UNSPECIFIED"
    RANKING_STATUS_PENDING = "RANKING_STATUS_PENDING"
    RANKING_STATUS_RANKED = "RANKING_STATUS_RANKED"
    RANKING_STATUS_DISQUALIFIED = "RANKING_STATUS_DISQUALIFIED"


class User(TypedDict):
    """User account information."""

    user_id: str
    username: str
    user_password_hashed: str
    local_routes: list[RouteId]
    date_joined_iso: str
    num_tokens: int


class Stop(TypedDict):
    """Information about a stop on a train's route."""

    stop_id: str
    stop_name: str
    scheduled_arrival_time_s: int
    actual_arrival_time_s: NotRequired[int]


class TripData(TypedDict):
    """Data about a specific train trip."""

    trip_id: str
    trip_id_short: str
    trip_status: TripStatus
    stops: list[Stop]
    target_stop_id: str
    actual_target_arrival_time_s: int  # Duplicated from within stops for quick access


class Ranking(TypedDict):
    """Ranking information for a train in a game."""

    rank: NotRequired[int]  # 1 = first, 2 = second, etc.
    ranking_status: RankingStatus


class Train(TypedDict):
    """Complete information about a train in a game."""

    route_id: RouteId
    trip_data: TripData
    ranking: Ranking


class Game(TypedDict):
    """Complete information about a game."""

    game_id: str
    date_iso: str
    week_number: str
    game_type: GameType
    game_variant: GameVariant
    game_status: GameStatus
    scheduled_arrival_time_s: int
    trains: list[Train]


class Stake(TypedDict):
    """A user's bet on a game."""

    user_id: str
    game_id: str
    predicted_winner: RouteId
    stake_amount: int


class Pot(TypedDict):
    """Collection of all stakes for a game."""

    game_id: str
    stakes: list[Stake]
    paid_out: bool
    locked: bool


GameConfig = namedtuple(
    "GameTypeAndVariant",
    ["game_type", "game_variant", "start_time_hhmmss", "end_time_hhmmss"],
)
