import argparse
from game_engine import GameEngine
from interfaces import GameEngineConfig


def parse_comma_separated_ints(value):
    """Parse comma-separated integers from a string."""
    if value.lower() in ("none", "null"):
        return None
    try:
        return [int(x.strip()) for x in value.split(",")]
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid comma-separated integers: '{value}'")


def parse_nullable_float(value):
    """Parse a float that can be explicitly set to None."""
    if value.lower() in ("none", "null"):
        return None
    try:
        return float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid float value: '{value}'")


def parse_nullable_int(value):
    """Parse an integer that can be explicitly set to None."""
    if value.lower() in ("none", "null"):
        return None
    try:
        return int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{value}'")


def create_argument_parser():
    parser = argparse.ArgumentParser(
        description="Metro Card Madness Game Engine",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Game timing arguments
    parser.add_argument(
        "--game-start-time-hours",
        "-s",
        type=parse_nullable_float,
        help="Hour to start the game (24-hour format, e.g. 17.0 for 5 PM). Use 'none' to disable.",
    )
    parser.add_argument(
        "--game-end-time-hours",
        "-e",
        type=parse_nullable_float,
        help="Hour to end the game (24-hour format, e.g. 20.0 for 8 PM). Use 'none' to disable.",
    )
    parser.add_argument(
        "--assignment-grace-period-minutes",
        "-g",
        type=int,
        default=30,
        help="Grace period in minutes for trip assignment",
    )

    # Game behavior arguments
    parser.add_argument(
        "--allowed-num-stops-to-finish",
        "-a",
        type=parse_comma_separated_ints,
        default="10,15,20,25",
        help="Comma-separated list of allowed number of stops to finish (e.g., '5,10,15'). Use 'none' to disable.",
    )
    parser.add_argument(
        "--min-num-stops-in-trip",
        "-m",
        type=int,
        default=10,
        help="Minimum number of stops required in a trip",
    )
    parser.add_argument(
        "--override-num-stops-to-finish",
        "-o",
        type=parse_nullable_int,
        help="Override the calculated number of stops to finish. Use 'none' to disable override.",
    )

    # Runtime arguments
    parser.add_argument(
        "--refresh-rate-seconds",
        "-r",
        type=int,
        default=30,
        help="How often to refresh game state in seconds",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--skip-write-to-db",
        "-x",
        action="store_true",
        help="Skip writing updates to the database (for testing)",
    )

    return parser


def create_config_from_args(args) -> GameEngineConfig:
    # Parse allowed_num_stops_to_finish if it's still a string (from default)
    allowed_stops = args.allowed_num_stops_to_finish
    if isinstance(allowed_stops, str):
        allowed_stops = parse_comma_separated_ints(allowed_stops)

    return GameEngineConfig(
        game_start_time_hours=args.game_start_time_hours,
        game_end_time_hours=args.game_end_time_hours,
        assignment_grace_period_minutes=args.assignment_grace_period_minutes,
        allowed_num_stops_to_finish=allowed_stops,
        min_num_stops_in_trip=args.min_num_stops_in_trip,
        override_num_stops_to_finish=args.override_num_stops_to_finish,
        refresh_rate_seconds=args.refresh_rate_seconds,
        verbose=args.verbose,
        skip_write_to_db=args.skip_write_to_db,
    )


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    config = create_config_from_args(args)

    if config.verbose:
        print("Starting Metro Card Madness with config:")
        print(f"  Game start time: {config.game_start_time_hours}")
        print(f"  Game end time: {config.game_end_time_hours}")
        print(
            f"  Assignment grace period: {config.assignment_grace_period_minutes} minutes"
        )
        print(f"  Allowed stops to finish: {config.allowed_num_stops_to_finish}")
        print(f"  Refresh rate: {config.refresh_rate_seconds} seconds")
        print(f"  Skip write to DB: {config.skip_write_to_db}")
        if config.override_num_stops_to_finish:
            print(f"  Override stops to finish: {config.override_num_stops_to_finish}")
        print()

    engine = GameEngine(config)
    engine.run_game_loop()


if __name__ == "__main__":
    main()
