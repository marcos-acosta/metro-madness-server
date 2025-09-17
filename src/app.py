from game_engine import GameEngine
import time


def main():
    engine = GameEngine(verbose=True)
    while True:
        engine.update(bypass_hours=True)
        time.sleep(30)


if __name__ == "__main__":
    main()
