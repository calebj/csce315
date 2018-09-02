import pyparsing as pp
import sys

from .formatting import print_err
from .gamedb import GameDB
from .parser_base import pretty_print_parser_error
from .parser_gamedb import GameDBCommandParser

###############
# Main routine
###############


def main(database_uri: str = ":memory:"):
    gamedb = GameDB(database_uri, parser_cls=GameDBCommandParser)

    # Suppress the fancy prompt if not being run interactively
    prompt = "> " if sys.stdin.isatty() else ""

    while True:
        try:
            line = input(prompt).lstrip()
        except EOFError:
            break

        if line:
            try:
                gamedb.parser.parse(line)
            except pp.ParseBaseException as e:
                print_err("Invalid input:\n" + pretty_print_parser_error(e))
