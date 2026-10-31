"""Playing phase: questions, attempts, answers, Dr. A vote, summary and round endings."""
import re
from collections import Counter

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import wiki
from game import (ANSWER_SECONDS, DR_A, ENIGMA, INACTIVITY_SECONDS, PSYOPS, RESEARCHER,
                  SPY, TEAM_ICON, TEAM_LETTER, TEAMS, VOTE_SECONDS, Game, Phase, Question,
                  cancel_job, close_game, dm, games, norm, say, schedule, user_game,
                  wiki_langs)
from i18n import T


def _lang(chat_id: int) -> str:
    g = games.get(chat_id)
    return g.lang if g else db.get_lang(chat_id)


def team_tag(g: Game, key: str) -> str:
    """' 🟢 Artichoke' in PSY-OPS, '' in Enigma."""
    if g.mode != PSYOPS:
        return ""
    return f" {TEAM_ICON[key]} {key.capitalize()}"


def touch_inactivity(ctx, g: Game) -> None:
    """Enigma: restart the inactivity timer."""
    if g.mode == ENIGMA:
        schedule(ctx, inactivity_expired, INACTIVITY_SECONDS, "inactivity", g.chat_id)


# ---------------------------------------------------------------- /ask
def _kb_answer(g: Game, q: Question) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(T(g.lang, "btn_yes"), callback_data=f"a:{q.id}:y"),
        InlineKeyboardButton(T(g.lang, "btn_no"), callback_data=f"a:{q.id}:n"),
        InlineKeyboardButton(T(g.lang, "btn_unknown"), callback_data=f"a:{q.id}:u"),
    ]])


async def ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        return
    g = games.get(chat.id)
    if not g:
        return
    if g.phase != Phase.PLAYING:
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    if g.roles.get(user.id) not in (RESEARCHER, DR_A):
        await update.message.reply_text(T(g.lang, "ask_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:200]
    if not text:
        await update.message.reply_text(T(g.lang, "ask_usage"))
        return
    key = g.key_of(user.id)
    patient = g.patients[key]
    if key in g.pending:
        await update.message.reply_text(T(g.lang, "ask_pending", patient=g.name(patient)))
        return
    if g.moves_left(user.id) <= 0:
        await update.message.reply_text(T(g.lang, "no_moves"))
        return

    g.moves_used[user.id] += 1                  # the move is spent now (refunded on "don't know")
    g.counter += 1
    q = Question(g.counter, key, user.id, text)
    g.pending[key] = q
    msg = await ctx.bot.send_message(
        chat.id,
        T(g.lang, "question_msg", who=g.name(user.id), team=team_tag(g, key),
          used=g.moves_used[user.id], limit=g.moves, text=text, patient=g.name(patient)),
        reply_markup=_kb_answer(g, q))
    q.message_id = msg.message_id
    schedule(ctx, answer_expired, ANSWER_SECONDS, "answer", chat.id, key, data=(key, q.id))
    touch_inactivity(ctx, g)


async def cb_answer(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    cq = update.callback_query
    _, qid, ans = cq.data.split(":")
    g = games.get(cq.message.chat_id)
    lang = _lang(cq.message.chat_id)
    pend = next((x for x in g.pending.values() if x.id == int(qid)), None) if g else None
    if not g or g.phase != Phase.PLAYING or not pend:
        await cq.answer(T(lang, "answer_stale"), show_alert=True)
        return
    patient = g.patients[pend.key]
    if cq.from_user.id != patient:
        await cq.answer(T(lang, "answer_not_patient", patient=g.name(patient)),
                        show_alert=True)
        return

    cancel_job(ctx, "answer", g.chat_id, pend.key)
    del g.pending[pend.key]
    if ans == "u":
        g.moves_used[pend.asker] -= 1           # "don't know" does not cost a move
    g.log.append({"key": pend.key, "who": g.name(pend.asker), "kind": "ask",
                  "text": pend.text, "res": ans})
    await cq.answer()
    await cq.edit_message_text(T(
        g.lang, "answered_msg", who=g.name(pend.asker), team=team_tag(g, pend.key),
        text=pend.text, answer=T(g.lang, f"res_{ans}")))
    touch_inactivity(ctx, g)
    await check_exhausted(ctx, g)


async def answer_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    key, qid = ctx.job.data
    pend = g.pending.get(key) if g else None
    if not g or g.phase != Phase.PLAYING or not pend or pend.id != qid:
        return
    patient = g.name(g.patients[key])
    ids = identities_text(g)
    close_game(ctx, g)
    await ctx.bot.send_message(
        g.chat_id, T(g.lang, "answer_timeout", patient=patient, ids=ids))


# ---------------------------------------------------------------- /try
async def try_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type == "private":
        await _spy_try(update, ctx)
        return
    g = games.get(chat.id)
    if not g:
        return
    if g.phase != Phase.PLAYING:
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    role = g.roles.get(user.id)
    if role == SPY:
        await dm(ctx, user.id, g, "spy_use_private")
    if role not in (RESEARCHER, DR_A):
        await update.message.reply_text(T(g.lang, "try_forbidden"))
        return
    text = " ".join(ctx.args).strip()[:100]
    if not text:
        await update.message.reply_text(T(g.lang, "try_usage"))
        return
    if g.moves_left(user.id) <= 0:
        await update.message.reply_text(T(g.lang, "no_moves"))
        return

    g.moves_used[user.id] += 1
    key = g.key_of(user.id)
    if role == DR_A:
        correct = False                         # Dr. A can never win by guessing
    else:
        hit = await wiki.match_identity({key: g.identities[key]}, text, wiki_langs(g.lang))
        correct = hit is not None
    if games.get(chat.id) is not g or g.phase != Phase.PLAYING:   # round ended meanwhile
        return
    touch_inactivity(ctx, g)
    if correct:
        await finish_solved(ctx, g, user.id, key)
        return

    g.log.append({"key": key, "who": g.name(user.id), "kind": "try",
                  "text": text, "res": "wrong"})
    await update.message.reply_text(T(
        g.lang, "try_wrong", who=g.name(user.id), text=text, left=g.moves_left(user.id)))
    if g.spy is not None and role == RESEARCHER:    # PSY-OPS: the spy gains an attempt
        g.spy_tries += 1
        await dm(ctx, g.spy, g, "spy_gain", n=g.spy_tries)
    await check_exhausted(ctx, g)


async def _spy_try(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """The KGB spy makes attempts in private, so their role stays secret."""
    user = update.effective_user
    g = games.get(user_game.get(user.id))
    if not g or g.roles.get(user.id) != SPY or g.phase != Phase.PLAYING:
        return
    text = " ".join(ctx.args).strip()[:100]
    if not text:
        await update.message.reply_text(T(g.lang, "try_usage"))
        return
    if g.spy_tries <= 0:
        await update.message.reply_text(T(g.lang, "spy_no_tries"))
        return
    g.spy_tries -= 1
    g.spy_used += 1
    remaining = {k: v for k, v in g.identities.items() if k not in g.spy_found}
    hit = await wiki.match_identity(remaining, text, wiki_langs(g.lang))
    if games.get(g.chat_id) is not g or g.phase != Phase.PLAYING:
        return
    if hit is None:
        await update.message.reply_text(T(g.lang, "spy_wrong", left=g.spy_tries))
        return
    g.spy_found.add(hit)
    if len(g.spy_found) == len(TEAMS):
        await finish_spy_win(ctx, g)
        return
    await update.message.reply_text(
        T(g.lang, "spy_partial", found=len(g.spy_found), left=g.spy_tries))


# ---------------------------------------------------------------- round-end checks
async def check_exhausted(ctx, g: Game) -> None:
    """End the round when nobody can make progress any more."""
    if g.phase != Phase.PLAYING or g.pending:
        return
    if any(g.moves_left(u) > 0 for u in g.researchers()):
        return
    if g.spy is not None and g.spy_tries > 0:
        return
    await end_without_guess(ctx, g)


async def end_without_guess(ctx, g: Game) -> None:
    if g.mode == ENIGMA and g.dr_a is not None:
        await start_vote(ctx, g)
    else:
        await finish_no_winner(ctx, g)


async def inactivity_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.PLAYING and g.mode == ENIGMA:
        await end_without_guess(ctx, g)


async def round_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """PSY-OPS: the 10 minutes are over."""
    g = games.get(ctx.job.chat_id)
    if g and g.phase == Phase.PLAYING and g.mode == PSYOPS:
        await finish_no_winner(ctx, g)


# ---------------------------------------------------------------- Dr. A vote (Enigma)
def _vote_text(g: Game) -> str:
    head = T(g.lang, "vote_start", secs=VOTE_SECONDS)
    counts = Counter(g.votes.values())
    if counts:
        top = max(counts.values())
        leaders = ", ".join(g.name(u) for u, c in counts.items() if c == top)
        status = T(g.lang, "vote_status", n=len(g.votes), total=len(g.players),
                   leaders=leaders, top=top)
    else:
        status = T(g.lang, "vote_status_none", total=len(g.players))
    return f"{head}\n\n{status}"


def _kb_vote(g: Game) -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(g.name(u)[:20], callback_data=f"v:{u}")
               for u in g.players]
    return InlineKeyboardMarkup([buttons[i:i + 2] for i in range(0, len(buttons), 2)])


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
    target = int(cq.data.split(":")[1])
    if voter not in g.players:
        await cq.answer(T(lang, "vote_not_player"), show_alert=True)
        return
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
    cancel_job(ctx, "vote", g.chat_id)
    counts = Counter(g.votes.values())
    tally = (", ".join(f"{g.name(u)}: {c}" for u, c in counts.most_common())
             if counts else T(g.lang, "none_label"))
    caught = False
    if counts:
        top = max(counts.values())
        leaders = [u for u, c in counts.items() if c == top]
        caught = leaders == [g.dr_a]            # must be the strictly most voted
    title = g.identities["main"].title
    k = g.patients["main"]
    if caught:
        winners = {k} | set(g.researchers())
        text = T(g.lang, "vote_caught", a=g.name(g.dr_a), k=g.name(k),
                 title=title, tally=tally)
        outcome = "caught"
    else:
        winners = {g.dr_a}
        text = T(g.lang, "vote_escaped", a=g.name(g.dr_a), title=title, tally=tally)
        outcome = "escaped"
    await _finish(ctx, g, outcome, winners, text, caught=caught)


# ---------------------------------------------------------------- endings
def identities_text(g: Game) -> str:
    if g.mode == ENIGMA:
        return g.identities["main"].title
    return " / ".join(f"{TEAM_LETTER[k]}: {g.identities[k].title}"
                      for k in TEAMS if k in g.identities)


def _roster(g: Game, team: str) -> str:
    members = [u for u in g.researchers() if g.team[u] == team]
    patient = g.patients[team]
    return ", ".join([f"{g.name(patient)} ({TEAM_LETTER[team]})"] + [g.name(u) for u in members])


def reveal(g: Game) -> str:
    """Secret roles, shown when the round is over."""
    out = ""
    if g.dr_a is not None:
        out += T(g.lang, "reveal_dr_a", name=g.name(g.dr_a))
    if g.mode == PSYOPS:
        out += T(g.lang, "reveal_teams", a=_roster(g, "artichoke"), b=_roster(g, "bluebird"))
        if g.spy is not None:
            out += T(g.lang, "reveal_spy", name=g.name(g.spy))
    return out


async def clear_pending(ctx, g: Game) -> None:
    """Remove the buttons from questions still waiting for an answer."""
    for q in list(g.pending.values()):
        try:
            await ctx.bot.edit_message_text(
                T(g.lang, "question_closed", who=g.name(q.asker), text=q.text),
                chat_id=g.chat_id, message_id=q.message_id)
        except TelegramError:
            pass
    g.pending.clear()


async def _finish(ctx, g: Game, outcome: str, winners: set[int], text: str,
                  guessed: dict[int, int] | None = None, caught: bool = False,
                  winner_team: str | None = None) -> None:
    await clear_pending(ctx, g)
    db.record_round(g, outcome, winners, guessed or {}, caught, winner_team)
    close_game(ctx, g)
    await ctx.bot.send_message(g.chat_id, text)


async def finish_solved(ctx, g: Game, guesser: int, key: str) -> None:
    ident = g.identities[key]
    if g.mode == ENIGMA:
        k = g.patients["main"]
        winners = {k, guesser}
        text = T(g.lang, "solved_enigma", guesser=g.name(guesser),
                 title=ident.title, k=g.name(k))
        team = None
    else:
        winners = {g.patients[key]} | {u for u in g.researchers() if g.team[u] == key}
        other = next(t for t in TEAMS if t != key)
        text = T(g.lang, "solved_psyops", team=key.capitalize(), guesser=g.name(guesser),
                 title=ident.title,
                 winners=", ".join(g.name(u) for u in g.players if u in winners),
                 other=g.identities[other].title)
        team = key
    await _finish(ctx, g, "solved", winners, text + reveal(g),
                  guessed={guesser: 1}, winner_team=team)


async def finish_spy_win(ctx, g: Game) -> None:
    text = T(g.lang, "spy_win", spy=g.name(g.spy),
             a=g.identities["artichoke"].title, b=g.identities["bluebird"].title)
    await _finish(ctx, g, "spy_win", {g.spy}, text + reveal(g), guessed={g.spy: 2})


async def finish_no_winner(ctx, g: Game) -> None:
    if g.mode == ENIGMA:
        text = T(g.lang, "no_winner_enigma", title=g.identities["main"].title)
    else:
        text = T(g.lang, "no_winner_psyops", a=g.identities["artichoke"].title,
                 b=g.identities["bluebird"].title)
    await _finish(ctx, g, "no_winner", set(), text + reveal(g))


# ---------------------------------------------------------------- /summary
def _entry_line(g: Game, i: int, e: dict, with_team: bool) -> str:
    icon = "🎯" if e["kind"] == "try" else "❓"
    text = f"«{e['text']}»" if e["kind"] == "try" else e["text"]
    res = T(g.lang, "res_wrong") if e["res"] == "wrong" else T(g.lang, f"res_{e['res']}")
    return f"{i}. {icon} {e['who']}: {text} → {res}"


def summary_text(g: Game) -> str:
    if g.mode == ENIGMA:
        lines = [T(g.lang, "summary_head_enigma")]
        if not g.log:
            lines.append(T(g.lang, "summary_empty"))
        lines += [_entry_line(g, i, e, False) for i, e in enumerate(g.log, 1)]
        pending = g.pending.get("main")
        if pending:
            lines.append(T(g.lang, "summary_pending", patient=g.name(g.patients["main"]),
                           who=g.name(pending.asker), text=pending.text))
        lines.append(T(g.lang, "summary_moves", moves=" · ".join(
            f"{g.name(u)} {g.moves_left(u)}" for u in g.movers())))
    else:
        lines = [T(g.lang, "summary_head_psyops")]
        if not g.log:
            lines.append(T(g.lang, "summary_empty"))
        for team in TEAMS:
            entries = [e for e in g.log if e["key"] == team]
            pending = g.pending.get(team)
            if not entries and not pending:
                continue
            lines.append("")
            lines.append(T(g.lang, "summary_team", icon=TEAM_ICON[team], team=team.capitalize()))
            lines += [_entry_line(g, i, e, True) for i, e in enumerate(entries, 1)]
            if pending:
                lines.append(T(g.lang, "summary_pending", patient=g.name(g.patients[team]),
                               who=g.name(pending.asker), text=pending.text))
    return "\n".join(lines)[:4000]


async def summary(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    g = games.get(chat.id)
    if not g:
        await update.message.reply_text(T(db.get_lang(chat.id), "round_none"))
        return
    if g.phase not in (Phase.PLAYING, Phase.VOTING):
        await update.message.reply_text(T(g.lang, "round_not_playing"))
        return
    await update.message.reply_text(summary_text(g))


# ---------------------------------------------------------------- anti-spoiler
async def spoiler(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Delete group messages that reveal an identity."""
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
