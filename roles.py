"""Round setup: role assignment, identity selection and start of play."""
import random
import time

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import play
import wiki
from game import (CHOICE_SECONDS, DR_A, DR_A_MIN_PLAYERS, ENIGMA, PATIENT, PSYOPS,
                  PSYOPS_SECONDS, RESEARCHER, SPY, TEAM_LETTER, TEAMS, Game, Phase,
                  cancel_job, close_game, dm, games, make_identity, say, schedule,
                  user_game, wiki_langs)
from i18n import T


# ---------------------------------------------------------------- role assignment
def _assign_enigma(g: Game, ids: list[int]) -> None:
    k = ids.pop()
    g.roles[k] = PATIENT
    g.patients["main"] = k
    if len(g.players) >= DR_A_MIN_PLAYERS:
        a = ids.pop()
        g.roles[a] = DR_A
        g.dr_a = a
    for u in ids:
        g.roles[u] = RESEARCHER


def _assign_psyops(g: Game, ids: list[int]) -> None:
    if len(ids) % 2 == 1:                       # odd number of players: one KGB spy
        s = ids.pop()
        g.roles[s] = SPY
        g.spy = s
    for team in TEAMS:                          # one random patient per team
        p = ids.pop()
        g.roles[p] = PATIENT
        g.team[p] = team
        g.patients[team] = p
    half = len(ids) // 2                        # split the rest evenly
    for i, u in enumerate(ids):
        g.roles[u] = RESEARCHER
        g.team[u] = TEAMS[0] if i < half else TEAMS[1]


def _names(g: Game, uids) -> str:
    names = [g.name(u) for u in uids]
    return ", ".join(names) if names else "-"


def _role_message(g: Game, uid: int) -> tuple[str, dict]:
    """(string key, format arguments) of the private message that explains a role."""
    role = g.roles[uid]
    if g.mode == ENIGMA:
        if role == PATIENT:
            return "dm_patient_enigma", {}
        if role == DR_A:
            return "dm_dr_a", {"moves": g.moves}
        return "dm_researcher_enigma", {"k": g.name(g.patients["main"]), "moves": g.moves}
    # PSY-OPS
    if role == SPY:
        return "dm_spy", {}
    team = g.team[uid]
    mates = [u for u in g.researchers() if g.team[u] == team and u != uid]
    if role == PATIENT:
        return "dm_patient_psyops", {
            "letter": TEAM_LETTER[team], "team": team.capitalize(),
            "mates": _names(g, [u for u in g.researchers() if g.team[u] == team])}
    patient = g.patients[team]
    return "dm_researcher_psyops", {
        "team": team.capitalize(), "patient": g.name(patient),
        "letter": TEAM_LETTER[team], "mates": _names(g, mates), "moves": g.moves}


# ---------------------------------------------------------------- round start
async def start_round(ctx, g: Game) -> None:
    """Assign roles, tell everyone their role in private, announce the round."""
    ids = list(g.players)
    random.shuffle(ids)
    if g.mode == ENIGMA:
        _assign_enigma(g, ids)
    else:
        _assign_psyops(g, ids)
    for u in g.movers():
        g.moves_used[u] = 0
    g.phase = Phase.CHOOSING
    g.awaiting = set(g.patients.values())

    failed = []
    for uid in g.players:
        key, kw = _role_message(g, uid)
        if not await dm(ctx, uid, g, key, **kw):
            failed.append(uid)
    if any(u in g.awaiting for u in failed):    # a patient can't be reached: abort
        bad = next(u for u in failed if u in g.awaiting)
        close_game(ctx, g)
        await ctx.bot.send_message(g.chat_id, T(g.lang, "dm_failed", name=g.name(bad)))
        return

    if g.mode == ENIGMA:
        extra = T(g.lang, "announce_enigma_dra") if g.dr_a is not None else ""
        await say(ctx, g, "announce_enigma", n=len(g.players),
                  k=g.name(g.patients["main"]), extra=extra)
    else:
        spy = T(g.lang, "announce_psyops_spy") if g.spy is not None else ""
        await say(ctx, g, "announce_psyops", n=len(g.players),
                  k=g.name(g.patients["artichoke"]), h=g.name(g.patients["bluebird"]),
                  spy=spy)
    if failed:
        await say(ctx, g, "dm_warn", names=", ".join(g.name(u) for u in failed))
    await _check_delete_permission(ctx, g)
    schedule(ctx, choice_expired, CHOICE_SECONDS, "choice", g.chat_id)


async def _check_delete_permission(ctx, g: Game) -> None:
    try:
        member = await ctx.bot.get_chat_member(g.chat_id, ctx.bot.id)
        ok = member.status == "administrator" and bool(getattr(member, "can_delete_messages", False))
    except TelegramError:
        ok = False
    if not ok:
        g.permission_warned = True
        await say(ctx, g, "no_delete_perm")


async def choice_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.CHOOSING:
        close_game(ctx, g)
        await ctx.bot.send_message(g.chat_id, T(g.lang, "choice_timeout"))


# ---------------------------------------------------------------- identity selection
async def on_identity(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Private text message from a patient: the identity they pick."""
    uid = update.effective_user.id
    g = games.get(user_game.get(uid))
    if not g or g.phase != Phase.CHOOSING or uid not in g.awaiting:
        return
    typed = update.message.text.strip()[:100]
    found = await wiki.verify_wikipedia(typed, wiki_langs(g.lang))
    if g.phase != Phase.CHOOSING or uid not in g.awaiting:   # round changed meanwhile
        return
    if found is None:
        await update.message.reply_text(T(g.lang, "identity_not_found"))
        return
    title, qid = found
    verdict = await wiki.is_character(qid)      # True / False / None (could not be verified)
    if g.phase != Phase.CHOOSING or uid not in g.awaiting:
        return
    if verdict is False:
        await update.message.reply_text(T(g.lang, "identity_not_character", title=title))
        return

    ident = make_identity(typed, title)
    if any(other.accepted & ident.accepted for other in g.identities.values()):
        await update.message.reply_text(T(g.lang, "identity_taken"))
        return
    g.identities[g.patient_key(uid)] = ident
    g.awaiting.discard(uid)
    note = "\n" + T(g.lang, "identity_unverified") if verdict is None else ""
    if g.awaiting:
        await update.message.reply_text(T(g.lang, "identity_waiting", title=title) + note)
        return
    await update.message.reply_text(T(g.lang, "identity_saved", title=title) + note)
    await begin_play(ctx, g)


async def begin_play(ctx, g: Game) -> None:
    """All identities are set: the playing phase starts."""
    cancel_job(ctx, "choice", g.chat_id)
    g.phase = Phase.PLAYING
    g.started_at = time.time()
    if g.mode == ENIGMA:
        if g.dr_a is not None:
            await dm(ctx, g.dr_a, g, "dm_identity_dra", title=g.identities["main"].title)
        await say(ctx, g, "play_start_enigma", moves=g.moves)
        play.touch_inactivity(ctx, g)
    else:
        await say(ctx, g, "play_start_psyops", moves=g.moves)
        schedule(ctx, play.round_expired, PSYOPS_SECONDS, "round", g.chat_id)
