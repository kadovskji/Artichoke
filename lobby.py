"""Sign-up phase: /start, /newgame, mode/teams/moves buttons, /join, /ready, /wait, /stop."""
import math
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import db
import play
import roles
from game import (ARTICHOKE, CONFIG_SECONDS, LOBBY_SECONDS, MOVE_OPTIONS, STARGATE,
                  TEAM_COUNTS, WAIT_MAX_MINUTES, Game, Phase, cancel_job, close_game,
                  fmt_duration, games, is_admin, min_players, schedule, stargate_layout,
                  user_game, valid_totals)
from i18n import T

CONFIG_PHASES = (Phase.MODE, Phase.TEAMS, Phase.MOVES)


def mode_name(g: Game) -> str:
    if g.mode == STARGATE:
        return f"{T(g.lang, 'mode_stargate')} ({T(g.lang, 'teams_n', n=g.teams_count)})"
    return T(g.lang, "mode_artichoke")


def lobby_text(g: Game) -> str:
    moves = g.moves if g.moves else T(g.lang, "moves_auto")
    return T(g.lang, "lobby_text", creator=g.name(g.creator), mode=mode_name(g),
             moves=moves, min=min_players(g.mode, g.teams_count))


async def ask_activation(update: Update, ctx: ContextTypes.DEFAULT_TYPE, lang: str) -> None:
    url = f"https://t.me/{ctx.bot.username}?start=join"
    await update.message.reply_text(
        T(lang, "need_start", name=update.effective_user.first_name),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(T(lang, "btn_activate"), url=url)]]))


# ---------------------------------------------------------------- /start
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type != "private":
        await update.message.reply_text(T(db.get_lang(chat.id), "start_group"))
        return
    db.register_start(user.id, user.first_name)
    lang = "it" if (user.language_code or "").startswith("it") else "en"
    await update.message.reply_text(T(lang, "start_private"))


# ---------------------------------------------------------------- /newgame
async def newgame(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    if chat.type == "private":
        await update.message.reply_text(T(lang, "group_only"))
        return
    db.track_chat(chat.id, chat.title)
    if chat.id in games:
        await update.message.reply_text(T(lang, "game_exists"))
        return
    if user.id in user_game:
        await update.message.reply_text(T(lang, "already_in_game"))
        return
    if not db.has_started(user.id):
        await ask_activation(update, ctx, lang)
        return
    db.touch_user(user.id, user.first_name)
    g = Game(chat.id, user.id, lang)
    g.players[user.id] = user.first_name
    games[chat.id] = g
    user_game[user.id] = chat.id
    schedule(ctx, config_expired, CONFIG_SECONDS, "config", chat.id)
    await update.message.reply_text(
        T(lang, "pick_mode", name=user.first_name),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(T(lang, "btn_artichoke"), callback_data=f"m:{ARTICHOKE}"),
            InlineKeyboardButton(T(lang, "btn_stargate"), callback_data=f"m:{STARGATE}"),
        ]]))


async def config_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase in CONFIG_PHASES:
        close_game(ctx, g, "config timeout")
        await ctx.bot.send_message(g.chat_id, T(g.lang, "config_expired"))


async def _creator_gate(q, g: Game | None, phase: Phase) -> bool:
    """Common checks for the creator's configuration buttons."""
    lang = g.lang if g else db.get_lang(q.message.chat_id)
    if not g or g.phase != phase:
        await q.answer(T(lang, "stale"), show_alert=True)
        return False
    if q.from_user.id != g.creator:
        await q.answer(T(lang, "only_creator"), show_alert=True)
        return False
    return True


async def _open_lobby(ctx, q, g: Game) -> None:
    g.phase = Phase.LOBBY
    cancel_job(ctx, "config", g.chat_id)
    g.lobby_end = time.time() + LOBBY_SECONDS
    schedule(ctx, lobby_expired, LOBBY_SECONDS, "lobby", g.chat_id)
    await q.edit_message_text(lobby_text(g))


async def _after_options(ctx, q, g: Game) -> None:
    """Mode (and teams) chosen: ask for the moves if the group lets the creator pick them."""
    if db.get_settings(g.chat_id)["attempts"] == "creator":
        g.phase = Phase.MOVES
        schedule(ctx, config_expired, CONFIG_SECONDS, "config", g.chat_id)
        await q.edit_message_text(
            T(g.lang, "pick_moves", mode=mode_name(g)),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(str(n), callback_data=f"n:{n}") for n in MOVE_OPTIONS]]))
    else:
        g.moves = 0                                 # automatic: computed when the round starts
        await _open_lobby(ctx, q, g)


async def cb_mode(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    g = games.get(q.message.chat_id)
    if not await _creator_gate(q, g, Phase.MODE):
        return
    mode = q.data.split(":")[1]
    if mode not in (ARTICHOKE, STARGATE):
        await q.answer()
        return
    g.mode = mode
    schedule(ctx, config_expired, CONFIG_SECONDS, "config", g.chat_id)
    await q.answer()
    if mode == STARGATE:
        g.phase = Phase.TEAMS
        await q.edit_message_text(
            T(g.lang, "pick_teams"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(T(g.lang, "teams_n", n=n), callback_data=f"t:{n}")
                for n in TEAM_COUNTS]]))
        return
    await _after_options(ctx, q, g)


async def cb_teams(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    g = games.get(q.message.chat_id)
    if not await _creator_gate(q, g, Phase.TEAMS):
        return
    n = int(q.data.split(":")[1])
    if n not in TEAM_COUNTS:
        await q.answer()
        return
    g.teams_count = n
    await q.answer()
    await _after_options(ctx, q, g)


async def cb_moves(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    g = games.get(q.message.chat_id)
    if not await _creator_gate(q, g, Phase.MOVES):
        return
    n = int(q.data.split(":")[1])
    if n not in MOVE_OPTIONS:
        await q.answer()
        return
    g.moves = n
    await q.answer()
    await _open_lobby(ctx, q, g)


# ---------------------------------------------------------------- /join /ready /wait
async def join(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    g = games.get(chat.id)
    if g and g.phase in CONFIG_PHASES:
        await update.message.reply_text(T(lang, "join_wait_config"))
        return
    if not g or g.phase != Phase.LOBBY:
        await update.message.reply_text(T(lang, "lobby_none"))
        return
    if user.id in g.players:
        await update.message.reply_text(T(lang, "join_already"))
        return
    if user.id in user_game:
        await update.message.reply_text(T(lang, "join_other"))
        return
    if not db.has_started(user.id):
        await ask_activation(update, ctx, lang)
        return
    db.touch_user(user.id, user.first_name)
    g.players[user.id] = user.first_name
    user_game[user.id] = chat.id
    await update.message.reply_text(
        T(lang, "joined", name=user.first_name, n=len(g.players)))


def _layout_problem(g: Game) -> str | None:
    """Text explaining why the current players can't play, or None if all is fine."""
    n = len(g.players)
    if n < min_players(g.mode, g.teams_count):
        return "need"
    if g.mode == STARGATE and stargate_layout(n, g.teams_count) is None:
        return "layout"
    return None


async def ready(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """In the lobby: start now. During a /hold pause: resume the round."""
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    g = games.get(chat.id)
    if g and g.paused:
        if user.id not in g.players:
            await update.message.reply_text(T(lang, "only_players"))
            return
        await play.resume(ctx, g, early=True)
        return
    if not g or g.phase != Phase.LOBBY:
        await update.message.reply_text(T(lang, "lobby_none"))
        return
    if user.id not in g.players:
        await update.message.reply_text(T(lang, "only_players"))
        return
    n = len(g.players)
    problem = _layout_problem(g)
    if problem == "need":
        await update.message.reply_text(
            T(lang, "ready_need", min=min_players(g.mode, g.teams_count), n=n))
        return
    if problem == "layout":
        hint = ", ".join(map(str, valid_totals(g.teams_count, n + 1)))
        await update.message.reply_text(
            T(lang, "ready_layout", teams=g.teams_count, n=n, list=hint))
        return
    await begin(ctx, g)


async def wait(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    g = games.get(chat.id)
    if not g or g.phase != Phase.LOBBY:
        await update.message.reply_text(T(lang, "lobby_none"))
        return
    if user.id not in g.players:
        await update.message.reply_text(T(lang, "only_players"))
        return
    arg = (ctx.args[0] if ctx.args else "").replace(",", ".")
    try:
        minutes = float(arg)
    except ValueError:
        minutes = float("nan")
    if not math.isfinite(minutes) or minutes <= 0:
        await update.message.reply_text(T(lang, "wait_usage"))
        return
    if minutes > WAIT_MAX_MINUTES:
        await update.message.reply_text(T(lang, "wait_max"))
        return
    g.lobby_end += minutes * 60
    left = g.lobby_end - time.time()
    schedule(ctx, lobby_expired, left, "lobby", g.chat_id)
    await update.message.reply_text(
        T(lang, "wait_ok", added=fmt_duration(minutes * 60), left=fmt_duration(left)))


async def lobby_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if not g or g.phase != Phase.LOBBY:
        return
    problem = _layout_problem(g)
    if problem == "need":
        close_game(ctx, g, "not enough players")
        await ctx.bot.send_message(g.chat_id, T(g.lang, "not_enough"))
        return
    if problem == "layout":
        hint = ", ".join(map(str, valid_totals(g.teams_count, len(g.players) + 1)))
        close_game(ctx, g, "uneven teams")
        await ctx.bot.send_message(g.chat_id, T(g.lang, "bad_layout", list=hint))
        return
    await begin(ctx, g)


async def begin(ctx, g: Game) -> None:
    """Close the sign-ups and start the round."""
    cancel_job(ctx, "lobby", g.chat_id)
    await roles.start_round(ctx, g)


# ---------------------------------------------------------------- /stop
async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    g = games.get(chat.id)
    if not g:
        return
    if user.id != g.creator and not await is_admin(ctx, chat.id, user.id):
        await update.message.reply_text(T(g.lang, "stop_denied"))
        return
    await play.clear_pending(ctx, g)
    close_game(ctx, g, "stopped")
    await update.message.reply_text(T(g.lang, "stopped"))
