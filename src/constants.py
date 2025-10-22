import os


TRANSITER_URL = os.getenv("TRANSITER_URL", "http://localhost:8080")

HOUR_NOON = 12
HOUR_5PM = HOUR_NOON + 5
HOUR_8PM = HOUR_NOON + 8

SECONDS_PER_DAY = 24 * 60 * 60

NYC_TIME_ZONE = "America/New_York"

MAX_MINUTES_SINCE_FIRST_STOP = 15

NUM_MATCHES_PER_BRACKET = 21

MATCH_ID_DAY_CUTOFFS = [22, 21, 19, 15, 7]

PRE_START_REFRESH_TIME_SECONDS = 60

SUPPLEMENTED_STATIC_GTFS_URL = (
    "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_supplemented.zip"
)

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
