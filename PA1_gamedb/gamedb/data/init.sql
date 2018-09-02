-- Table of players

CREATE TABLE IF NOT EXISTS player(
    id INTEGER NOT NULL PRIMARY KEY,
    name STRING NOT NULL
);

-- Table of games

CREATE TABLE IF NOT EXISTS game(
    id INTEGER NOT NULL PRIMARY KEY,
    name STRING NOT NULL
);

-- Table of victories. Points are not optional.

CREATE TABLE IF NOT EXISTS victory(
    id INTEGER NOT NULL PRIMARY KEY,
    game_id INTEGER NOT NULL,
    name STRING NOT NULL,
    points INTEGER NOT NULL,
    FOREIGN KEY (game_id) REFERENCES game(id)
);

-- Mapping between player and game, with IGN

CREATE TABLE IF NOT EXISTS player_game(
    player_id INTEGER NOT NULL,
    game_id INTEGER NOT NULL,
    ign STRING,
    FOREIGN KEY (player_id) REFERENCES player(id),
    FOREIGN KEY (game_id) REFERENCES game(id),
    PRIMARY KEY (player_id, game_id)
);

-- Indexes for individual player_game columns

CREATE INDEX IF NOT EXISTS player_game_player_id_idx ON player_game(player_id);
CREATE INDEX IF NOT EXISTS player_game_game_id_idx ON player_game(game_id);

-- Mapping between player and victory. No game ID for normalization.

CREATE TABLE IF NOT EXISTS player_victory(
    player_id INTEGER NOT NULL,
    victory_id INTEGER NOT NULL,
    FOREIGN KEY (player_id) REFERENCES player(id),
    FOREIGN KEY (victory_id) REFERENCES victory(id),
    PRIMARY KEY (player_id, victory_id)
);

-- Indexes for individual player_victory columns

CREATE INDEX IF NOT EXISTS player_victory_player_id_idx ON player_victory(player_id);
CREATE INDEX IF NOT EXISTS player_victory_victory_id_idx ON player_victory(victory_id);

-- Mapping between players to define friendship. Each relationship
-- is stored once, and the left ID must be the lower value.

CREATE TABLE IF NOT EXISTS friendship_raw(
    left_side INTEGER NOT NULL,
    right_side INTEGER NOT NULL,
    CONSTRAINT friendship_constraint CHECK (
        left_side < right_side AND
        left_side != right_side
    ),
    FOREIGN KEY (left_side) REFERENCES player(id),
    FOREIGN KEY (right_side) REFERENCES player(id),
    PRIMARY KEY (left_side, right_side)
);

-- Indexes for each column due to compound primary key

CREATE INDEX IF NOT EXISTS friendship_left_side_idx ON friendship_raw(left_side);
CREATE INDEX IF NOT EXISTS friendship_right_side_idx ON friendship_raw(right_side);

-- A view for simple access to players on both sides of a friendship.
-- SQLite optimizes the WHERE clause here to have equivalent performance
-- to a regular SELECT FROM friendship_raw in terms of time complexity.

CREATE VIEW IF NOT EXISTS friendship(player_id, friend_id) AS
    SELECT 
        left_side AS player_id,
        right_side AS friend_id
    FROM friendship_raw
    UNION
    SELECT
        right_side AS player_id,
        left_side AS friend_id
    FROM friendship_raw;

-- A simple way to link friends on the order-enforced table.
-- The node IDs are always inserted in the correct order.
-- CAVEAT: the row count of a view insert is always 0, since
-- operations inside triggers aren't counted.

CREATE TRIGGER friendship_ordered_insert
    INSTEAD OF INSERT ON friendship BEGIN
        INSERT INTO friendship_raw (left_side, right_side)
        VALUES (
            MIN(NEW.player_id, NEW.friend_id),
            MAX(NEW.player_id, NEW.friend_id)
        );
    END;

-- A view to gather per-game scores and victory counts for each person/game combination.
-- If the player has an entry in player_game but no victories, their score is 0.
-- SQLite will optimize this query using any WHERE clause used.

CREATE VIEW IF NOT EXISTS per_game_totals_view(
    player_id, game_id, n_earned_victories, game_score
) AS SELECT 
        pg.player_id as player_id,
        pg.game_id as game_id,
        SUM(CASE WHEN v.id IS NULL THEN 0 ELSE 1 END) as n_earned_victories,
        COALESCE(SUM(v.points), 0) as game_score
    FROM player_game pg
        LEFT NATURAL JOIN player_victory pv
        LEFT JOIN victory v
            ON v.id = pv.victory_id AND v.game_id = pg.game_id
    GROUP BY pg.player_id, pg.game_id;
