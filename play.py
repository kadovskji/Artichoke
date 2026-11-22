"""Playing phase: questions, attempts, answers, Agent Skip arrests, Dr. A vote, /hold,
/summary and round endings."""
import asyncio
import math
import re
import time
from collections import Counter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import wiki
from game import (ANSWER_SECONDS, ARTICHOKE, DR_A, FINAL_SECONDS,
                  HOLD_MAX_MINUTES, HOLD_TOTAL_SECONDS, INACTIVITY_SECONDS, PATIENT,
                  RESEARCHER, SECRET_COOLDOWN, SECRET_MAX_TRIES, SKIP, SKIP_MAX_TRIES, STARGATE, VOTE_SECONDS, Game, Phase,
                  Question, cancel_job, close_game, compact, dm, fmt_duration, games,
                  is_admin, norm, predict_needed, say, schedule, timers, user_game,
                  wiki_langs)
from i18n import T

ACTIVE = (Phase.CHOOSING, Phase.PREDICT, Phase.PLAYING)


def _lang(chat_id: int) -> str:
    g = games.get(chat_id)
    return g.lang if g else db.get_lang(chat_id)


def touch_inactivity(ctx, g: Game) -> None:
    """Restart the 10-minute inactivity timer."""
    schedule(ctx, inactivity_expired, INACTIVITY_SECONDS, "inactivity", g.chat_id)


def identities_text(g: Game) -> str:
    return " / ".join(i.title for i in g.used_identities) or "-"


# ---------------------------------------------------------------- /ask
def _kb_answer(g: Game, q: Question, only_unknown: bool = False) -> InlineKeyboardMarkup:
    unknown = InlineKeyboardButton(T(g.lang, "btn_unknown"), callback_data=f"a:{q.id}:u")
    if only_unknown:
        return InlineKeyboardMarkup([[unknown]])
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T(g.lang, "btn_yes"), callback_data=f"a:{q.id}:y"),
        InlineKeyboardButton(T(g.lang, "btn_no"), callback_data=f"a:{q.id}:n"),
        unknown,
    ]])


def _can_ask(g: Game, role: str | None) -> bool:
    if g.mode == STARGATE:
        return role in (RESEARCHER, PATIENT, SKIP)
    return role in (RESEARCHER, DR_A)


def _can_try(g: Game, role: str | None) -> bool:
    """Who can try the identity in the group (Agent Skip does it in private)."""
    if g.mode == STARGATE:
        return role in (RESEARCHER, PATIENT)
    return role in (RESEARCHER, DR_A)


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
    if not _can_ask(g, g.roles.get(user.id)):
        await update.message.reply_text(T(g.lang, "ask_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:200]
    if not text:
        await update.message.reply_text(T(g.lang, "ask_usage"))
        return
    if g.pending:
        await update.message.reply_text(
            T(g.lang, "ask_pending_s") if g.mode == STARGATE
            else T(g.lang, "ask_pending", patient=g.name(g.patient)))
        return
    if g.moves_left(user.id) <= 0:
        await update.message.reply_text(T(g.lang, "no_moves"))
        return

    # the move is spent now (Artichoke refunds it on "don't know", Stargate never does)
    g.moves_used[user.id] = g.moves_used.get(user.id, 0) + 1
    g.counter += 1
    q = Question(g.counter, user.id, text)
    g.pending = q
    if g.mode == ARTICHOKE:
        msg = await ctx.bot.send_message(
            chat.id,
            T(g.lang, "question_msg", who=g.name(user.id), used=g.moves_used[user.id],
              limit=g.moves, text=text, patient=g.name(g.patient)),
            reply_markup=_kb_answer(g, q))
        q.message_id = msg.message_id
    else:
        # Stargate: K is secret, so K answers in private and the bot publishes the answer
        msg = await ctx.bot.send_message(
            chat.id,
            T(g.lang, "question_msg_s", who=g.name(user.id), used=g.moves_used[user.id],
              limit=g.moves, text=text))
        q.message_id = msg.message_id
        own = user.id == g.patient
        copy = await ctx.bot.send_message(
            g.patient,
            T(g.lang, "dm_question_own" if own else "dm_question",
              who=g.name(user.id), text=text),
            reply_markup=_kb_answer(g, q, only_unknown=own))
        q.dm_message_id = copy.message_id
    schedule(ctx, answer_expired, ANSWER_SECONDS, "answer", chat.id, data=q.id)
    touch_inactivity(ctx, g)


async def cb_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    _, qid, ans = cq.data.split(":")
    uid = cq.from_user.id
    # Artichoke: the buttons are in the group. Stargate: they are in K's private chat.
    g = games.get(cq.message.chat_id) or games.get(user_game.get(uid))
    lang = g.lang if g else _lang(cq.message.chat_id)
    pend = g.pending if g else None
    if not g or g.phase != Phase.PLAYING or not pend or pend.id != int(qid):
        await cq.answer(T(lang, "answer_stale"), show_alert=True)
        return
    if uid != g.patient:
        await cq.answer(T(lang, "answer_not_patient", patient=g.name(g.patient)),
                        show_alert=True)
        return
    if g.paused:
        await cq.answer(T(lang, "game_paused"), show_alert=True)
        return
    if g.mode == STARGATE and pend.asker == g.patient and ans != "u":
        await cq.answer(T(lang, "answer_own_only"), show_alert=True)
        return

    cancel_job(ctx, "answer", g.chat_id)
    g.pending = None
    if ans == "u" and g.mode == ARTICHOKE:
        g.moves_used[pend.asker] -= 1           # only in Artichoke "don't know" is free
    g.log.append({"no": g.identity_no, "who": g.name(pend.asker), "kind": "ask",
                  "text": pend.text, "res": ans, "msg": pend.message_id})
    await cq.answer()
    result = T(g.lang, f"res_{ans}")
    published = T(g.lang, "answered_msg", who=g.name(pend.asker), text=pend.text, answer=result)
    if g.mode == ARTICHOKE:
        await cq.edit_message_text(published)
    else:
        await cq.edit_message_text(T(g.lang, "dm_question_done", answer=result))
        try:
            await ctx.bot.edit_message_text(published, chat_id=g.chat_id,
                                            message_id=pend.message_id)
        except TelegramError:
            pass
    touch_inactivity(ctx, g)
    await check_exhausted(ctx, g)


async def answer_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if not g or g.phase != Phase.PLAYING or not g.pending or g.pending.id != ctx.job.data:
        return
    ids = identities_text(g)
    await clear_pending(ctx, g)
    close_game(ctx, g, "patient did not answer")
    if g.mode == STARGATE:
        await ctx.bot.send_message(g.chat_id, T(g.lang, "answer_timeout_s", ids=ids))
    else:
        await ctx.bot.send_message(g.chat_id, T(g.lang, "answer_timeout",
                                                patient=g.name(g.patient), ids=ids))


# ---------------------------------------------------------------- /try
async def try_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        await _secret_try(update, ctx)
        return
    g = games.get(chat.id)
    if not await _gate(update, g):
        return
    role = g.roles.get(user.id)
    if _secret_guesser(g, role):                # Skip / Dr. A try in private
        await dm(ctx, user.id, g, "secret_try_private")
        return
    if not _can_try(g, role):
        await update.message.reply_text(T(g.lang, "try_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:100]
    if not text:
        await update.message.reply_text(T(g.lang, "try_usage"))
        return
    if g.moves_left(user.id) <= 0:
        await update.message.reply_text(T(g.lang, "no_moves"))
        return
    g.moves_used[user.id] = g.moves_used.get(user.id, 0) + 1

    no = g.identity_no
    if role in (DR_A, PATIENT):
        correct = False                         # Dr. A and Patient K can never win by guessing
    else:
        hit = await wiki.match_identity({"main": g.identity}, text, wiki_langs(g.lang))
        correct = hit is not None
    if games.get(chat.id) is not g or g.phase != Phase.PLAYING or g.identity_no != no:
        return                                  # the round moved on while we were checking
    touch_inactivity(ctx, g)

    if correct:
        if g.mode == ARTICHOKE:
            await finish_solved(ctx, g, user.id)
        else:
            await finish_team_win(ctx, g, user.id)
        return

    g.log.append({"no": no, "who": g.name(user.id), "kind": "try", "text": text,
                  "res": "wrong"})
    if role == RESEARCHER and g.predictions:    # did a researcher try a name Dr. A predicted?
        await _count_prediction(g, text)
        if games.get(chat.id) is not g or g.phase != Phase.PLAYING or g.identity_no != no:
            return
    await update.message.reply_text(T(
        g.lang, "try_wrong", who=g.name(user.id), text=text, left=g.moves_left(user.id)))
    # Every wrong attempt (K's too, so K can't be told apart) gives Agent Skip an arrest
    if g.skip is not None and role in (RESEARCHER, PATIENT):
        if g.skip_tries < SKIP_MAX_TRIES:
            g.skip_tries += 1
            await dm(ctx, g.skip, g, "skip_gain", n=g.skip_tries)
        else:
            await dm(ctx, g.skip, g, "skip_gain_max", n=g.skip_tries)
    await check_exhausted(ctx, g)


def _secret_guesser(g: Game, role: str | None) -> bool:
    """Agent Skip doesn't know the identity: Skip tries it in private, and a correct guess
    reverses all the answers given so far."""
    return g.mode == STARGATE and role == SKIP


def shown_result(e: dict) -> str:
    """The result of a log entry as everybody sees it (yes/no swapped once flipped)."""
    res = e["res"]
    if e.get("flip") and res in ("y", "n"):
        return "n" if res == "y" else "y"
    return res


async def _count_prediction(g: Game, text: str) -> None:
    """A researcher made a wrong attempt: if it is one of Dr. A's predicted names (matched
    like an identity, redirects included), book it. Each name counts once."""
    pending = [i for i in range(len(g.predictions)) if i not in g.predict_hits]
    guess = compact(text)
    for i in pending:
        if guess in g.predictions[i].accepted:
            g.predict_hits.add(i)
            return
    if not pending:
        return
    found = await wiki.verify_wikipedia(text, wiki_langs(g.lang))
    if found is None:
        return
    resolved = compact(found[0])
    for i in pending:
        if resolved in g.predictions[i].accepted:
            g.predict_hits.add(i)
            return


async def _secret_try(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Agent Skip tries the identity in private (free: it doesn't spend a move, so the
    moves left in /summary don't give Skip away)."""
    user = update.effective_user
    g = games.get(user_game.get(user.id))
    if (not g or not _secret_guesser(g, g.roles.get(user.id))
            or g.phase not in (Phase.PLAYING, Phase.VOTING, Phase.FINAL)):
        return
    text = " ".join(ctx.args).strip()[:100]
    if not text:
        await update.message.reply_text(T(g.lang, "try_usage"))
        return
    if g.flipped:
        await update.message.reply_text(T(g.lang, "secret_identity_already"))
        return
    if g.secret_tries >= SECRET_MAX_TRIES:
        await update.message.reply_text(T(g.lang, "secret_try_none"))
        return
    wait = g.secret_last + SECRET_COOLDOWN - time.time()
    if wait > 0:
        await update.message.reply_text(T(g.lang, "secret_try_wait", secs=math.ceil(wait)))
        return
    g.secret_tries += 1                         # counted (and the clock started) before the check
    g.secret_last = time.time()
    hit = await wiki.match_identity({"main": g.identity}, text, wiki_langs(g.lang))
    if games.get(g.chat_id) is not g or g.flipped:
        return
    if hit is None:
        await update.message.reply_text(T(g.lang, "secret_identity_wrong",
                                          left=SECRET_MAX_TRIES - g.secret_tries))
        return
    g.flipped = True
    await update.message.reply_text(T(g.lang, "secret_identity_ok"))
    flip_answers(ctx, g)


EDIT_DELAY = 0.5        # seconds between two edits, to stay within Telegram's rate limits


def flip_answers(ctx, g: Game) -> None:
    """Reverse every yes/no answer given so far: in the log (so /summary shows them swapped)
    and in the messages already posted in the group, rewritten in the background."""
    todo = []
    for e in g.log:
        if e["kind"] == "ask" and e["res"] in ("y", "n"):
            e["flip"] = True
            if e.get("msg"):
                todo.append(e)
    task = asyncio.create_task(_rewrite_messages(ctx, g, todo))
    g.edit_tasks.add(task)
    task.add_done_callback(g.edit_tasks.discard)


async def _rewrite_messages(ctx, g: Game, entries: list[dict]) -> None:
    for e in entries:
        text = T(g.lang, "answered_msg", who=e["who"], text=e["text"],
                 answer=T(g.lang, f"res_{shown_result(e)}"))
        for _ in range(3):
            try:
                await ctx.bot.edit_message_text(text, chat_id=g.chat_id, message_id=e["msg"])
                break
            except TelegramError as err:
                wait = getattr(err, "retry_after", None)
                if wait is None:
                    break                       # message gone or unchanged: skip it
                await asyncio.sleep(float(getattr(wait, "total_seconds", lambda: wait)()) + 0.5)
        await asyncio.sleep(EDIT_DELAY)


# ---------------------------------------------------------------- /arrest (Agent Skip)
def _arrest_problem(g: Game, uid: int) -> str | None:
    """Why Agent Skip can't arrest right now (an i18n key), or None."""
    if uid != g.skip:
        return "arrest_forbidden"
    if g.skip_tries <= 0:
        return "arrest_none"
    if g.phase == Phase.PLAYING and g.skip_play_used >= 1:
        return "arrest_wait_end"                # the second arrest is for the end
    return None


def _kb_arrest(g: Game) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(g.name(u)[:20], callback_data=f"k:{u}")
               for u in g.players if u != g.skip]
    return InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)])


async def arrest(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        return
    g = games.get(chat.id)
    if not g or g.mode != STARGATE:
        return
    if g.paused:
        await update.message.reply_text(T(g.lang, "game_paused"))
        return
    if g.phase not in (Phase.PLAYING, Phase.FINAL):
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    problem = _arrest_problem(g, user.id)
    if problem:
        await update.message.reply_text(T(g.lang, problem))
        return
    await update.message.reply_text(T(g.lang, "arrest_menu", n=g.skip_tries),
                                    reply_markup=_kb_arrest(g))


async def cb_arrest(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    g = games.get(cq.message.chat_id)
    lang = _lang(cq.message.chat_id)
    if not g or g.mode != STARGATE or g.phase not in (Phase.PLAYING, Phase.FINAL):
        await cq.answer(T(lang, "arrest_stale"), show_alert=True)
        return
    if g.paused:
        await cq.answer(T(lang, "game_paused"), show_alert=True)
        return
    problem = _arrest_problem(g, cq.from_user.id)
    if problem:
        await cq.answer(T(lang, problem), show_alert=True)
        return
    target = int(cq.data.split(":")[1])
    if target not in g.players or target == g.skip:
        await cq.answer()
        return
    await cq.answer(T(lang, "arrest_done"))
    g.skip_tries -= 1
    g.skip_used += 1
    if g.phase == Phase.PLAYING:
        g.skip_play_used += 1
    if target == g.patient:
        try:
            await cq.edit_message_text(T(g.lang, "arrest_done"))
        except TelegramError:
            pass
        await finish_skip_win(ctx, g)
        return
    try:
        await cq.edit_message_text(
            T(g.lang, "arrest_wrong", name=g.name(target), n=g.skip_tries))
    except TelegramError:
        pass
    if g.phase == Phase.FINAL and g.skip_tries <= 0:
        await complete_final(ctx, g)


# ---------------------------------------------------------------- round-end checks
async def check_exhausted(ctx, g: Game) -> None:
    """End the round when nobody can make progress any more."""
    if g.phase != Phase.PLAYING or g.pending or g.paused:
        return
    if any(g.moves_left(u) > 0 for u in g.researchers()):
        return
    await end_without_guess(ctx, g)


async def end_without_guess(ctx, g: Game) -> None:
    if g.mode == ARTICHOKE:
        if g.dr_a is not None and len(g.predict_hits) >= predict_needed(g.predict_allowed):
            await finish_dra_win(ctx, g)        # the researchers tried enough of his names
        elif g.vote_enabled:
            await start_vote(ctx, g)
        else:
            await finish_no_winner(ctx, g)
        return
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
    counts = Counter(g.votes.values())
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
    rows.append([InlineKeyboardButton(T(g.lang, "vote_option_none"), callback_data="v:none")])
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
    if raw == "none":
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
    await cq.answer(T(lang, "vote_recorded"))
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
    counts = Counter(g.votes.values())
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
        await _finish(ctx, g, "vote_ok", winners, text + predictions_text(g),
                      caught=g.dr_a is not None)
    else:
        if g.dr_a is not None:
            text = T(g.lang, "vote_fail_dra", a=g.name(g.dr_a), title=title, tally=tally)
        else:
            text = T(g.lang, "vote_fail_none", title=title, tally=tally)
        await _finish(ctx, g, "vote_fail", set(), text + predictions_text(g))


# ---------------------------------------------------------------- endings
def predictions_text(g: Game) -> str:
    """Dr. A's predicted names, with the ones the researchers tried."""
    if not g.predictions:
        return ""
    names = ", ".join(f"{p.title} {'✅' if i in g.predict_hits else '❌'}"
                      for i, p in enumerate(g.predictions))
    return T(g.lang, "reveal_predictions", names=names, hits=len(g.predict_hits),
             total=len(g.predictions), needed=predict_needed(g.predict_allowed))


def reveal(g: Game) -> str:
    """Secret roles, shown when the round is over."""
    out = ""
    if g.dr_a is not None:
        out += T(g.lang, "reveal_dr_a", name=g.name(g.dr_a)) + predictions_text(g)
    if g.mode == STARGATE:
        out += T(g.lang, "reveal_patient", name=g.name(g.patient))
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


async def finish_dra_win(ctx, g: Game) -> None:
    """Artichoke: nobody guessed, and the researchers tried enough of Dr. A's names."""
    text = T(g.lang, "dra_win", a=g.name(g.dr_a), title=g.identity.title,
             hits=len(g.predict_hits), total=len(g.predictions))
    await _finish(ctx, g, "dra_win", {g.dr_a}, text + reveal(g))


async def finish_skip_win(ctx, g: Game) -> None:
    """Stargate: Agent Skip arrested the right player and wins alone."""
    g.final = None
    text = T(g.lang, "skip_win", skip=g.name(g.skip), k=g.name(g.patient),
             ids=identities_text(g))
    await _finish(ctx, g, "skip_win", {g.skip}, text + reveal(g))


async def finish_team_win(ctx, g: Game, guesser: int) -> None:
    """Stargate: a team named the identity; it wins together with K."""
    _credit(g, guesser)
    team = g.team[guesser]
    winners = {g.patient, *g.team_members(team)}
    names = ", ".join(g.name(u) for u in g.players if u in winners)
    text = T(g.lang, "team_win", team=team, title=g.identity.title, winners=names)
    await end_stargate(ctx, g, "team_win", winners, text, team)


async def finish_no_winner(ctx, g: Game) -> None:
    if g.mode == ARTICHOKE:
        text = T(g.lang, "no_winner_artichoke", title=g.identity.title)
        await _finish(ctx, g, "no_winner", set(), text + reveal(g))
    else:
        text = T(g.lang, "no_winner_stargate", ids=identities_text(g))
        await end_stargate(ctx, g, "no_winner", set(), text, None)


async def end_stargate(ctx, g: Game, outcome: str, winners: set[int], text: str,
                       winner_team: str | None) -> None:
    """The round is over: if Agent Skip still has arrests there are 90 seconds left."""
    await clear_pending(ctx, g)
    if g.skip is None or g.skip_tries <= 0:
        await _finish(ctx, g, outcome, winners, text + reveal(g), winner_team=winner_team)
        return
    g.final = (outcome, winners, text, winner_team)
    g.phase = Phase.FINAL
    cancel_job(ctx, "inactivity", g.chat_id)
    await ctx.bot.send_message(g.chat_id, T(g.lang, "final_window", secs=FINAL_SECONDS),
                               reply_markup=_kb_arrest(g))
    schedule(ctx, final_expired, FINAL_SECONDS, "final", g.chat_id)


async def complete_final(ctx, g: Game) -> None:
    """Skip's last chance is over: announce the result that was waiting."""
    outcome, winners, text, winner_team = g.final
    g.final = None
    await _finish(ctx, g, outcome, winners, text + reveal(g), winner_team=winner_team)


async def final_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.FINAL and g.final:
        await complete_final(ctx, g)


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
    res = T(g.lang, "res_wrong") if e["res"] == "wrong" else T(g.lang, f"res_{shown_result(e)}")
    return f"{i}. {icon} {e['who']}: {text} → {res}"


def summary_text(g: Game) -> str:
    lines = [T(g.lang, "summary_head_stargate" if g.mode == STARGATE
               else "summary_head_artichoke")]
    if not g.log and not g.pending:
        lines.append(T(g.lang, "summary_empty"))
    lines += [_entry_line(g, i, e) for i, e in enumerate(g.log, 1)]
    if g.pending:
        if g.mode == ARTICHOKE:
            lines.append(T(g.lang, "summary_pending", patient=g.name(g.patient),
                           who=g.name(g.pending.asker), text=g.pending.text))
        else:
            lines.append(T(g.lang, "summary_pending_s", who=g.name(g.pending.asker),
                           text=g.pending.text))
    lines.append("")
    lines.append(T(g.lang, "summary_moves", moves=" · ".join(
        f"{g.name(u)} {g.moves_left(u)}" for u in g.askers())))
    return "\n".join(lines)[:4000]


async def summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    g = games.get(chat.id)
    if not g:
        await update.message.reply_text(T(db.get_lang(chat.id), "round_none"))
        return
    if g.phase not in (Phase.PLAYING, Phase.CHOOSING, Phase.VOTING, Phase.FINAL) \
            or g.identity_no == 0:
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    await update.message.reply_text(summary_text(g))


# ---------------------------------------------------------------- anti-spoiler
async def spoiler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete group messages that reveal the current identity."""
    msg = update.effective_message
    g = games.get(update.effective_chat.id)
    if (not g or g.phase not in (Phase.PREDICT, Phase.PLAYING, Phase.VOTING, Phase.FINAL)
            or not msg or not msg.text):
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
