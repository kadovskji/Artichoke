"""Sign-up phase: /start, /newgame, /join, /ready, /wait, /stop, /setlan."""
import math
import time

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import roles
from game import (CONFIG_SECONDS, ENIGMA, LOBBY_SECONDS, MIN_PLAYERS, MOVE_OPTIONS,
                  PSYOPS, WAIT_MAX_MINUTES, Game, Phase, cancel_job, close_game,
                  games, schedule, user_game)
from i18n import T, parse_lang


async def is_admin(ctx, chat_id: int, user_id: int) -> bool:
    try:
        member = await ctx.bot.get_chat_member(chat_id, user_id)
    except TelegramError:
        return False
    return member.status in ("administrator", "creator")


def fmt_duration(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    m, s = divmod(seconds, 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def mode_name(g: Game) -> str:
    return T(g.lang, "mode_enigma" if g.mode == ENIGMA else "mode_psyops")


def lobby_text(g: Game) -> str:
    return T(g.lang, "lobby_text", creator=g.name(g.creator), mode=mode_name(g),
             moves=g.moves, min=MIN_PLAYERS[g.mode])


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
            InlineKeyboardButton(T(lang, "btn_enigma"), callback_data=f"m:{ENIGMA}"),
            InlineKeyboardButton(T(lang, "btn_psyops"), callback_data=f"m:{PSYOPS}"),
        ]]))


async def config_expired(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    g = games.get(ctx.job.chat_id)
    if g and g.phase in (Phase.MODE, Phase.MOVES):
        close_game(ctx, g)
        await ctx.bot.send_message(g.chat_id, T(g.lang, "config_expired"))


async def cb_mode(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    g = games.get(q.message.chat_id)
    lang = g.lang if g else db.get_lang(q.message.chat_id)
    if not g or g.phase != Phase.MODE:
        await q.answer(T(lang, "stale"), show_alert=True)
        return
    if q.from_user.id != g.creator:
        await q.answer(T(lang, "only_creator"), show_alert=True)
        return
    mode = q.data.split(":")[1]
    if mode not in (ENIGMA, PSYOPS):
        await q.answer()
        return
    g.mode = mode
    g.phase = Phase.MOVES
    schedule(ctx, config_expired, CONFIG_SECONDS, "config", g.chat_id)
    await q.answer()
    await q.edit_message_text(
        T(g.lang, "pick_moves", mode=mode_name(g)),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(str(n), callback_data=f"n:{n}") for n in MOVE_OPTIONS]]))


async def cb_moves(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    g = games.get(q.message.chat_id)
    lang = g.lang if g else db.get_lang(q.message.chat_id)
    if not g or g.phase != Phase.MOVES:
        await q.answer(T(lang, "stale"), show_alert=True)
        return
    if q.from_user.id != g.creator:
        await q.answer(T(lang, "only_creator"), show_alert=True)
        return
    n = int(q.data.split(":")[1])
    if n not in MOVE_OPTIONS:
        await q.answer()
        return
    g.moves = n
    g.phase = Phase.LOBBY
    cancel_job(ctx, "config", g.chat_id)
    g.lobby_end = time.time() + LOBBY_SECONDS
    schedule(ctx, lobby_expired, LOBBY_SECONDS, "lobby", g.chat_id)
    await q.answer()
    await q.edit_message_text(lobby_text(g))


# ---------------------------------------------------------------- /join /ready /wait
async def join(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    g = games.get(chat.id)
    if g and g.phase in (Phase.MODE, Phase.MOVES):
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


async def ready(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    g = games.get(chat.id)
    if not g or g.phase != Phase.LOBBY:
        await update.message.reply_text(T(lang, "lobby_none"))
        return
    if user.id not in g.players:
        await update.message.reply_text(T(lang, "only_players"))
        return
    if len(g.players) < MIN_PLAYERS[g.mode]:
        await update.message.reply_text(
            T(lang, "ready_need", min=MIN_PLAYERS[g.mode], n=len(g.players)))
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
    if len(g.players) < MIN_PLAYERS[g.mode]:
        close_game(ctx, g)
        await ctx.bot.send_message(g.chat_id, T(g.lang, "not_enough"))
        return
    await begin(ctx, g)


async def begin(ctx, g: Game) -> None:
    """Close the sign-ups and start the round."""
    cancel_job(ctx, "lobby", g.chat_id)
    await roles.start_round(ctx, g)


# ---------------------------------------------------------------- /stop /setlan
async def stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    g = games.get(chat.id)
    if not g:
        return
    if user.id != g.creator and not await is_admin(ctx, chat.id, user.id):
        await update.message.reply_text(T(g.lang, "stop_denied"))
        return
    close_game(ctx, g)
    await update.message.reply_text(T(g.lang, "stopped"))


async def setlan(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    if chat.type == "private":
        await update.message.reply_text(T(lang, "group_only"))
        return
    if not await is_admin(ctx, chat.id, user.id):
        await update.message.reply_text(T(lang, "setlan_admin"))
        return
    new = parse_lang(ctx.args[0] if ctx.args else None)
    if not new:
        await update.message.reply_text(T(lang, "setlan_usage"))
        return
    db.set_lang(chat.id, new)
    g = games.get(chat.id)
    if g:
        g.lang = new
    await update.message.reply_text(T(new, "setlan_ok"))
