from interfaces import GameEngineConfig, RouteId
import os

TRANSITER_URL = os.getenv("TRANSITER_URL", "http://localhost:8080")

HOUR_NOON = 12
HOUR_5PM = HOUR_NOON + 5
HOUR_8PM = HOUR_NOON + 8

NYC_TIME_ZONE = "America/New_York"

MAX_MINUTES_SINCE_FIRST_STOP = 15

NUM_MATCHES_PER_BRACKET = 21

MATCH_ID_DAY_CUTOFFS = [22, 21, 19, 15, 7]

PRE_START_REFRESH_TIME_SECONDS = 60

MATCH_CONNECTIONS = {
    1: [None, None],
    2: [None, None],
    3: [None, None],
    4: [None, None],
    5: [None, None],
    6: [None, None],
    7: [None, None],
    8: [None, None],
    9: [None, 1],
    10: [None, 2],
    11: [None, 3],
    12: [None, 4],
    13: [None, 5],
    14: [None, 6],
    15: [9, 7],
    16: [10, 11],
    17: [12, 8],
    18: [13, 14],
    19: [15, 16],
    20: [17, 18],
    21: [19, 20],
}

VALID_STARTING_STARTING_IDS = {
    RouteId.ROUTE_1: [
        "101",
        "140",
        "142",
    ],
    RouteId.ROUTE_2: [],
    RouteId.ROUTE_A: [
        "A02",
        "A65",
        "H11",
    ],
    RouteId.ROUTE_C: [
        "112",
        "A55",
    ],
    RouteId.ROUTE_E: [
        "E01",
        "G05",
    ],
}
