from game_engine import GameEngine
from interface import GameEngineConfig


def main():
    config: GameEngineConfig = {"verbose": True, "refresh_rate_s": 30}
    game_engine = GameEngine(config)
    game_engine.run_game_loop()


if __name__ == "__main__":
    main()
