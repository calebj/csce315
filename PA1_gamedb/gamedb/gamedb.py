import pkg_resources
import sqlite3
from typing import Type, Optional

from .formatting import get_initials
from .parser_base import CommandParser
from .parser_gamedb import GameDBCommandParser


# Load DDL from bundled package data
init_sql = pkg_resources.resource_string(__name__, "data/init.sql").decode()


class GameDB:
    """
    The main GameDB application instance class.

    Parameters
    ----------
    database_path : str
        The URI to connect to with SQLite. Pass ":memory:" to use in-memory DB.
    parser_cls : Optional[Type[CommandParser]]
        The class containing the parser commands. Must be a subclass of CommandParser.

    Attributes
    ----------
    db : sqlite3.Connection
        The connection to the app's database.
    parser : CommandParser
        The command parser instance.
    """

    def __init__(
        self, database_path: str, parser_cls: Type[CommandParser] = GameDBCommandParser
    ) -> None:
        # The database connection handle
        self.db = sqlite3.connect(database_path)

        # Turn on foreign keys and execute DDL script
        self.db.execute("PRAGMA foreign_keys = ON;")
        self.db.executescript(init_sql)

        # Register initials(str) function
        self.db.create_function("initials", 1, get_initials)

        # Instantiate the command parser
        self.parser = parser_cls(parent=self)

    ###################
    # Helper functions
    ###################

    def get_game_name(self, game_id: int) -> Optional[str]:
        "Returns the name associated with a game ID, or None if not found."
        row = self.db.execute("SELECT name FROM game WHERE id = ?", (game_id,)).fetchone()

        return row[0] if row else None

    def get_player_name(self, player_id: int) -> Optional[str]:
        "Returns the name associated with a player ID, or None if not found."
        row = self.db.execute("SELECT name FROM player WHERE id = ?", (player_id,)).fetchone()

        return row[0] if row else None

    def get_victory_name(self, victory_id: int, game_id: int = None) -> Optional[str]:
        "Returns the name associated with a victory ID (and optional game), or None if not found."
        sql = "SELECT name FROM victory WHERE id = ? "
        params = [victory_id]

        if game_id is not None:
            sql += "AND game_id = ?"
            params.append(game_id)

        row = self.db.execute(sql, params).fetchone()

        return row[0] if row else None
