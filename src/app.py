from datetime import datetime
from game_engine import GameEngine
from constants import DEV_GAME_CONFIG
import time


def main():
    engine = GameEngine(DEV_GAME_CONFIG)
    engine.run_game_loop()


if __name__ == "__main__":
    main()
