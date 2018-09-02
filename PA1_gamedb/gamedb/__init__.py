import sys

assert sys.version_info >= (3, 6), "GameDB requires Python 3.6+"


# Top level convenience imports
from .command import main
from .formatting import row_counter, generate_numbered_table, print_err, get_initials
from .gamedb import GameDB
from .parser_base import CommandParser, pretty_print_parser_error, ParserCommand, decorate_command
from .parser_gamedb import GameDBCommandParser
