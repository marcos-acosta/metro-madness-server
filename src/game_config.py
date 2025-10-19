from game_constants import ALL_ROUTE_IDS, BMT_ROUTE_IDS, IND_ROUTE_IDS, IRT_ROUTE_IDS
from interface import GameType, GameConfig, GameVariant


GAME_SCHEDULE = {
    # 0 = Monday
    0: GameConfig(
        game_type=GameType.GAME_TYPE_FREE_FOR_ALL,
        game_variant=GameVariant.GAME_VARIANT_WEEKDAY,
        start_time_hhmmss="17:00:00",
        end_time_hhmmss="19:00:00",
    ),
    # 1 = Tuesday
    1: GameConfig(
        game_type=GameType.GAME_TYPE_IRT_SYSTEM,
        game_variant=GameVariant.GAME_VARIANT_WEEKDAY,
        start_time_hhmmss="17:00:00",
        end_time_hhmmss="19:00:00",
    ),
    # 2 = Wednesday
    2: GameConfig(
        game_type=GameType.GAME_TYPE_BMT_SYSTEM,
        game_variant=GameVariant.GAME_VARIANT_WEEKDAY,
        start_time_hhmmss="17:00:00",
        end_time_hhmmss="19:00:00",
    ),
    # 3 = Thursday
    3: GameConfig(
        game_type=GameType.GAME_TYPE_IND_SYSTEM,
        game_variant=GameVariant.GAME_VARIANT_WEEKDAY,
        start_time_hhmmss="17:00:00",
        end_time_hhmmss="19:00:00",
    ),
    # 4 = Friday
    4: GameConfig(
        game_type=GameType.GAME_TYPE_SYSTEM_CHAMPIONSHIP,
        game_variant=GameVariant.GAME_VARIANT_WEEKDAY,
        start_time_hhmmss="17:00:00",
        end_time_hhmmss="19:00:00",
    ),
    # 5 = Saturday
    5: None,
    # 6 = Sunday
    6: None,
}

GAME_TYPE_TO_ROUTE_IDS = {
    GameType.GAME_TYPE_FREE_FOR_ALL: ALL_ROUTE_IDS,
    GameType.GAME_TYPE_IRT_SYSTEM: IRT_ROUTE_IDS,
    GameType.GAME_TYPE_BMT_SYSTEM: BMT_ROUTE_IDS,
    GameType.GAME_TYPE_IND_SYSTEM: IND_ROUTE_IDS,
}
