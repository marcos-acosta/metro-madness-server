from datetime import datetime
from game_engine import GameEngine
from constants import DEV_GAME_CONFIG
import time


def main():
    engine = GameEngine(DEV_GAME_CONFIG)
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Update")
        engine.update()
        print()
        time.sleep(30)


if __name__ == "__main__":
    main()
