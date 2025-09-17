from datetime import datetime
from game_engine import GameEngine
import time


def main():
    engine = GameEngine(verbose=True)
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Update")
        engine.update(bypass_hours=True)
        print()
        time.sleep(30)


if __name__ == "__main__":
    main()
