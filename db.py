"""SQLite persistence: users, group settings, known groups and finished rounds."""
import logging
import os
import sqlite3
import time

DB_FILE = os.environ.get("DB_FILE", "artichoke.db")
LOG = logging.getLogger("artichoke.game")

DEFAULT_SETTINGS = {"lang": "en", "breaks": "on", "attempts": "auto", "dra": "random",
                    "variants": "off"}
ALLOWED_SETTINGS = {
    "lang": ("en", "it"),
    "breaks": ("on", "admins", "off"),      # who can use /hold
    "attempts": ("auto", "creator"),        # moves per person: computed, or chosen by the creator
    "dra": ("random", "always"),            # Dr. A: 30% chance of being absent, or always present
    "variants": ("off", "on"),              # special (non-random) game variants
}

_db = sqlite3.connect(DB_FILE)
_db.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    started INTEGER NOT NULL DEFAULT 0);          -- 1 = pressed /start in private
CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id INTEGER PRIMARY KEY,
    lang TEXT NOT NULL DEFAULT 'en');
CREATE TABLE IF NOT EXISTS known_chats (          -- groups where the bot is (or was) present
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER, ts INTEGER, mode TEXT,
    players INTEGER, moves_limit INTEGER, moves_total INTEGER, duration INTEGER,
    outcome TEXT,            -- solved | team_win | skip_win | vote_ok | vote_fail | no_winner
    winner_team TEXT,        -- Stargate winning team, if any
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


def _add_column(table: str, column: str, ddl: str) -> None:
    cols = {r[1] for r in _db.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        _db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


# Migrations from older versions
_add_column("chat_settings", "breaks", "TEXT NOT NULL DEFAULT 'on'")
_add_column("chat_settings", "attempts", "TEXT NOT NULL DEFAULT 'auto'")
_add_column("chat_settings", "dra", "TEXT NOT NULL DEFAULT 'random'")
_add_column("chat_settings", "variants", "TEXT NOT NULL DEFAULT 'off'")
_add_column("rounds", "variant", "TEXT")
_add_column("round_players", "solve_moves", "INTEGER")

# Rounds played with the old modes (enigma / psyops) follow different rules: drop them.
_legacy = _db.execute("SELECT COUNT(*) FROM rounds WHERE mode IN ('enigma', 'psyops')").fetchone()[0]
if _legacy:
    _db.execute("DELETE FROM round_players WHERE round_id IN "
                "(SELECT id FROM rounds WHERE mode IN ('enigma', 'psyops'))")
    _db.execute("DELETE FROM rounds WHERE mode IN ('enigma', 'psyops')")
    LOG.info("removed %d rounds played with the old game modes", _legacy)

# Groups seen by older versions (settings or finished rounds) are assumed to still have the bot;
# if one doesn't, the first announcement marks it inactive.
_db.execute("INSERT OR IGNORE INTO known_chats (chat_id, title, active) "
            "SELECT chat_id, NULL, 1 FROM chat_settings WHERE chat_id < 0")
_db.execute("INSERT OR IGNORE INTO known_chats (chat_id, title, active) "
            "SELECT DISTINCT chat_id, NULL, 1 FROM rounds WHERE chat_id < 0")
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


# ---------------------------------------------------------------- group settings
def get_settings(chat_id: int) -> dict:
    rows = query("SELECT lang, breaks, attempts, dra, variants FROM chat_settings WHERE chat_id = ?",
                 (chat_id,))
    if not rows:
        return dict(DEFAULT_SETTINGS)
    return dict(zip(("lang", "breaks", "attempts", "dra", "variants"), rows[0]))


def get_lang(chat_id: int) -> str:
    return get_settings(chat_id)["lang"]


def set_setting(chat_id: int, key: str, value: str) -> bool:
    """Change one group setting. Returns False if key or value are not valid."""
    if value not in ALLOWED_SETTINGS.get(key, ()):
        return False
    _db.execute("INSERT OR IGNORE INTO chat_settings (chat_id) VALUES (?)", (chat_id,))
    _db.execute(f"UPDATE chat_settings SET {key} = ? WHERE chat_id = ?", (value, chat_id))
    _db.commit()
    return True


# ---------------------------------------------------------------- known groups
def track_chat(chat_id: int, title: str | None) -> None:
    """Remember a group where the bot is present (used for admin announcements)."""
    _db.execute(
        "INSERT INTO known_chats (chat_id, title, active) VALUES (?, ?, 1) "
        "ON CONFLICT(chat_id) DO UPDATE SET title = excluded.title, active = 1",
        (chat_id, title))
    _db.commit()


def set_chat_active(chat_id: int, active: bool, title: str | None = None) -> None:
    _db.execute(
        "INSERT INTO known_chats (chat_id, title, active) VALUES (?, ?, ?) "
        "ON CONFLICT(chat_id) DO UPDATE SET active = excluded.active",
        (chat_id, title, int(active)))
    _db.commit()


def chats_by_lang(lang: str) -> list[int]:
    """Active groups whose language is `lang` (groups without settings use English)."""
    rows = query(
        "SELECT k.chat_id FROM known_chats k LEFT JOIN chat_settings s ON s.chat_id = k.chat_id "
        "WHERE k.active = 1 AND COALESCE(s.lang, 'en') = ?", (lang,))
    return [r[0] for r in rows]


# ---------------------------------------------------------------- rounds
def record_round(g, outcome: str, winners: set[int], caught: bool,
                 winner_team: str | None) -> None:
    """Store a finished round and the result of each participant."""
    moves = {u: g.total_moves.get(u, 0) + g.moves_used.get(u, 0) for u in g.players}
    if g.skip is not None:
        moves[g.skip] += g.skip_used
    now = int(time.time())
    cur = _db.execute(
        "INSERT INTO rounds (chat_id, ts, mode, players, moves_limit, moves_total, "
        "duration, outcome, winner_team, identities, variant) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (g.chat_id, now, g.mode, len(g.players), g.moves, sum(moves.values()),
         int(now - g.started_at), outcome, winner_team,
         " | ".join(i.title for i in g.used_identities), g.variant))
    rows = [
        (cur.lastrowid, uid, name, g.roles.get(uid), g.team.get(uid),
         int(uid in winners), g.guessed.get(uid, 0),
         int(caught and uid == g.dr_a), moves[uid], g.solve_moves.get(uid))
        for uid, name in g.players.items()
    ]
    _db.executemany("INSERT INTO round_players "
                    "(round_id, user_id, name, role, team, won, guessed, caught, moves, "
                    "solve_moves) VALUES (?,?,?,?,?,?,?,?,?,?)", rows)
    _db.commit()
