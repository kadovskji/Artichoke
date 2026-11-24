"""Shared game model, registry, timers and helpers."""
import logging
import re
import time
import unicodedata
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

from telegram.error import TelegramError

from i18n import T

LOG = logging.getLogger("artichoke.game")     # game events end up in the log file

# ---------------------------------------------------------------- modes
ARTICHOKE = "artichokemode"     # one patient K, researchers, maybe Dr. A
STARGATE = "stargatemode"       # teams race to identify K's identities
MODES = (ARTICHOKE, STARGATE)

# Special (non-random) variants: the creator of the round gets a fixed role.
RANDOM, MUNCHAUSEN, PSYCHOSIS = "random", "munchausen", "psychosis"
VARIANTS = {ARTICHOKE: (RANDOM, MUNCHAUSEN),    # Munchausen: the creator is Patient K
            STARGATE: (RANDOM, PSYCHOSIS)}      # Psychosis: the creator is Agent Skip

TEAM_NAMES = ("Grill Flame", "Center Lane", "Sun Streak", "Gondola Wish")
TEAM_COUNTS = (2, 3, 4)
SECRET_MAX_TRIES = 3            # private identity guesses of Skip / Dr. A
SECRET_COOLDOWN = 30            # seconds between two of them
SKIP_MAX_TRIES = 2              # Stargate: arrests Agent Skip can hold at once

DR_A_MIN_PLAYERS = 5            # Artichoke: Dr. A and the final vote need this many players
DR_A_PRESENCE = {"never": 0.0, "30": 0.3, "50": 0.5, "70": 0.7, "always": 1.0}  # /settings
PREDICT_MAX = 7                 # max names Dr. A can predict
PREDICT_SECONDS_PER_NAME = 25   # time to write them: this many seconds per allowed name
PREDICT_REMINDERS = (30, 15)    # reminders in the group: seconds left before the questions open

MOVE_OPTIONS = (5, 7, 10, 15, 20)   # moves per person when the round creator chooses them

# Timings, in seconds
CONFIG_SECONDS = 120        # creator must pick mode / teams / moves
LOBBY_SECONDS = 300         # sign-up window
CHOICE_SECONDS = 120        # K must pick an identity
ANSWER_SECONDS = 300        # K must answer a question
INACTIVITY_SECONDS = 600    # the round ends after this much inactivity
VOTE_SECONDS = 90           # Dr. A vote
FINAL_SECONDS = 90          # Stargate: Agent Skip's last chance to arrest K after the round is over
WAIT_MAX_MINUTES = 10       # max extension per /wait
HOLD_MAX_MINUTES = 10       # max length of a single /hold
HOLD_TOTAL_SECONDS = 1800   # max total pause time per round

# Roles
PATIENT, RESEARCHER, DR_A, SKIP = "patient", "researcher", "dr_a", "skip"


class Phase(Enum):
    MODE = auto()       # creator picks the mode
    VARIANT = auto()    # creator picks random or a special variant (if the group allows it)
    TEAMS = auto()      # Stargate: creator picks the number of teams
    MOVES = auto()      # creator picks the moves per person (if the group allows it)
    LOBBY = auto()      # sign-ups
    CHOOSING = auto()   # K chooses an identity
    PREDICT = auto()    # Artichoke: Dr. A writes his predictions (same wait in every round)
    PLAYING = auto()
    VOTING = auto()     # Artichoke: vote to unmask Dr. A
    FINAL = auto()      # Stargate: round over, Agent Skip may still arrest K


# ---------------------------------------------------------------- rules helpers
def min_players(mode: str, teams: int = 2) -> int:
    """Minimum number of players for a mode (Stargate depends on the teams)."""
    if mode == ARTICHOKE:
        return 2
    return {2: 4, 3: 8, 4: 10}.get(teams, 4)


def predict_needed(allowed: int) -> int:
    """Predicted names the researchers must try for Dr. A to win: half of the allowed ones,
    rounded up (fixed at the start, whatever number of names Dr. A actually writes)."""
    return (allowed + 1) // 2


def auto_moves(n_players: int) -> int:
    """Moves per person, computed from the number of players."""
    if n_players <= 2:
        return 25
    if n_players == 3:
        return 15
    if n_players <= 6:
        return 10
    if n_players <= 8:
        return 7
    if n_players <= 15:
        return 5
    return 3


def stargate_layout(n_players: int, teams: int) -> tuple[bool, int] | None:
    """How to split `n_players` for a Stargate round: (has_skip, team_size), or None.

    Patient K and Agent Skip are always there; the remaining researchers must split
    into equal teams of at least 2 (1 is enough with two teams).
    """
    min_size = 1 if teams == 2 else 2
    researchers = n_players - 2
    if researchers >= teams * min_size and researchers % teams == 0:
        return True, researchers // teams
    return None


def valid_totals(teams: int, start: int, count: int = 4) -> list[int]:
    """The next `count` numbers of players (from `start`) that give even teams."""
    out, n = [], max(start, 1)
    while len(out) < count and n < start + 60:
        if stargate_layout(n, teams):
            out.append(n)
        n += 1
    return out


# ---------------------------------------------------------------- text helpers
def norm(s: str) -> str:
    """Lowercase and strip accents, for tolerant comparisons."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold().strip()


def compact(s: str) -> str:
    """Like norm(), but also without spaces and punctuation."""
    return re.sub(r"[\W_]+", "", norm(s))


def wiki_langs(lang: str) -> tuple[str, str]:
    """Wikipedia language editions to search, in order."""
    return ("it", "en") if lang == "it" else ("en", "it")


def fmt_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    m, s = divmod(seconds, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


# ---------------------------------------------------------------- model
@dataclass
class Identity:
    title: str                                  # canonical Wikipedia title
    accepted: set[str]                          # compact forms accepted as a correct guess
    spoiler: set[str]                           # normalized forms to delete from the chat


def make_identity(typed: str, title: str) -> Identity:
    base = re.sub(r"\s*\(.*?\)", "", title).strip()
    spoiler = {k for k in (norm(typed), norm(base)) if len(k) >= 3}
    accepted = {k for k in (compact(typed), compact(base), compact(title)) if k}
    return Identity(title, accepted, spoiler)


@dataclass
class Question:
    id: int
    asker: int
    text: str
    message_id: int | None = None               # message in the group
    dm_message_id: int | None = None            # Stargate: the copy sent to K in private


@dataclass
class Game:
    chat_id: int
    creator: int
    lang: str
    mode: str | None = None
    variant: str = RANDOM                       # RANDOM, MUNCHAUSEN or PSYCHOSIS
    teams_count: int = 0                        # Stargate
    moves: int = 0                              # moves per person; 0 = automatic (set at start)
    phase: Phase = Phase.MODE
    players: dict[int, str] = field(default_factory=dict)     # user_id -> name
    lobby_end: float = 0.0
    started_at: float = 0.0

    roles: dict[int, str] = field(default_factory=dict)
    team: dict[int, str] = field(default_factory=dict)        # Stargate: user_id -> team name
    team_names: list[str] = field(default_factory=list)       # Stargate: teams in play
    patient: int | None = None                                # K
    dr_a: int | None = None
    skip: int | None = None

    identity: Identity | None = None                          # current identity
    used_identities: list[Identity] = field(default_factory=list)
    identity_no: int = 0                                      # 1 = first identity of the round
    awaiting_identity: bool = False

    moves_used: dict[int, int] = field(default_factory=dict)  # for the current identity
    total_moves: dict[int, int] = field(default_factory=dict) # of the identities already played
    pending: Question | None = None
    log: list[dict] = field(default_factory=list)
    counter: int = 0
    edit_tasks: set = field(default_factory=set)              # background chat-message rewrites

    skip_tries: int = 0                                       # arrests Skip holds right now
    skip_play_used: int = 0                                   # arrests used while playing (max 1)
    secret_tries: int = 0                                     # private guesses made by Skip / Dr. A
    secret_last: float = 0.0                                  # time of the last one
    flipped: bool = False                                     # Skip / Dr. A guessed: past answers reversed
    vote_enabled: bool = False                                # Artichoke: vote on Dr. A if nobody guesses
    dra_possible: bool = False                                # Artichoke: Dr. A may be in the round
    predict_allowed: int = 0                                  # names Dr. A may write
    predictions: list[Identity] = field(default_factory=list) # names written by Dr. A
    predict_hits: set[int] = field(default_factory=set)       # indexes tried by the researchers
    burnt: list[Identity] = field(default_factory=list)       # identity dropped with Dr. A
    final: tuple | None = None                                # result waiting for Skip's last chance
    skip_used: int = 0
    guessed: dict[int, int] = field(default_factory=dict)     # identities guessed per player
    solve_moves: dict[int, int] = field(default_factory=dict) # moves used at the best guess

    votes: dict[int, Any] = field(default_factory=dict)       # voter -> uid | "none" | "skip"
    permission_warned: bool = False

    paused: bool = False
    pause_started: float = 0.0
    pause_planned: float = 0.0                                # when the current /hold ends
    hold_used: set[int] = field(default_factory=set)
    hold_spent: float = 0.0
    frozen: list[tuple] = field(default_factory=list)         # timers frozen by /hold

    def name(self, uid: int) -> str:
        return self.players.get(uid, "?")

    def researchers(self) -> list[int]:
        return [u for u in self.players if self.roles.get(u) == RESEARCHER]

    def askers(self) -> list[int]:
        """Everyone who can ask questions (and has a pool of moves)."""
        extra = (PATIENT,) if self.mode == STARGATE else ()
        return [u for u in self.players if self.roles.get(u) in (RESEARCHER, DR_A, SKIP, *extra)]

    def team_members(self, team: str) -> list[int]:
        return [u for u in self.players if self.team.get(u) == team]

    def moves_left(self, uid: int) -> int:
        return self.moves - self.moves_used.get(uid, 0)

    def all_spoilers(self) -> set[str]:
        return set(self.identity.spoiler) if self.identity else set()


# ---------------------------------------------------------------- registry
games: dict[int, Game] = {}        # chat_id -> game
user_game: dict[int, int] = {}     # user_id -> chat_id (one active round per user)


# ---------------------------------------------------------------- timers
@dataclass
class Timer:
    callback: Callable
    end: float
    data: Any


timers: dict[tuple[int, str, str], Timer] = {}    # (chat_id, kind, key) -> pending timer


def job_name(kind: str, chat_id: int, key: str = "") -> str:
    return f"{kind}:{chat_id}:{key}"


def cancel_job(ctx, kind: str, chat_id: int, key: str = "") -> None:
    timers.pop((chat_id, kind, key), None)
    for job in ctx.job_queue.get_jobs_by_name(job_name(kind, chat_id, key)):
        job.schedule_removal()


def schedule(ctx, callback, seconds: float, kind: str, chat_id: int,
             key: str = "", data=None) -> None:
    """(Re)schedule a one-shot job, replacing any previous one with the same name.

    The deadline is remembered in `timers` so that /hold can freeze and resume it.
    """
    cancel_job(ctx, kind, chat_id, key)
    seconds = max(0.0, seconds)
    ident = (chat_id, kind, key)
    timers[ident] = Timer(callback, time.time() + seconds, data)

    async def run(c, _callback=callback, _ident=ident):
        timers.pop(_ident, None)
        await _callback(c)

    ctx.job_queue.run_once(run, seconds, chat_id=chat_id,
                           name=job_name(kind, chat_id, key), data=data)


def close_game(ctx, g: Game, reason: str = "closed") -> None:
    """Remove a game from the registry and cancel all of its timers."""
    LOG.info("round closed: chat=%s mode=%s reason=%s", g.chat_id, g.mode, reason)
    for (cid, kind, key) in list(timers):
        if cid == g.chat_id:
            cancel_job(ctx, kind, cid, key)
    for kind in ("config", "lobby", "choice", "predict", "inactivity", "answer", "vote", "hold",
                 "final"):
        cancel_job(ctx, kind, g.chat_id)
    for uid in g.players:
        user_game.pop(uid, None)
    games.pop(g.chat_id, None)


# ---------------------------------------------------------------- messaging
async def say(ctx, g: Game, key: str, **kw):
    """Send a localized message to the game's group."""
    return await ctx.bot.send_message(g.chat_id, T(g.lang, key, **kw))


async def dm(ctx, uid: int, g: Game, key: str, **kw) -> bool:
    """Send a localized private message. Returns False if the user can't be reached."""
    try:
        await ctx.bot.send_message(uid, T(g.lang, key, **kw))
        return True
    except TelegramError:
        return False


async def is_admin(ctx, chat_id: int, user_id: int) -> bool:
    try:
        member = await ctx.bot.get_chat_member(chat_id, user_id)
    except TelegramError:
        return False
    return member.status in ("administrator", "creator")
