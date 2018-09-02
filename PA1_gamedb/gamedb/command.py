import os
import pyparsing as pp
import readline
import sys

from .formatting import print_err
from .gamedb import GameDB
from .parser_base import pretty_print_parser_error
from .parser_gamedb import GameDBCommandParser

histfile = os.path.join(os.path.expanduser("~"), ".gamedb_history")


###############
# Main routine
###############


def main(database_path):
    """
    The interactive prompt loop for GameDB

    Parameters
    ----------
    database_path : str
        the path to pass to `sqlite.connect()`
    """
    gamedb = GameDB(database_path, parser_cls=GameDBCommandParser)

    # Load command history from file or create it if it doesn't exist
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        open(histfile, "wb").close()

    # Set maximum command history length
    readline.set_history_length(1000)

    # Suppress the fancy prompt if not being run interactively
    prompt = "gamedb> " if sys.stdin.isatty() else ""

    while True:
        try:
            line = input(prompt).lstrip()
        except EOFError:
            break
        finally:
            readline.append_history_file(1, histfile)

        if line:
            try:
                gamedb.parser.parse(line)
            except pp.ParseBaseException as e:
                print_err("Invalid input:\n" + pretty_print_parser_error(e))
