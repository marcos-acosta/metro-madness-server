from enum import StrEnum
import os


TRANSITER_URL = os.getenv("TRANSITER_URL", "http://localhost:8080")


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
