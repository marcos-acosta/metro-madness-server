import os

from interfaces import GameEngineConfig


TRANSITER_URL = os.getenv("TRANSITER_URL", "http://localhost:8080")

HOUR_NOON = 12
HOUR_5PM = HOUR_NOON + 5
HOUR_8PM = HOUR_NOON + 8

NYC_TIME_ZONE = "America/New_York"

MAX_MINUTES_SINCE_FIRST_STOP = 15

PROD_GAME_CONFIG: GameEngineConfig = {
    "game_start_time_hours": HOUR_5PM,
    "game_end_time_hours": HOUR_8PM,
    "assignment_grace_period_minutes": 30,
    "allowed_num_stops_to_finish": [10, 15, 20, 25],
    "min_num_stops_in_trip": 11,
    "verbose": True,
}

DEV_GAME_CONFIG: GameEngineConfig = {
    "assignment_grace_period_minutes": 30,
    "allowed_num_stops_to_finish": [10, 15, 20, 25],
    "min_num_stops_in_trip": 11,
    "ignore_game_time": True,
    "verbose": True,
    "skip_write_to_db": True,
}
