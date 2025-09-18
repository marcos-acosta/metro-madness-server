from interfaces import GameEngineConfig
import os

TRANSITER_URL = os.getenv("TRANSITER_URL", "http://localhost:8080")

HOUR_NOON = 12
HOUR_5PM = HOUR_NOON + 5
HOUR_8PM = HOUR_NOON + 8

NYC_TIME_ZONE = "America/New_York"

MAX_MINUTES_SINCE_FIRST_STOP = 15

NUM_MATCHES_PER_BRACKET = 21

MATCH_ID_DAY_CUTOFFS = [22, 21, 19, 15, 7]

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

PROD_GAME_CONFIG: GameEngineConfig = {
    "game_start_time_hours": HOUR_5PM,
    "game_end_time_hours": HOUR_8PM,
    "assignment_grace_period_minutes": 30,
    "allowed_num_stops_to_finish": [10, 15, 20, 25],
    "verbose": True,
    "refresh_rate_seconds": 30,
}

DEV_GAME_CONFIG: GameEngineConfig = {
    "assignment_grace_period_minutes": 30,
    "allowed_num_stops_to_finish": [10, 15, 20, 25],
    "verbose": True,
    # "skip_write_to_db": True,
    "refresh_rate_seconds": 30,
    "override_num_stops_to_finish": 2,
}
