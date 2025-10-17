from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RouteId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROUTE_ID_UNSPECIFIED: _ClassVar[RouteId]
    ROUTE_ID_1: _ClassVar[RouteId]
    ROUTE_ID_2: _ClassVar[RouteId]
    ROUTE_ID_3: _ClassVar[RouteId]
    ROUTE_ID_4: _ClassVar[RouteId]
    ROUTE_ID_5: _ClassVar[RouteId]
    ROUTE_ID_6: _ClassVar[RouteId]
    ROUTE_ID_7: _ClassVar[RouteId]
    ROUTE_ID_A: _ClassVar[RouteId]
    ROUTE_ID_B: _ClassVar[RouteId]
    ROUTE_ID_C: _ClassVar[RouteId]
    ROUTE_ID_D: _ClassVar[RouteId]
    ROUTE_ID_E: _ClassVar[RouteId]
    ROUTE_ID_F: _ClassVar[RouteId]
    ROUTE_ID_G: _ClassVar[RouteId]
    ROUTE_ID_J: _ClassVar[RouteId]
    ROUTE_ID_L: _ClassVar[RouteId]
    ROUTE_ID_M: _ClassVar[RouteId]
    ROUTE_ID_N: _ClassVar[RouteId]
    ROUTE_ID_Q: _ClassVar[RouteId]
    ROUTE_ID_R: _ClassVar[RouteId]
    ROUTE_ID_W: _ClassVar[RouteId]
    ROUTE_ID_Z: _ClassVar[RouteId]

class GameType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_TYPE_UNSPECIFIED: _ClassVar[GameType]
    GAME_TYPE_IRT_SYSTEM: _ClassVar[GameType]
    GAME_TYPE_BMT_SYSTEM: _ClassVar[GameType]
    GAME_TYPE_IND_SYSTEM: _ClassVar[GameType]
    GAME_TYPE_SYSTEM_CHAMPIONSHIP: _ClassVar[GameType]
    GAME_TYPE_FREE_FOR_ALL: _ClassVar[GameType]

class GameVariant(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_VARIANT_UNSPECIFIED: _ClassVar[GameVariant]
    GAME_VARIANT_WEEKDAY: _ClassVar[GameVariant]
    GAME_VARIANT_WEEKEND: _ClassVar[GameVariant]

class GameStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GAME_STATUS_UNSPECIFIED: _ClassVar[GameStatus]
    GAME_STATUS_NOT_STARTED: _ClassVar[GameStatus]
    GAME_STATUS_UNDERWAY: _ClassVar[GameStatus]
    GAME_STATUS_FINISHED: _ClassVar[GameStatus]

class TripStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRIP_STATUS_UNSPECIFIED: _ClassVar[TripStatus]
    TRIP_STATUS_NOT_SEEN_YET: _ClassVar[TripStatus]
    TRIP_STATUS_UNDERWAY: _ClassVar[TripStatus]
    TRIP_STATUS_DISAPPEARED: _ClassVar[TripStatus]
    TRIP_STATUS_REACHED_TARGET: _ClassVar[TripStatus]

class RankingStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RANKING_STATUS_UNSPECIFIED: _ClassVar[RankingStatus]
    RANKING_STATUS_PENDING: _ClassVar[RankingStatus]
    RANKING_STATUS_RANKED: _ClassVar[RankingStatus]
    RANKING_STATUS_DISQUALIFIED: _ClassVar[RankingStatus]
ROUTE_ID_UNSPECIFIED: RouteId
ROUTE_ID_1: RouteId
ROUTE_ID_2: RouteId
ROUTE_ID_3: RouteId
ROUTE_ID_4: RouteId
ROUTE_ID_5: RouteId
ROUTE_ID_6: RouteId
ROUTE_ID_7: RouteId
ROUTE_ID_A: RouteId
ROUTE_ID_B: RouteId
ROUTE_ID_C: RouteId
ROUTE_ID_D: RouteId
ROUTE_ID_E: RouteId
ROUTE_ID_F: RouteId
ROUTE_ID_G: RouteId
ROUTE_ID_J: RouteId
ROUTE_ID_L: RouteId
ROUTE_ID_M: RouteId
ROUTE_ID_N: RouteId
ROUTE_ID_Q: RouteId
ROUTE_ID_R: RouteId
ROUTE_ID_W: RouteId
ROUTE_ID_Z: RouteId
GAME_TYPE_UNSPECIFIED: GameType
GAME_TYPE_IRT_SYSTEM: GameType
GAME_TYPE_BMT_SYSTEM: GameType
GAME_TYPE_IND_SYSTEM: GameType
GAME_TYPE_SYSTEM_CHAMPIONSHIP: GameType
GAME_TYPE_FREE_FOR_ALL: GameType
GAME_VARIANT_UNSPECIFIED: GameVariant
GAME_VARIANT_WEEKDAY: GameVariant
GAME_VARIANT_WEEKEND: GameVariant
GAME_STATUS_UNSPECIFIED: GameStatus
GAME_STATUS_NOT_STARTED: GameStatus
GAME_STATUS_UNDERWAY: GameStatus
GAME_STATUS_FINISHED: GameStatus
TRIP_STATUS_UNSPECIFIED: TripStatus
TRIP_STATUS_NOT_SEEN_YET: TripStatus
TRIP_STATUS_UNDERWAY: TripStatus
TRIP_STATUS_DISAPPEARED: TripStatus
TRIP_STATUS_REACHED_TARGET: TripStatus
RANKING_STATUS_UNSPECIFIED: RankingStatus
RANKING_STATUS_PENDING: RankingStatus
RANKING_STATUS_RANKED: RankingStatus
RANKING_STATUS_DISQUALIFIED: RankingStatus

class User(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    USER_PASSWORD_HASHED_FIELD_NUMBER: _ClassVar[int]
    LOCAL_ROUTES_FIELD_NUMBER: _ClassVar[int]
    DATE_JOINED_ISO_FIELD_NUMBER: _ClassVar[int]
    NUM_TOKENS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    username: str
    user_password_hashed: str
    local_routes: _containers.RepeatedScalarFieldContainer[RouteId]
    date_joined_iso: str
    num_tokens: int
    def __init__(self, user_id: _Optional[str] = ..., username: _Optional[str] = ..., user_password_hashed: _Optional[str] = ..., local_routes: _Optional[_Iterable[_Union[RouteId, str]]] = ..., date_joined_iso: _Optional[str] = ..., num_tokens: _Optional[int] = ...) -> None: ...

class Stop(_message.Message):
    __slots__ = ()
    STOP_ID_FIELD_NUMBER: _ClassVar[int]
    STOP_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_ARRIVAL_TIME_S_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_ARRIVAL_TIME_S_FIELD_NUMBER: _ClassVar[int]
    stop_id: str
    stop_name: str
    scheduled_arrival_time_s: int
    actual_arrival_time_s: int
    def __init__(self, stop_id: _Optional[str] = ..., stop_name: _Optional[str] = ..., scheduled_arrival_time_s: _Optional[int] = ..., actual_arrival_time_s: _Optional[int] = ...) -> None: ...

class TripData(_message.Message):
    __slots__ = ()
    TRIP_ID_FIELD_NUMBER: _ClassVar[int]
    TRIP_STATUS_FIELD_NUMBER: _ClassVar[int]
    STOPS_FIELD_NUMBER: _ClassVar[int]
    TARGET_STOP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTUAL_TARGET_ARRIVAL_TIME_S_FIELD_NUMBER: _ClassVar[int]
    trip_id: str
    trip_status: TripStatus
    stops: _containers.RepeatedCompositeFieldContainer[Stop]
    target_stop_id: str
    actual_target_arrival_time_s: int
    def __init__(self, trip_id: _Optional[str] = ..., trip_status: _Optional[_Union[TripStatus, str]] = ..., stops: _Optional[_Iterable[_Union[Stop, _Mapping]]] = ..., target_stop_id: _Optional[str] = ..., actual_target_arrival_time_s: _Optional[int] = ...) -> None: ...

class Ranking(_message.Message):
    __slots__ = ()
    RANK_FIELD_NUMBER: _ClassVar[int]
    RANKING_STATUS_FIELD_NUMBER: _ClassVar[int]
    rank: int
    ranking_status: RankingStatus
    def __init__(self, rank: _Optional[int] = ..., ranking_status: _Optional[_Union[RankingStatus, str]] = ...) -> None: ...

class Train(_message.Message):
    __slots__ = ()
    ROUTE_ID_FIELD_NUMBER: _ClassVar[int]
    TRIP_DATA_FIELD_NUMBER: _ClassVar[int]
    RANKING_FIELD_NUMBER: _ClassVar[int]
    route_id: RouteId
    trip_data: TripData
    ranking: Ranking
    def __init__(self, route_id: _Optional[_Union[RouteId, str]] = ..., trip_data: _Optional[_Union[TripData, _Mapping]] = ..., ranking: _Optional[_Union[Ranking, _Mapping]] = ...) -> None: ...

class Game(_message.Message):
    __slots__ = ()
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_ISO_FIELD_NUMBER: _ClassVar[int]
    WEEK_NUMER_FIELD_NUMBER: _ClassVar[int]
    GAME_TYPE_FIELD_NUMBER: _ClassVar[int]
    GAME_VARIANT_FIELD_NUMBER: _ClassVar[int]
    GAME_STATUS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULED_ARRIVAL_TIME_S_FIELD_NUMBER: _ClassVar[int]
    TRAINS_FIELD_NUMBER: _ClassVar[int]
    game_id: str
    date_iso: str
    week_numer: str
    game_type: GameType
    game_variant: GameVariant
    game_status: GameStatus
    scheduled_arrival_time_s: int
    trains: _containers.RepeatedCompositeFieldContainer[Train]
    def __init__(self, game_id: _Optional[str] = ..., date_iso: _Optional[str] = ..., week_numer: _Optional[str] = ..., game_type: _Optional[_Union[GameType, str]] = ..., game_variant: _Optional[_Union[GameVariant, str]] = ..., game_status: _Optional[_Union[GameStatus, str]] = ..., scheduled_arrival_time_s: _Optional[int] = ..., trains: _Optional[_Iterable[_Union[Train, _Mapping]]] = ...) -> None: ...

class Stake(_message.Message):
    __slots__ = ()
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_WINNER_FIELD_NUMBER: _ClassVar[int]
    STAKE_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    game_id: str
    predicted_winner: RouteId
    stake_amount: int
    def __init__(self, user_id: _Optional[str] = ..., game_id: _Optional[str] = ..., predicted_winner: _Optional[_Union[RouteId, str]] = ..., stake_amount: _Optional[int] = ...) -> None: ...

class Pot(_message.Message):
    __slots__ = ()
    GAME_ID_FIELD_NUMBER: _ClassVar[int]
    STAKES_FIELD_NUMBER: _ClassVar[int]
    PAID_OUT_FIELD_NUMBER: _ClassVar[int]
    LOCKED_FIELD_NUMBER: _ClassVar[int]
    game_id: str
    stakes: _containers.RepeatedCompositeFieldContainer[Stake]
    paid_out: bool
    locked: bool
    def __init__(self, game_id: _Optional[str] = ..., stakes: _Optional[_Iterable[_Union[Stake, _Mapping]]] = ..., paid_out: _Optional[bool] = ..., locked: _Optional[bool] = ...) -> None: ...
