from game_constants import ALL_ROUTE_IDS, BMT_ROUTE_IDS, IND_ROUTE_IDS, IRT_ROUTE_IDS
from interface import GameType, PopulateTrainsConfig


GAME_TYPE_TO_ROUTE_IDS = {
    GameType.GAME_TYPE_FREE_FOR_ALL: ALL_ROUTE_IDS,
    GameType.GAME_TYPE_IRT_SYSTEM: IRT_ROUTE_IDS,
    GameType.GAME_TYPE_BMT_SYSTEM: BMT_ROUTE_IDS,
    GameType.GAME_TYPE_IND_SYSTEM: IND_ROUTE_IDS,
}


DEFAULT_DEV_POPULATE_TRAINS_CONFIG: PopulateTrainsConfig = {
    "savedir": "./tmp/static_gtfs",
    "minTargetStopSequence": 5,
    "verboseStaticDataLoader": False,
    "overwriteStaticFiles": True,
    "verboseRecruiter": True,
}
