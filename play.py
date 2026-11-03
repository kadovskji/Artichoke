"""Playing phase: questions, attempts, answers, Stargate points, Dr. A vote, /hold,
/summary and round endings."""
import math
import re
import time
from collections import Counter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import wiki
from game import (ANSWER_SECONDS, ARTICHOKE, CHOICE_SECONDS, DR_A, DR_A_MIN_PLAYERS,
                  HOLD_MAX_MINUTES, HOLD_TOTAL_SECONDS, INACTIVITY_SECONDS, POINTS_TO_WIN,
                  RESEARCHER, SKIP, SKIP_MAX_TRIES, STARGATE, VOTE_SECONDS, Game, Phase,
                  Question, cancel_job, close_game, dm, fmt_duration, games, is_admin, norm,
                  say, schedule, timers, user_game, wiki_langs)
from i18n import T

ACTIVE = (Phase.CHOOSING, Phase.PLAYING)


def _lang(chat_id: int) -> str:
    g = games.get(chat_id)
    return g.lang if g else db.get_lang(chat_id)


def touch_inactivity(ctx, g: Game) -> None:
    """Restart the 10-minute inactivity timer."""
    schedule(ctx, inactivity_expired, INACTIVITY_SECONDS, "inactivity", g.chat_id)


def score_text(g: Game) -> str:
    return ", ".join(f"{t} {g.points.get(t, 0)}" for t in g.team_names)


def identities_text(g: Game) -> str:
    return " / ".join(i.title for i in g.used_identities) or "-"


# ---------------------------------------------------------------- /ask
def _kb_answer(g: Game, q: Question) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T(g.lang, "btn_yes"), callback_data=f"a:{q.id}:y"),
        InlineKeyboardButton(T(g.lang, "btn_no"), callback_data=f"a:{q.id}:n"),
        InlineKeyboardButton(T(g.lang, "btn_unknown"), callback_data=f"a:{q.id}:u"),
    ]])


async def _gate(update: Update, g: Game | None) -> bool:
    """Common checks for /ask and /try in a group: a round in its playing phase."""
    if not g:
        return False
    if g.paused:
        await update.message.reply_text(T(g.lang, "game_paused"))
        return False
    if g.phase != Phase.PLAYING:
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return False
    return True


async def ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        return
    g = games.get(chat.id)
    if not await _gate(update, g):
        return
    if g.roles.get(user.id) not in (RESEARCHER, DR_A, SKIP):
        await update.message.reply_text(T(g.lang, "ask_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:200]
    if not text:
        await update.message.reply_text(T(g.lang, "ask_usage"))
        return
    if g.pending:
        await update.message.reply_text(T(g.lang, "ask_pending", patient=g.name(g.patient)))
        return
    if g.moves_left(user.id) <= 0:
        await update.message.reply_text(T(g.lang, "no_moves"))
        return

    g.moves_used[user.id] = g.moves_used.get(user.id, 0) + 1   # refunded on "don't know"
    g.counter += 1
    q = Question(g.counter, user.id, text)
    g.pending = q
    msg = await ctx.bot.send_message(
        chat.id,
        T(g.lang, "question_msg", who=g.name(user.id), used=g.moves_used[user.id],
          limit=g.moves, text=text, patient=g.name(g.patient)),
        reply_markup=_kb_answer(g, q))
    q.message_id = msg.message_id
    schedule(ctx, answer_expired, ANSWER_SECONDS, "answer", chat.id, data=q.id)
    touch_inactivity(ctx, g)


async def cb_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    _, qid, ans = cq.data.split(":")
    g = games.get(cq.message.chat_id)
    lang = _lang(cq.message.chat_id)
    pend = g.pending if g else None
    if not g or g.phase != Phase.PLAYING or not pend or pend.id != int(qid):
        await cq.answer(T(lang, "answer_stale"), show_alert=True)
        return
    if cq.from_user.id != g.patient:
        await cq.answer(T(lang, "answer_not_patient", patient=g.name(g.patient)),
                        show_alert=True)
        return
    if g.paused:
        await cq.answer(T(lang, "game_paused"), show_alert=True)
        return

    cancel_job(ctx, "answer", g.chat_id)
    g.pending = None
    if ans == "u":
        g.moves_used[pend.asker] -= 1           # "don't know" does not cost a move
    g.log.append({"no": g.identity_no, "who": g.name(pend.asker), "kind": "ask",
                  "text": pend.text, "res": ans})
    await cq.answer()
    await cq.edit_message_text(T(
        g.lang, "answered_msg", who=g.name(pend.asker), text=pend.text,
        answer=T(g.lang, f"res_{ans}")))
    touch_inactivity(ctx, g)
    await check_exhausted(ctx, g)


async def answer_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if not g or g.phase != Phase.PLAYING or not g.pending or g.pending.id != ctx.job.data:
        return
    patient, ids = g.name(g.patient), identities_text(g)
    await clear_pending(ctx, g)
    close_game(ctx, g, "patient did not answer")
    await ctx.bot.send_message(g.chat_id, T(g.lang, "answer_timeout", patient=patient, ids=ids))


# ---------------------------------------------------------------- /try
async def try_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        return
    g = games.get(chat.id)
    if not await _gate(update, g):
        return
    role = g.roles.get(user.id)
    if role not in (RESEARCHER, DR_A, SKIP):
        await update.message.reply_text(T(g.lang, "try_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:100]
    if not text:
        await update.message.reply_text(T(g.lang, "try_usage"))
        return

    if role == SKIP:
        if g.skip_tries <= 0:
            await dm(ctx, user.id, g, "skip_no_tries")      # private: don't expose the role
            return
        g.skip_tries -= 1
        g.skip_used += 1
    else:
        if g.moves_left(user.id) <= 0:
            await update.message.reply_text(T(g.lang, "no_moves"))
            return
        g.moves_used[user.id] = g.moves_used.get(user.id, 0) + 1

    no = g.identity_no
    if role == DR_A:
        correct = False                         # Dr. A can never win by guessing
    else:
        hit = await wiki.match_identity({"main": g.identity}, text, wiki_langs(g.lang))
        correct = hit is not None
    if games.get(chat.id) is not g or g.phase != Phase.PLAYING or g.identity_no != no:
        return                                  # the round moved on while we were checking
    touch_inactivity(ctx, g)

    if correct:
        if role == SKIP:
            await finish_skip_win(ctx, g, user.id)
        elif g.mode == ARTICHOKE:
            await finish_solved(ctx, g, user.id)
        else:
            await point_scored(ctx, g, user.id)
        return

    g.log.append({"no": no, "who": g.name(user.id), "kind": "try", "text": text,
                  "res": "wrong"})
    if role == SKIP:
        await update.message.reply_text(T(g.lang, "try_wrong_skip", text=text))
    else:
        await update.message.reply_text(T(
            g.lang, "try_wrong", who=g.name(user.id), text=text, left=g.moves_left(user.id)))
    if g.skip is not None and role == RESEARCHER:
        if g.skip_tries < SKIP_MAX_TRIES:
            g.skip_tries += 1
            await dm(ctx, g.skip, g, "skip_gain", n=g.skip_tries)
        else:
            await dm(ctx, g.skip, g, "skip_gain_max", n=g.skip_tries)
    await check_exhausted(ctx, g)


# ---------------------------------------------------------------- round-end checks
async def check_exhausted(ctx, g: Game) -> None:
    """End the round when nobody can make progress any more."""
    if g.phase != Phase.PLAYING or g.pending or g.paused:
        return
    if any(g.moves_left(u) > 0 for u in g.researchers()):
        return
    if g.skip is not None and g.skip_tries > 0:
        return
    await end_without_guess(ctx, g)


async def end_without_guess(ctx, g: Game) -> None:
    if g.mode == ARTICHOKE:
        if len(g.players) >= DR_A_MIN_PLAYERS:
            await start_vote(ctx, g)
        else:
            await finish_no_winner(ctx, g)
        return
    # Stargate: a strict leader wins, otherwise nobody
    ranked = sorted(g.team_names, key=lambda t: g.points.get(t, 0), reverse=True)
    best = g.points.get(ranked[0], 0)
    if best > 0 and sum(1 for t in ranked if g.points.get(t, 0) == best) == 1:
        await finish_team_win(ctx, g, ranked[0], lead=True)
    else:
        await finish_no_winner(ctx, g)


async def inactivity_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.PLAYING:
        await end_without_guess(ctx, g)


async def choice_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """K did not pick an identity in time."""
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.CHOOSING:
        close_game(ctx, g, "identity not chosen")
        await ctx.bot.send_message(g.chat_id, T(g.lang, "choice_timeout"))


# ---------------------------------------------------------------- Dr. A vote (Artichoke)
def _label(g: Game, v) -> str:
    return T(g.lang, "vote_option_none") if v == "none" else g.name(v)


def _vote_text(g: Game) -> str:
    head = T(g.lang, "vote_start", secs=VOTE_SECONDS)
    counts = Counter(v for v in g.votes.values() if v != "skip")
    if counts:
        top = max(counts.values())
        leaders = ", ".join(_label(g, v) for v, c in counts.items() if c == top)
        status = T(g.lang, "vote_status", n=len(g.votes), total=len(g.players),
                   leaders=leaders, top=top)
    else:
        status = T(g.lang, "vote_status_none", total=len(g.players))
    return f"{head}\n\n{status}"


def _kb_vote(g: Game) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(g.name(u)[:20], callback_data=f"v:{u}")
               for u in g.players]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton(T(g.lang, "vote_option_none"), callback_data="v:none"),
                 InlineKeyboardButton(T(g.lang, "btn_vote_skip"), callback_data="v:skip")])
    return InlineKeyboardMarkup(rows)


async def start_vote(ctx, g: Game) -> None:
    await clear_pending(ctx, g)
    cancel_job(ctx, "inactivity", g.chat_id)
    g.phase = Phase.VOTING
    g.votes = {}
    await ctx.bot.send_message(g.chat_id, _vote_text(g), reply_markup=_kb_vote(g))
    schedule(ctx, vote_expired, VOTE_SECONDS, "vote", g.chat_id)


async def cb_vote(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    g = games.get(cq.message.chat_id)
    lang = _lang(cq.message.chat_id)
    if not g or g.phase != Phase.VOTING:
        await cq.answer(T(lang, "vote_closed"), show_alert=True)
        return
    voter = cq.from_user.id
    raw = cq.data.split(":", 1)[1]
    if voter not in g.players:
        await cq.answer(T(lang, "vote_not_player"), show_alert=True)
        return
    if raw in ("none", "skip"):
        target = raw
    else:
        target = int(raw)
        if target not in g.players:
            await cq.answer()
            return
        if target == voter:
            await cq.answer(T(lang, "vote_self"), show_alert=True)
            return
    if voter in g.votes:
        await cq.answer(T(lang, "vote_already"), show_alert=True)
        return
    g.votes[voter] = target                     # secret and irrevocable
    await cq.answer(T(lang, "vote_skipped" if target == "skip" else "vote_recorded"))
    if len(g.votes) == len(g.players):
        await finish_vote(ctx, g)
        return
    try:
        await cq.edit_message_text(_vote_text(g), reply_markup=_kb_vote(g))
    except TelegramError:
        pass


async def vote_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.VOTING:
        await finish_vote(ctx, g)


async def finish_vote(ctx, g: Game) -> None:
    """Plurality rule: the right option must have strictly more votes than any other."""
    cancel_job(ctx, "vote", g.chat_id)
    counts = Counter(v for v in g.votes.values() if v != "skip")
    tally = (", ".join(f"{_label(g, v)}: {c}" for v, c in counts.most_common())
             or T(g.lang, "none_label"))
    correct = g.dr_a if g.dr_a is not None else "none"
    ok = False
    if counts:
        top = max(counts.values())
        leaders = [v for v, c in counts.items() if c == top]
        ok = leaders == [correct]
    title = g.identity.title
    if ok:
        winners = {u for u, v in g.votes.items() if v == correct}
        names = ", ".join(g.name(u) for u in g.players if u in winners)
        if g.dr_a is not None:
            text = T(g.lang, "vote_ok_dra", a=g.name(g.dr_a), winners=names,
                     title=title, tally=tally)
        else:
            text = T(g.lang, "vote_ok_none", winners=names, title=title, tally=tally)
        await _finish(ctx, g, "vote_ok", winners, text, caught=g.dr_a is not None)
    else:
        if g.dr_a is not None:
            text = T(g.lang, "vote_fail_dra", a=g.name(g.dr_a), title=title, tally=tally)
            winners = {g.dr_a}
        else:
            text = T(g.lang, "vote_fail_none", title=title, tally=tally)
            winners = set()
        await _finish(ctx, g, "vote_fail", winners, text)


# ---------------------------------------------------------------- endings
def reveal(g: Game) -> str:
    """Secret roles, shown when the round is over."""
    out = ""
    if g.dr_a is not None:
        out += T(g.lang, "reveal_dr_a", name=g.name(g.dr_a))
    if g.skip is not None:
        out += T(g.lang, "reveal_skip", name=g.name(g.skip))
    if g.mode == STARGATE:
        for t in g.team_names:
            out += T(g.lang, "reveal_team", team=t,
                     members=", ".join(g.name(u) for u in g.team_members(t)) or "-")
    return out


async def clear_pending(ctx, g: Game) -> None:
    """Remove the buttons from a question still waiting for an answer."""
    q = g.pending
    g.pending = None
    cancel_job(ctx, "answer", g.chat_id)
    if q and q.message_id:
        try:
            await ctx.bot.edit_message_text(
                T(g.lang, "question_closed", who=g.name(q.asker), text=q.text),
                chat_id=g.chat_id, message_id=q.message_id)
        except TelegramError:
            pass


async def _finish(ctx, g: Game, outcome: str, winners: set[int], text: str,
                  caught: bool = False, winner_team: str | None = None) -> None:
    await clear_pending(ctx, g)
    db.record_round(g, outcome, winners, caught, winner_team)
    close_game(ctx, g, outcome)
    await ctx.bot.send_message(g.chat_id, text)


def _credit(g: Game, guesser: int) -> None:
    """Book a correct guess for statistics."""
    g.guessed[guesser] = g.guessed.get(guesser, 0) + 1
    used = g.moves_used.get(guesser, 0)
    if guesser not in g.solve_moves or used < g.solve_moves[guesser]:
        g.solve_moves[guesser] = used


async def finish_solved(ctx, g: Game, guesser: int) -> None:
    """Artichoke: K and the first researcher who guesses win together."""
    _credit(g, guesser)
    text = T(g.lang, "solved_artichoke", guesser=g.name(guesser), title=g.identity.title,
             k=g.name(g.patient))
    await _finish(ctx, g, "solved", {g.patient, guesser}, text + reveal(g))


async def finish_skip_win(ctx, g: Game, skip_uid: int) -> None:
    g.guessed[skip_uid] = g.guessed.get(skip_uid, 0) + 1
    text = T(g.lang, "skip_win", skip=g.name(skip_uid), title=g.identity.title,
             ids=identities_text(g))
    await _finish(ctx, g, "skip_win", {skip_uid}, text + reveal(g))


async def point_scored(ctx, g: Game, guesser: int) -> None:
    """Stargate: a team guessed the current identity."""
    team = g.team[guesser]
    g.points[team] = g.points.get(team, 0) + 1
    g.solved.append((g.identity.title, team, guesser))
    _credit(g, guesser)
    if g.points[team] >= POINTS_TO_WIN:
        await finish_team_win(ctx, g, team)
        return
    await say(ctx, g, "point_scored", guesser=g.name(guesser), title=g.identity.title,
              team=team, score=score_text(g))
    await request_identity(ctx, g)


async def request_identity(ctx, g: Game) -> None:
    """Stargate: K must pick a new identity; moves are reset."""
    await clear_pending(ctx, g)
    cancel_job(ctx, "inactivity", g.chat_id)
    for u, n in g.moves_used.items():
        g.total_moves[u] = g.total_moves.get(u, 0) + n
    g.moves_used = {u: 0 for u in g.askers()}
    g.identity = None
    g.phase = Phase.CHOOSING
    g.awaiting_identity = True
    await say(ctx, g, "next_identity_group", k=g.name(g.patient))
    await dm(ctx, g.patient, g, "dm_next_identity")
    schedule(ctx, choice_expired, CHOICE_SECONDS, "choice", g.chat_id)


async def finish_team_win(ctx, g: Game, team: str, lead: bool = False) -> None:
    members = g.team_members(team)
    winners = {g.patient, *members}
    names = ", ".join(g.name(u) for u in g.players if u in winners)
    text = T(g.lang, "team_win_lead" if lead else "team_win", team=team,
             pts=g.points.get(team, 0), winners=names, ids=identities_text(g))
    await _finish(ctx, g, "team_win", winners, text + reveal(g), winner_team=team)


async def finish_no_winner(ctx, g: Game) -> None:
    if g.mode == ARTICHOKE:
        text = T(g.lang, "no_winner_artichoke", title=g.identity.title)
    else:
        text = T(g.lang, "no_winner_stargate", score=score_text(g), ids=identities_text(g))
    await _finish(ctx, g, "no_winner", set(), text + reveal(g))


# ---------------------------------------------------------------- /hold
def _freeze(ctx, g: Game) -> None:
    """Stop every running timer of the round, remembering the time left."""
    now = time.time()
    g.frozen = []
    for ident, t in list(timers.items()):
        chat_id, kind, key = ident
        if chat_id == g.chat_id and kind != "hold":
            g.frozen.append((kind, key, max(0.0, t.end - now), t.callback, t.data))
            cancel_job(ctx, kind, chat_id, key)


async def hold(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        return
    g = games.get(chat.id)
    lang = _lang(chat.id)
    if not g or g.phase not in ACTIVE:
        await update.message.reply_text(T(lang, "round_not_playing" if g else "round_none"))
        return
    if user.id not in g.players:
        await update.message.reply_text(T(lang, "only_players"))
        return
    mode = db.get_settings(chat.id)["breaks"]
    if mode == "off":
        await update.message.reply_text(T(lang, "hold_off"))
        return
    if mode == "admins" and not await is_admin(ctx, chat.id, user.id):
        await update.message.reply_text(T(lang, "hold_admins"))
        return
    if g.paused:
        await update.message.reply_text(T(lang, "hold_already"))
        return
    if user.id in g.hold_used:
        await update.message.reply_text(T(lang, "hold_used"))
        return
    arg = (ctx.args[0] if ctx.args else "").replace(",", ".")
    try:
        minutes = float(arg)
    except ValueError:
        minutes = float("nan")
    if not math.isfinite(minutes) or minutes <= 0:
        await update.message.reply_text(T(lang, "hold_usage"))
        return
    if minutes > HOLD_MAX_MINUTES:
        await update.message.reply_text(T(lang, "hold_max"))
        return
    left = HOLD_TOTAL_SECONDS - g.hold_spent
    if left <= 0:
        await update.message.reply_text(T(lang, "hold_none_left"))
        return
    seconds = min(minutes * 60, left)

    now = time.time()
    g.paused = True
    g.pause_started = now
    g.pause_planned = now + seconds
    g.hold_spent += seconds
    g.hold_used.add(user.id)
    _freeze(ctx, g)
    schedule(ctx, hold_expired, seconds, "hold", g.chat_id)
    await update.message.reply_text(
        T(lang, "hold_started", name=user.first_name, dur=fmt_duration(seconds)))


async def resume(ctx, g: Game, early: bool = False) -> None:
    """End a /hold pause and restart the frozen timers."""
    if not g.paused:
        return
    cancel_job(ctx, "hold", g.chat_id)
    if early:                                   # give back the unused pause time
        g.hold_spent = max(0.0, g.hold_spent - max(0.0, g.pause_planned - time.time()))
    g.paused = False
    frozen, g.frozen = g.frozen, []
    for kind, key, left, callback, data in frozen:
        schedule(ctx, callback, left, kind, g.chat_id, key, data)
    await say(ctx, g, "hold_ended")


async def hold_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.paused:
        await resume(ctx, g)


# ---------------------------------------------------------------- /summary
def _entry_line(g: Game, i: int, e: dict) -> str:
    icon = "🎯" if e["kind"] == "try" else "❓"
    text = f"«{e['text']}»" if e["kind"] == "try" else e["text"]
    res = T(g.lang, "res_wrong") if e["res"] == "wrong" else T(g.lang, f"res_{e['res']}")
    return f"{i}. {icon} {e['who']}: {text} → {res}"


def summary_text(g: Game) -> str:
    stargate = g.mode == STARGATE
    lines = [T(g.lang, "summary_head_stargate" if stargate else "summary_head_artichoke")]
    if not g.log and not g.pending:
        lines.append(T(g.lang, "summary_empty"))
    for no in range(1, max(g.identity_no, 1) + 1):
        entries = [e for e in g.log if e["no"] == no]
        if stargate:
            lines += ["", T(g.lang, "summary_identity", n=no)]
        lines += [_entry_line(g, i, e) for i, e in enumerate(entries, 1)]
    if g.pending:
        lines.append(T(g.lang, "summary_pending", patient=g.name(g.patient),
                       who=g.name(g.pending.asker), text=g.pending.text))
    shown = [u for u in g.askers() if u != g.skip]          # Skip stays secret
    lines.append("")
    lines.append(T(g.lang, "summary_moves", moves=" · ".join(
        f"{g.name(u)} {g.moves_left(u)}" for u in shown)))
    if stargate:
        lines.append(T(g.lang, "summary_points", score=score_text(g)))
    return "\n".join(lines)[:4000]


async def summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    g = games.get(chat.id)
    if not g:
        await update.message.reply_text(T(db.get_lang(chat.id), "round_none"))
        return
    if g.phase not in (Phase.PLAYING, Phase.CHOOSING, Phase.VOTING) or g.identity_no == 0:
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    await update.message.reply_text(summary_text(g))


# ---------------------------------------------------------------- anti-spoiler
async def spoiler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete group messages that reveal the current identity."""
    msg = update.effective_message
    g = games.get(update.effective_chat.id)
    if not g or g.phase not in (Phase.PLAYING, Phase.VOTING) or not msg or not msg.text:
        return
    words = g.all_spoilers()
    if not words:
        return
    text = norm(msg.text)
    if not any(re.search(rf"\b{re.escape(k)}\b", text) for k in words):
        return
    try:
        await msg.delete()
    except TelegramError:
        if not g.permission_warned:
            g.permission_warned = True
            await say(ctx, g, "no_delete_perm")
        return
    await say(ctx, g, "spoiler_removed", name=msg.from_user.first_name)
