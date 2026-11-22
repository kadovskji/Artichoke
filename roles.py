"""Round setup: role assignment, identity selection and start of play."""
import logging
import random
import time

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import play
import wiki
from game import (ARTICHOKE, CHOICE_SECONDS, DR_A, DR_A_MIN_PLAYERS, DR_A_PRESENCE,
                  MUNCHAUSEN, PATIENT, PREDICT_MAX, PREDICT_SECONDS_PER_NAME, PSYCHOSIS,
                  RESEARCHER, SKIP, STARGATE, TEAM_NAMES,
                  Game, Phase, auto_moves, predict_needed,
                  cancel_job, close_game, dm, games, make_identity, say, schedule,
                  stargate_layout, user_game, valid_totals, wiki_langs)
from i18n import T

LOG = logging.getLogger("artichoke.game")


# ---------------------------------------------------------------- role assignment
def _assign_artichoke(g: Game, ids: list[int]) -> None:
    if g.variant == MUNCHAUSEN:                 # the creator is Patient K
        ids.remove(g.creator)
        g.patient = g.creator
    else:
        g.patient = ids.pop()
    g.roles[g.patient] = PATIENT
    if g.dra_possible and random.random() < DR_A_PRESENCE[db.get_settings(g.chat_id)["dra"]]:
        g.dr_a = ids.pop()
        g.roles[g.dr_a] = DR_A
    for u in ids:
        g.roles[u] = RESEARCHER


def _assign_stargate(g: Game, ids: list[int], has_skip: bool, size: int) -> None:
    if g.variant == PSYCHOSIS:                  # the creator is Agent Skip
        ids.remove(g.creator)
        g.skip = g.creator
        g.roles[g.skip] = SKIP
    g.patient = ids.pop()
    g.roles[g.patient] = PATIENT
    if has_skip and g.skip is None:
        g.skip = ids.pop()
        g.roles[g.skip] = SKIP
    g.team_names = random.sample(TEAM_NAMES, g.teams_count)
    for i, name in enumerate(g.team_names):
        for u in ids[i * size:(i + 1) * size]:
            g.roles[u] = RESEARCHER
            g.team[u] = name


def _role_message(g: Game, uid: int) -> tuple[str, dict]:
    """(string key, format arguments) of the private message that explains a role."""
    role, k = g.roles[uid], g.name(g.patient)
    if g.mode == ARTICHOKE:
        if role == PATIENT:
            return "dm_patient_a", {}
        if role == DR_A:
            return "dm_dr_a", {"moves": g.moves, "allowed": g.predict_allowed,
                           "needed": predict_needed(g.predict_allowed)}
        return "dm_researcher_a", {"k": k, "moves": g.moves}
    teams = ", ".join(g.team_names)
    if role == PATIENT:
        return "dm_patient_s", {"teams": teams, "skip": g.name(g.skip)}
    if role == SKIP:
        return "dm_skip", {"moves": g.moves}
    return "dm_researcher_s", {"team": g.team[uid], "teams": teams, "moves": g.moves}


# ---------------------------------------------------------------- round start
async def start_round(ctx, g: Game) -> None:
    """Assign roles, tell everyone their role in private, announce the round."""
    n = len(g.players)
    ids = list(g.players)
    random.shuffle(ids)
    if g.moves == 0:
        g.moves = auto_moves(n)
    if g.mode == ARTICHOKE:
        cfg = db.get_settings(g.chat_id)
        g.dra_possible = n >= DR_A_MIN_PLAYERS and cfg["dra"] != "never"
        g.predict_allowed = min(PREDICT_MAX, n - 2)     # one name per researcher, at most 7
        g.vote_enabled = g.dra_possible and cfg["dravote"] == "on"
        _assign_artichoke(g, ids)
    else:
        layout = stargate_layout(n, g.teams_count)
        if layout is None:                      # should have been caught in the lobby
            hint = ", ".join(map(str, valid_totals(g.teams_count, n + 1)))
            close_game(ctx, g, "uneven teams")
            await ctx.bot.send_message(g.chat_id, T(g.lang, "bad_layout", list=hint))
            return
        _assign_stargate(g, ids, *layout)
    g.moves_used = {u: 0 for u in g.askers()}
    g.phase = Phase.CHOOSING
    g.awaiting_identity = True
    LOG.info("round started: chat=%s mode=%s players=%d moves=%d dr_a=%s skip=%s",
             g.chat_id, g.mode, n, g.moves, g.dr_a is not None, g.skip is not None)

    failed = []
    for uid in g.players:
        key, kw = _role_message(g, uid)
        if not await dm(ctx, uid, g, key, **kw):
            failed.append(uid)
    if g.patient in failed:                     # K can't be reached: abort
        close_game(ctx, g, "patient unreachable")
        if g.mode == STARGATE:                  # K is secret: don't say who
            await ctx.bot.send_message(g.chat_id, T(g.lang, "dm_failed_s"))
        else:
            await ctx.bot.send_message(g.chat_id,
                                       T(g.lang, "dm_failed", name=g.name(g.patient)))
        return

    if g.mode == ARTICHOKE:
        extra = T(g.lang, "announce_artichoke_vote") if g.vote_enabled else ""
        await say(ctx, g, "announce_artichoke", n=n, k=g.name(g.patient),
                  moves=g.moves, extra=extra)
    else:
        await say(ctx, g, "announce_stargate", n=n, skip=g.name(g.skip),
                  teams=", ".join(g.team_names), moves=g.moves)
    if failed:
        await say(ctx, g, "dm_warn", names=", ".join(g.name(u) for u in failed))
    await _check_delete_permission(ctx, g)
    schedule(ctx, play.choice_expired, CHOICE_SECONDS, "choice", g.chat_id)


async def _check_delete_permission(ctx, g: Game) -> None:
    try:
        member = await ctx.bot.get_chat_member(g.chat_id, ctx.bot.id)
        ok = member.status == "administrator" and bool(getattr(member, "can_delete_messages", False))
    except TelegramError:
        ok = False
    if not ok:
        g.permission_warned = True
        await say(ctx, g, "no_delete_perm")


# ---------------------------------------------------------------- identity selection
async def on_identity(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Private text message from K: the identity they pick."""
    uid = update.effective_user.id
    g = games.get(user_game.get(uid))

    def waiting() -> bool:
        return bool(g and games.get(g.chat_id) is g and g.phase == Phase.CHOOSING
                    and g.awaiting_identity and uid == g.patient)

    if not waiting():
        return
    if g.paused:
        await update.message.reply_text(T(g.lang, "game_paused"))
        return
    typed = update.message.text.strip()[:100]
    found = await wiki.verify_wikipedia(typed, wiki_langs(g.lang))
    if not waiting():                           # round changed meanwhile
        return
    if found is None:
        await update.message.reply_text(T(g.lang, "identity_not_found"))
        return
    title, qid = found
    verdict = await wiki.is_character(qid)      # True / False / None (could not be verified)
    if not waiting():
        return
    if verdict is False:
        await update.message.reply_text(T(g.lang, "identity_not_character", title=title))
        return

    ident = make_identity(typed, title)
    if any(other.accepted & ident.accepted for other in g.used_identities + g.burnt):
        await update.message.reply_text(T(g.lang, "identity_taken"))
        return
    g.identity = ident
    g.used_identities.append(ident)
    g.identity_no += 1
    g.awaiting_identity = False
    note = "\n" + T(g.lang, "identity_unverified") if verdict is None else ""
    await update.message.reply_text(T(g.lang, "identity_saved", title=title) + note)
    await begin_play(ctx, g)


async def begin_play(ctx, g: Game) -> None:
    """An identity is set. Where Dr. A may be in the round, everybody waits the same time
    (so the wait doesn't give him away) while he writes his predictions."""
    cancel_job(ctx, "choice", g.chat_id)
    if g.dra_possible:
        await start_predict(ctx, g)
    else:
        await start_playing(ctx, g)


async def start_predict(ctx, g: Game) -> None:
    g.phase = Phase.PREDICT
    secs = PREDICT_SECONDS_PER_NAME * g.predict_allowed
    await say(ctx, g, "predict_wait")
    if g.dr_a is not None:
        await dm(ctx, g.dr_a, g, "dm_predict", title=g.identity.title, allowed=g.predict_allowed,
                 needed=predict_needed(g.predict_allowed), secs=secs)
    schedule(ctx, predict_expired, secs, "predict", g.chat_id)


async def start_playing(ctx, g: Game) -> None:
    g.phase = Phase.PLAYING
    g.started_at = time.time()
    await say(ctx, g, "play_start_artichoke" if g.mode == ARTICHOKE
              else "play_start_stargate", moves=g.moves)
    play.touch_inactivity(ctx, g)


# ---------------------------------------------------------------- joining a round in progress
def late_moves(g: Game) -> int:
    """Moves for someone joining a round in progress: the average of the moves left to the
    current players (rounded, at least 1)."""
    left = [g.moves_left(u) for u in g.askers()]
    avg = sum(left) / len(left) if left else g.moves
    return max(1, min(g.moves, int(avg + 0.5)))


async def late_join(ctx, g: Game, uid: int, name: str) -> bool:
    """Add a researcher to a round that has already started. In Stargate the newcomer
    joins the smallest team. Returns False if they can't be reached in private."""
    moves = late_moves(g)
    team = None
    if g.mode == STARGATE:
        size = {t: len(g.team_members(t)) for t in g.team_names}
        smallest = min(size.values())
        team = random.choice([t for t, n in size.items() if n == smallest])
        key, kw = "dm_researcher_s", {"team": team, "teams": ", ".join(g.team_names),
                                      "moves": moves}
    else:
        key, kw = "dm_researcher_a", {"k": g.name(g.patient), "moves": moves}
    if not await dm(ctx, uid, g, key, **kw):
        return False
    g.players[uid] = name
    user_game[uid] = g.chat_id
    g.roles[uid] = RESEARCHER
    if team:
        g.team[uid] = team
    g.moves_used[uid] = g.moves - moves
    LOG.info("late join: chat=%s user=%s moves=%d", g.chat_id, uid, moves)
    await say(ctx, g, "joined_late", name=name, moves=moves, n=len(g.players))
    return True


# ---------------------------------------------------------------- Dr. A's predictions
async def on_prediction(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Private text from Dr. A while the round waits: a name he predicts the researchers
    will try (wrongly). Returns True if the message was handled here."""
    uid = update.effective_user.id
    g = games.get(user_game.get(uid))

    def waiting() -> bool:
        return bool(g and games.get(g.chat_id) is g and g.phase == Phase.PREDICT
                    and uid == g.dr_a)

    if not waiting():
        return False
    if g.paused:
        await update.message.reply_text(T(g.lang, "game_paused"))
        return True
    if len(g.predictions) >= g.predict_allowed:
        await update.message.reply_text(T(g.lang, "predict_full"))
        return True
    typed = update.message.text.strip()[:100]
    found = await wiki.verify_wikipedia(typed, wiki_langs(g.lang))
    if not waiting():
        return True
    if found is None:
        await update.message.reply_text(T(g.lang, "identity_not_found"))
        return True
    title, qid = found
    verdict = await wiki.is_character(qid)
    if not waiting():
        return True
    if verdict is False:
        await update.message.reply_text(T(g.lang, "identity_not_character", title=title))
        return True
    ident = make_identity(typed, title)
    if ident.accepted & g.identity.accepted:
        await update.message.reply_text(T(g.lang, "predict_is_identity"))
        return True
    if any(ident.accepted & p.accepted for p in g.predictions):
        await update.message.reply_text(T(g.lang, "predict_dup"))
        return True
    if len(g.predictions) >= g.predict_allowed:         # filled while we were checking
        await update.message.reply_text(T(g.lang, "predict_full"))
        return True
    g.predictions.append(ident)
    await update.message.reply_text(T(
        g.lang, "predict_saved", title=title, n=len(g.predictions), allowed=g.predict_allowed,
        needed=predict_needed(g.predict_allowed)))
    return True


async def undo_prediction(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """/undo in private: Dr. A removes the last name he wrote."""
    uid = update.effective_user.id
    g = games.get(user_game.get(uid))
    if not g or g.phase != Phase.PREDICT or uid != g.dr_a or g.paused:
        return
    if not g.predictions:
        await update.message.reply_text(T(g.lang, "predict_none"))
        return
    gone = g.predictions.pop()
    await update.message.reply_text(T(g.lang, "predict_undone", title=gone.title,
                                      n=len(g.predictions), allowed=g.predict_allowed))


async def predict_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """The wait is over. If Dr. A wrote too few names to be able to win, he loses the role."""
    g = games.get(ctx.job.chat_id)
    if not g or g.phase != Phase.PREDICT:
        return
    if g.dr_a is not None and len(g.predictions) < predict_needed(g.predict_allowed):
        await drop_dra(ctx, g)
        return
    await start_playing(ctx, g)


async def drop_dra(ctx, g: Game) -> None:
    """Dr. A can't win any more: he becomes a researcher and K picks a new identity (the old
    one is burnt, since the ex Dr. A knows it). No vote in this round: everybody knows."""
    dra = g.dr_a
    g.roles[dra] = RESEARCHER
    g.dr_a = None
    g.predictions, g.predict_hits = [], set()
    g.dra_possible = g.vote_enabled = False
    g.used_identities.remove(g.identity)
    g.burnt.append(g.identity)
    g.identity = None
    g.identity_no -= 1
    g.phase = Phase.CHOOSING
    g.awaiting_identity = True
    LOG.info("Dr. A dropped: chat=%s", g.chat_id)
    await say(ctx, g, "dra_dropped")
    await dm(ctx, g.patient, g, "dm_choose_again")
    await dm(ctx, dra, g, "dm_dra_dropped")
    schedule(ctx, play.choice_expired, CHOICE_SECONDS, "choice", g.chat_id)
