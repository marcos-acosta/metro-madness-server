from game_engine import GameEngine
from interface import GameEngineConfig


def main():
    config: GameEngineConfig = {"verbose": True}
    game_engine = GameEngine(config)


if __name__ == "__main__":
    main()
