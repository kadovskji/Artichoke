"""SQLite persistence: users, chat settings and finished rounds."""
import os
import sqlite3
import time

from i18n import DEFAULT_LANG

DB_FILE = os.environ.get("DB_FILE", "artichoke.db")

_db = sqlite3.connect(DB_FILE)
_db.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    started INTEGER NOT NULL DEFAULT 0);          -- 1 = pressed /start in private
CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id INTEGER PRIMARY KEY,
    lang TEXT NOT NULL DEFAULT 'en');
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER, ts INTEGER, mode TEXT,
    players INTEGER, moves_limit INTEGER, moves_total INTEGER, duration INTEGER,
    outcome TEXT,            -- solved | spy_win | caught | escaped | no_winner
    winner_team TEXT,        -- PSY-OPS winning team, if any
    identities TEXT);
CREATE TABLE IF NOT EXISTS round_players (
    round_id INTEGER, user_id INTEGER, name TEXT, role TEXT, team TEXT,
    won INTEGER, guessed INTEGER,   -- identities this player guessed
    caught INTEGER,                 -- 1 if unmasked as Dr. A
    moves INTEGER);
CREATE INDEX IF NOT EXISTS idx_rounds_chat ON rounds(chat_id);
CREATE INDEX IF NOT EXISTS idx_rp_user ON round_players(user_id);
CREATE INDEX IF NOT EXISTS idx_rp_round ON round_players(round_id);
""")
_db.commit()


def query(sql: str, params: tuple = ()) -> list[tuple]:
    return _db.execute(sql, params).fetchall()


# ---------------------------------------------------------------- users
def register_start(uid: int, name: str) -> None:
    """The user pressed /start in private: the bot may message them."""
    _db.execute(
        "INSERT INTO users (user_id, name, started) VALUES (?, ?, 1) "
        "ON CONFLICT(user_id) DO UPDATE SET name = excluded.name, started = 1",
        (uid, name))
    _db.commit()


def touch_user(uid: int, name: str) -> None:
    """Remember the latest display name of a user."""
    _db.execute(
        "INSERT INTO users (user_id, name, started) VALUES (?, ?, 0) "
        "ON CONFLICT(user_id) DO UPDATE SET name = excluded.name",
        (uid, name))
    _db.commit()


def has_started(uid: int) -> bool:
    rows = query("SELECT started FROM users WHERE user_id = ?", (uid,))
    return bool(rows and rows[0][0])


# ---------------------------------------------------------------- language
def get_lang(chat_id: int) -> str:
    rows = query("SELECT lang FROM chat_settings WHERE chat_id = ?", (chat_id,))
    return rows[0][0] if rows else DEFAULT_LANG


def set_lang(chat_id: int, lang: str) -> None:
    _db.execute(
        "INSERT INTO chat_settings (chat_id, lang) VALUES (?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET lang = excluded.lang",
        (chat_id, lang))
    _db.commit()


# ---------------------------------------------------------------- rounds
def record_round(g, outcome: str, winners: set[int], guessed: dict[int, int],
                 caught: bool, winner_team: str | None) -> None:
    """Store a finished round and the result of each participant."""
    moves = {u: g.moves_used.get(u, 0) for u in g.players}
    if g.spy is not None:
        moves[g.spy] = g.spy_used
    now = int(time.time())
    cur = _db.execute(
        "INSERT INTO rounds (chat_id, ts, mode, players, moves_limit, moves_total, "
        "duration, outcome, winner_team, identities) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (g.chat_id, now, g.mode, len(g.players), g.moves, sum(moves.values()),
         int(now - g.started_at), outcome, winner_team,
         " | ".join(i.title for i in g.identities.values())))
    rows = [
        (cur.lastrowid, uid, name, g.roles.get(uid), g.team.get(uid),
         int(uid in winners), guessed.get(uid, 0),
         int(caught and uid == g.dr_a), moves[uid])
        for uid, name in g.players.items()
    ]
    _db.executemany("INSERT INTO round_players VALUES (?,?,?,?,?,?,?,?,?)", rows)
    _db.commit()
