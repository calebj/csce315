import pyparsing as pp
from sqlite3 import IntegrityError

from .formatting import generate_numbered_table, get_initials, print_err
from .parser_base import CommandParser, decorate_command

###############################################
# ParseElements for the various argument types
###############################################

# A positive-only, unsigned integer (no + allowed)
ID_TOK = pp.Word(pp.nums).setParseAction(lambda l: int(l[0]))
ID_TOK.setName("unsigned integer")

# Any signed integer (-/+ allowed but optional)
OPT_SIGN = pp.Optional(pp.Word("+-", exact=1))
INT_TOK = (OPT_SIGN + ID_TOK).setParseAction(lambda l: int(l[0]))
INT_TOK.leaveWhitespace().setName("signed integer")

# Quoted string by spec, uncomment the rest to work on unquoted strings.
NAME_TOK = pp.QuotedString('"')  # | pp.Word(pp.alphas8bit + pp.printables)


class GameDBCommandParser(CommandParser):
    "The GameDB app command parser class. Contains all app-specific commands."

    @decorate_command("AddPlayer", player_id=ID_TOK, player_name=NAME_TOK)
    def cmd_add_player(self, player_id: int, player_name: str):
        """
        Add a player to the database.

        Usage: AddPlayer <Player ID> <Player Name>

        <Player ID> is a positive integer identifier for the player.
        <Player Name> is a string enclosed by double quotes ("Andruid Kerne").

        <Player Name> may contain special characters (excluding double quote).
        """
        with self.parent.db as conn:
            try:
                conn.execute(
                    "INSERT INTO player (id, name) VALUES (?, ?);", (player_id, player_name)
                )
                print(f"{player_name} added as Player #{player_id}.")
            except IntegrityError:
                print_err(f"Player #{player_id} already exists!")

    @decorate_command("AddGame", game_id=ID_TOK, game_name=NAME_TOK)
    def cmd_add_game(self, game_id: int, game_name: str):
        """
        Add game to the database.

        Usage: AddGame <Game ID> <Game Name>

        <Game ID> is a positive integer identifier for the game.
        <Game Name> is a string enclosed by double quotes (i.e. "Mirror's Edge").

        <Game Name> may contain special characters (excluding double quote).
        """
        with self.parent.db as conn:
            try:
                conn.execute("INSERT INTO game (id, name) VALUES (?, ?);", (game_id, game_name))
                print(f"{game_name} added as Game #{game_id}.")
            except IntegrityError:
                print_err(f"Game ID {game_id} already exists!")

    @decorate_command(
        "AddVictory", game_id=ID_TOK, victory_id=ID_TOK, victory_name=NAME_TOK, points=INT_TOK
    )
    def cmd_add_victory(self, game_id: int, victory_id: int, victory_name: str, points: int):
        """
        Add Victory to the game denoted by <Game ID>.

        Usage: AddVictory <Game ID> <Victory ID> <Victory Name> <Victory Points>

        <Victory ID> is an integer identifier for the Victory.
        <Victory Name> is a string enclosed by double quotes (i.e. "Head over heels").
        <Victory Points> is an integer indicating how many gamer points the Victory is worth.

        <Victory Name> may contain special characters (excluding double quote).
        """
        game_name = self.parent.get_game_name(game_id)

        if game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            try:
                conn.execute(
                    "INSERT INTO victory (id, game_id, name, points) VALUES (?, ?, ?, ?);",
                    (victory_id, game_id, victory_name, points),
                )
                print(f"'{victory_name}' added to {game_name} as Victory #{victory_id}.")
            except IntegrityError:
                print_err(f"Victory #{victory_id} already exists!")

    @decorate_command("Plays", player_id=ID_TOK, game_id=ID_TOK, player_ign=NAME_TOK)
    def cmd_plays(self, player_id: int, game_id: int, player_ign: str):
        """
        Add entry for player playing a specific game.

        Usage: Plays <Player ID> <Game ID> <Player IGN>

        <Player IGN> is a string identifier for that that player's particular
                     in-game name for the specified game, enclosed by double quotes.

        <Player IGN> may contain special characters (excluding double quote).
        """
        player_name = self.parent.get_player_name(player_id)
        game_name = self.parent.get_game_name(game_id)

        if player_name is None:
            print_err(f"Player #{player_id} is not in the database!")
            return
        elif game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            try:
                conn.execute(
                    "INSERT INTO player_game (player_id, game_id, ign) VALUES (?, ?, ?);",
                    (player_id, game_id, player_ign),
                )
                print(f"Added '{game_name}' to player {player_name}'s game list.")
            except IntegrityError:
                print_err(f"{game_name} is already in {player_name}'s game list!")

    @decorate_command("AddFriends", player1_id=ID_TOK, player2_id=ID_TOK)
    def cmd_add_friends(self, player1_id: int, player2_id: int):
        """
        Makes players 1 & 2 friends. Friends are mutual.

        Usage: AddFriends <Player ID1> <Player ID2>
        """
        player1_name = self.parent.get_player_name(player1_id)
        player2_name = self.parent.get_player_name(player2_id)

        if player1_name is None:
            print_err(f"Player #{player1_id} is not in the database!")
            return
        elif player2_name is None:
            print_err(f"Player #{player2_id} is not in the database!")
            return

        with self.parent.db as conn:
            try:
                conn.execute(
                    "INSERT INTO friendship (player_id, friend_id) VALUES (?, ?);",
                    (player1_id, player2_id),
                )
                print(f"{player1_name} and {player2_name} are now friends.")
            except IntegrityError:
                print_err(f"{player1_name} is already friends with {player2_name}.")

    @decorate_command("WinVictory", player_id=ID_TOK, game_id=ID_TOK, victory_id=ID_TOK)
    def cmd_win_victory(self, player_id: int, game_id: int, victory_id: int):
        """
        Adds Victory indicated to <Player ID>'s record.

        Each Victory can only be achieved by a given player for once.

        Usage: WinVictory <Player ID> <Game ID> <Victory ID>
        """
        player_name = self.parent.get_player_name(player_id)
        victory_name = self.parent.get_victory_name(victory_id, game_id=game_id)

        if player_name is None:
            print_err(f"Player #{player_id} is not in the database!")
            return
        elif victory_name is None:
            print_err(f"Victory #{victory_id} is not in the database!")
            return

        with self.parent.db as conn:
            try:
                conn.execute(
                    "INSERT INTO player_victory (player_id, victory_id) VALUES (?, ?);",
                    (player_id, victory_id),
                )
                print(f"Added '{victory_name}' to {player_name}'s victories.")
            except IntegrityError:
                print_err(f"{player_name} has already earned {victory_name}!")

    @decorate_command("FriendsWhoPlay", player_id=ID_TOK, game_id=ID_TOK)
    def cmd_friends_who_play(self, player_id: int, game_id: int):
        """
        Report which of player's friends play the specified game.

        Usage: FriendsWhoPlay <Player ID> <Game ID>
        """
        player_name = self.parent.get_player_name(player_id)
        game_name = self.parent.get_game_name(game_id)

        if player_name is None:
            print_err(f"Player #{player_id} is not in the database!")
            return
        elif game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            rows = conn.execute(
                "SELECT p.name, COALESCE(pgtv.game_score, 0)"
                "  FROM friendship f"
                "    INNER JOIN player p ON p.id = f.friend_id"
                "    LEFT JOIN per_game_totals_view pgtv"
                "      ON pgtv.player_id = f.friend_id"
                "  WHERE f.player_id = ? AND pgtv.game_id = ?"
                "  ORDER BY game_score DESC",
                (player_id, game_id),
            ).fetchall()

            if rows:
                print(f"\n{player_name}'s friends who play {game_name}:\n")
                print(generate_numbered_table(rows, headers=("Name", "Score")))
            else:
                print(f"\n{player_name} has no friends. :(")

    @decorate_command("ComparePlayers", player1_id=ID_TOK, player2_id=ID_TOK, game_id=ID_TOK)
    def cmd_compare_players(self, player1_id: int, player2_id: int, game_id: int):
        """
        Compares two players' Victory records for a game.

        Usage: ComparePlayers <Player ID1> <Player ID2> <Game ID>
        """
        # Query names by IDs
        player1_name = self.parent.get_player_name(player1_id)
        player2_name = self.parent.get_player_name(player2_id)
        game_name = self.parent.get_game_name(game_id)

        # Throw an error and return if any items are missing
        if player1_name is None:
            print_err(f"Player #{player1_id} is not in the database!")
            return
        elif player2_name is None:
            print_err(f"Player #{player2_id} is not in the database!")
            return
        elif game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            totals = conn.execute(
                "SELECT p.name, v.game_score"
                "  FROM per_game_totals_view v"
                "    INNER JOIN player p ON p.id = v.player_id"
                "  WHERE v.game_id = ? AND p.id IN (?, ?)"
                "  ORDER BY CASE WHEN p.id = ? THEN 0 ELSE 1 END",
                (game_id, player1_id, player2_id, player1_id),
            ).fetchall()

            print(f"Total scores for {game_name}:\n")
            print(generate_numbered_table(totals, headers=("Player", "Points")))

            victories = conn.execute(
                "SELECT"
                "    v.name,"
                "    v.points,"
                "    CASE WHEN pv1.victory_id IS NULL THEN 'N' ELSE 'Y' END,"
                "    CASE WHEN pv2.victory_id IS NULL THEN 'N' ELSE 'Y' END"
                "  FROM victory v"
                "    LEFT JOIN player_victory pv1"
                "      ON pv1.victory_id = v.id AND pv1.player_id = ?"
                "    LEFT JOIN player_victory pv2"
                "      ON pv2.victory_id = v.id AND pv2.player_id = ?"
                "  WHERE v.game_id = ?"
                "  ORDER BY v.name ASC, v.points DESC",
                (player1_id, player2_id, game_id),
            ).fetchall()

            if victories:
                print(f"\nVictories for {game_name}:\n")
                headers = [
                    "Victory",
                    "Points",
                    get_initials(player1_name),
                    get_initials(player2_name),
                ]
                print(generate_numbered_table(victories, headers=headers))
            else:
                print("No victories.")

    @decorate_command("SummarizePlayer", player_id=ID_TOK)
    def cmd_summarize_player(self, player_id: int):
        """
        Print all of player's friends, games, and point totals.

        Usage: SummarizePlayer <Player ID>
        """
        player_name = self.parent.get_player_name(player_id)

        if player_name is None:
            print(f"Player #{player_id} is not in the database!")
            return

        with self.parent.db as conn:
            friends = conn.execute(
                "SELECT p.name, SUM(COALESCE(pgtv.game_score, 0)) as score"
                "  FROM friendship f"
                "    JOIN player p ON p.id = f.friend_id"
                "    LEFT JOIN per_game_totals_view pgtv"
                "      ON pgtv.player_id = p.id"
                "  WHERE f.player_id = ?"
                "  GROUP BY p.id"
                "  ORDER BY score desc",
                (player_id,),
            ).fetchall()

            if friends:
                print(f"{player_name}'s friends:")
                print(generate_numbered_table(friends, headers=("Name", "Score")))
            else:
                print(f"{player_name} has no friends. :(")

            games = conn.execute(
                "SELECT"
                "    g.name,"
                "    pgtv.n_earned_victories || '/' || game_sum.vcount,"
                "    pgtv.game_score as score,"
                "    pg.ign"
                "  FROM per_game_totals_view pgtv"
                "    JOIN game g ON g.id = pgtv.game_id"
                "    NATURAL JOIN player_game pg"
                "    JOIN (SELECT game_id, COUNT(*) AS vcount FROM victory GROUP BY game_id)"
                "      AS game_sum ON g.id = game_sum.game_id"
                "  WHERE pgtv.player_id = ?"
                "  ORDER BY pgtv.game_score DESC",
                (player_id,),
            ).fetchall()

            if games:
                print(f"\n{player_name}'s games:")
                print(
                    generate_numbered_table(games, headers=("Name", "Victories", "Points", "IGN"))
                )
            else:
                print(f"{player_name} has no games in their library. :(")

            print(f"\n{player_name}'s total score:", sum(t[2] for t in games))

    @decorate_command("SummarizeGame", game_id=ID_TOK)
    def cmd_summarize_game(self, game_id: int):
        """
        Print a report of a game's players and victory stats.

        Usage: SummarizeGame <Game ID>
        """
        game_name = self.parent.get_game_name(game_id)

        if game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            victories = conn.execute(
                "SELECT v.name, v.points, COUNT(pv.victory_id)"
                "  FROM victory v"
                "    LEFT JOIN player_victory pv ON pv.victory_id = v.id"
                "  WHERE v.game_id = ?"
                "  GROUP BY v.id"
                "  ORDER BY v.points DESC, v.name ASC",
                (game_id,),
            ).fetchall()

            players = conn.execute(
                "SELECT p.name, pgtv.game_score, pgtv.n_earned_victories"
                "  FROM per_game_totals_view pgtv"
                "    JOIN player p ON p.id = pgtv.player_id"
                "  WHERE pgtv.game_id = ?"
                "  ORDER BY pgtv.game_score DESC, p.name ASC",
                (game_id,),
            ).fetchall()

            num_players = len(players)
            num_victories = len(victories)

            if victories:
                # Replace n_earned column with n_earned / n_players
                victories = [row[:-1] + (f"{row[-1]}/{num_players}",) for row in victories]
                print(f"Victories for {game_name}:")
                print(generate_numbered_table(victories, headers=("Name", "Points", "Players")))
            else:
                print(f"{game_name} has no Victories associated with it.")

            if players:
                # Replace n_earned column with n_earned / n_victories
                players = [row[:-1] + (f"{row[-1]}/{num_victories}",) for row in players]
                print(f"\nPlayers with {game_name} in their library:")
                print(generate_numbered_table(players, headers=("Name", "Points", "Victories")))
            else:
                print(f"\nNo players have {game_name} in their library.")

    @decorate_command("SummarizeVictory", game_id=ID_TOK, victory_id=ID_TOK)
    def cmd_summarize_victory(self, game_id: int, victory_id: int):
        """
        Print a report of a Victory's achievement records.

        Usage: SummarizeVictory <Game ID> <Victory ID>
        """
        game_name = self.parent.get_game_name(game_id)
        victory_name = self.parent.get_victory_name(victory_id, game_id)

        if game_name is None:
            print_err(f"Game #{game_id} is not in the database!")
            return
        elif victory_name is None:
            print_err(f"Victory #{victory_id} for game #{game_id} is not in the database!")
            return

        with self.parent.db as conn:
            total_players = conn.execute(
                "SELECT COUNT(*) FROM player_game pg WHERE pg.game_id = ?", (game_id,)
            ).fetchone()

            # column will always be present because aggregate functions always
            # return at least one row.
            total_players = total_players[0]

            rows = conn.execute(
                "SELECT p.name FROM player_victory pv"
                "    JOIN player p ON p.id = pv.player_id"
                "  WHERE pv.victory_id = ?",
                (victory_id,),
            ).fetchall()

            percent_earned = round(100 * len(rows) / total_players, 2)
            print(f"{percent_earned}% of all {game_name} players have earned {victory_name}:\n")

            if rows:
                print(generate_numbered_table(rows, headers=("Player", "Score")))
            else:
                print("No results.")

    @decorate_command("VictoryRanking")
    def cmd_victory_ranking(self):
        """
        Print a summary ranking all players by their points scored.

        Usage: VictoryRanking
        """
        with self.parent.db as conn:
            rows = conn.execute(
                "SELECT p.name, COALESCE(SUM(pgtv.game_score), 0)"
                "  FROM player p"
                "    LEFT JOIN per_game_totals_view pgtv ON pgtv.player_id = p.id"
                "  GROUP BY pgtv.player_id"
                "  ORDER BY game_score DESC"
            ).fetchall()

            if rows:
                print("Global leaderboard:\n")
                print(generate_numbered_table(rows, headers=("Player", "Total Score")))
            else:
                print("No results.")
