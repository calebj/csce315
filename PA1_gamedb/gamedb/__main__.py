import argparse

from .command import main

DEFAULT_DB = ":memory:"

parser = argparse.ArgumentParser(description="A gamer information database with a console UI.")
parser.add_argument(
    "database",
    nargs="?",
    default=DEFAULT_DB,
    help=f"The sqlite database to use. Defaults to {DEFAULT_DB}.",
)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.database == DEFAULT_DB:
        print(
            "NOTE: Connecting to a transient in-memory database. All data will be discarded upon exit."
        )

    main(args.database)
