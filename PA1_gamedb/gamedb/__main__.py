import argparse

from .command import main

parser = argparse.ArgumentParser(description="A gamer information database with a console UI.")
parser.add_argument(
    "database", default=":memory:", help="The sqlite database to use. Defaults to :memory:"
)


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.database)
