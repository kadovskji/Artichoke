"""Shared game model, registry, timers and small helpers."""
import re
import unicodedata
from dataclasses import dataclass, field
from enum import Enum, auto

from telegram.error import TelegramError

from i18n import T

# ---------------------------------------------------------------- constants
ENIGMA = "enigma"
PSYOPS = "psyops"
MIN_PLAYERS = {ENIGMA: 2, PSYOPS: 4}
DR_A_MIN_PLAYERS = 5            # Enigma: Dr. A only plays with this many players
MOVE_OPTIONS = (5, 10, 15, 20)  # moves (questions + attempts) per participant

# Timings, in seconds
CONFIG_SECONDS = 120        # creator must pick mode / moves
LOBBY_SECONDS = 300         # sign-up window
CHOICE_SECONDS = 120        # patients must pick their identity
ANSWER_SECONDS = 120        # patient must answer a question
INACTIVITY_SECONDS = 600    # Enigma: round ends after this much inactivity
PSYOPS_SECONDS = 600        # PSY-OPS: total round time
VOTE_SECONDS = 60           # Dr. A vote
WAIT_MAX_MINUTES = 10       # max extension per /wait

# Roles
PATIENT, RESEARCHER, DR_A, SPY = "patient", "researcher", "dr_a", "spy"

# PSY-OPS teams
TEAMS = ("artichoke", "bluebird")
TEAM_LETTER = {"artichoke": "K", "bluebird": "H"}   # patient names
TEAM_ICON = {"artichoke": "🟢", "bluebird": "🔵"}


class Phase(Enum):
    MODE = auto()       # creator picks the mode
    MOVES = auto()      # creator picks moves per participant
    LOBBY = auto()      # sign-ups
    CHOOSING = auto()   # patients choose their identity
    PLAYING = auto()
    VOTING = auto()     # Enigma: vote to unmask Dr. A


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
    key: str                    # "main" (Enigma) or team name (PSY-OPS)
    asker: int
    text: str
    message_id: int | None = None


@dataclass
class Game:
    chat_id: int
    creator: int
    lang: str
    mode: str | None = None
    moves: int = 0
    phase: Phase = Phase.MODE
    players: dict[int, str] = field(default_factory=dict)     # user_id -> name
    lobby_end: float = 0.0
    started_at: float = 0.0

    roles: dict[int, str] = field(default_factory=dict)
    team: dict[int, str] = field(default_factory=dict)        # PSY-OPS: user_id -> team
    patients: dict[str, int] = field(default_factory=dict)    # key -> user_id
    identities: dict[str, Identity] = field(default_factory=dict)
    awaiting: set[int] = field(default_factory=set)           # patients yet to choose
    dr_a: int | None = None
    spy: int | None = None

    moves_used: dict[int, int] = field(default_factory=dict)
    pending: dict[str, Question] = field(default_factory=dict)
    log: list[dict] = field(default_factory=list)
    counter: int = 0

    spy_tries: int = 0          # attempts currently available to the spy
    spy_used: int = 0
    spy_found: set[str] = field(default_factory=set)

    votes: dict[int, int] = field(default_factory=dict)       # voter -> suspect
    permission_warned: bool = False

    def name(self, uid: int) -> str:
        return self.players.get(uid, "?")

    def patient_key(self, uid: int) -> str | None:
        for key, patient in self.patients.items():
            if patient == uid:
                return key
        return None

    def key_of(self, uid: int) -> str | None:
        """Key of the question queue / identity a researcher works on."""
        return "main" if self.mode == ENIGMA else self.team.get(uid)

    def researchers(self) -> list[int]:
        return [u for u in self.players if self.roles.get(u) == RESEARCHER]

    def movers(self) -> list[int]:
        """Everyone with a pool of moves (researchers, plus Dr. A)."""
        return [u for u in self.players if self.roles.get(u) in (RESEARCHER, DR_A)]

    def moves_left(self, uid: int) -> int:
        return self.moves - self.moves_used.get(uid, 0)

    def all_spoilers(self) -> set[str]:
        out: set[str] = set()
        for ident in self.identities.values():
            out |= ident.spoiler
        return out


# ---------------------------------------------------------------- registry
games: dict[int, Game] = {}        # chat_id -> game
user_game: dict[int, int] = {}     # user_id -> chat_id (one active round per user)


# ---------------------------------------------------------------- jobs
def job_name(kind: str, chat_id: int, key: str = "") -> str:
    return f"{kind}:{chat_id}:{key}"


def cancel_job(ctx, kind: str, chat_id: int, key: str = "") -> None:
    for job in ctx.job_queue.get_jobs_by_name(job_name(kind, chat_id, key)):
        job.schedule_removal()


def schedule(ctx, callback, seconds: float, kind: str, chat_id: int,
             key: str = "", data=None) -> None:
    """(Re)schedule a one-shot job, replacing any previous one with the same name."""
    cancel_job(ctx, kind, chat_id, key)
    ctx.job_queue.run_once(callback, max(0, seconds), chat_id=chat_id,
                           name=job_name(kind, chat_id, key), data=data)


def close_game(ctx, g: Game) -> None:
    """Remove a game from the registry and cancel all of its timers."""
    for kind in ("config", "lobby", "choice", "inactivity", "round", "vote"):
        cancel_job(ctx, kind, g.chat_id)
    for key in ("main",) + TEAMS:
        cancel_job(ctx, "answer", g.chat_id, key)
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
