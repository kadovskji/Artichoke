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
from game import (ARTICHOKE, CHOICE_SECONDS, DR_A, DR_A_ABSENT_CHANCE, DR_A_MIN_PLAYERS,
                  MUNCHAUSEN, PATIENT, PSYCHOSIS, RESEARCHER, SKIP, STARGATE, TEAM_NAMES,
                  Game, Phase, auto_moves,
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
    if len(g.players) >= DR_A_MIN_PLAYERS:
        always = db.get_settings(g.chat_id)["dra"] == "always"
        if always or random.random() >= DR_A_ABSENT_CHANCE:
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
            return "dm_dr_a", {"moves": g.moves}
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
        extra = T(g.lang, "announce_artichoke_vote") if n >= DR_A_MIN_PLAYERS else ""
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
    if any(other.accepted & ident.accepted for other in g.used_identities):
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
    """An identity is set: the playing phase (re)starts."""
    cancel_job(ctx, "choice", g.chat_id)
    g.phase = Phase.PLAYING
    g.started_at = time.time()
    if g.dr_a is not None:
        await dm(ctx, g.dr_a, g, "dm_identity_dra", title=g.identity.title)
    await say(ctx, g, "play_start_artichoke" if g.mode == ARTICHOKE
              else "play_start_stargate", moves=g.moves)
    play.touch_inactivity(ctx, g)
