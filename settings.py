"""/settings: group settings menu (group admins only)."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
from game import games, is_admin
from i18n import T

KEYS = ("lang", "breaks", "attempts", "dra", "variants")


def _menu(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    cfg = db.get_settings(chat_id)
    lang = cfg["lang"]
    rows = [[InlineKeyboardButton(
        f"{T(lang, 'set_' + k)}: {T(lang, f'set_{k}_{cfg[k]}')}", callback_data=f"s:{k}")]
        for k in KEYS]
    return T(lang, "settings_title"), InlineKeyboardMarkup(rows)


def _submenu(chat_id: int, key: str) -> tuple[str, InlineKeyboardMarkup]:
    cfg = db.get_settings(chat_id)
    lang = cfg["lang"]
    rows = [[InlineKeyboardButton(
        ("✅ " if v == cfg[key] else "") + T(lang, f"set_{key}_{v}"),
        callback_data=f"s:{key}:{v}")] for v in db.ALLOWED_SETTINGS[key]]
    rows.append([InlineKeyboardButton(T(lang, "btn_back"), callback_data="s:menu")])
    text = f"{T(lang, 'set_' + key)}\n\n{T(lang, 'settings_sub_' + key)}"
    return text, InlineKeyboardMarkup(rows)


async def settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    lang = db.get_lang(chat.id)
    if chat.type == "private":
        await update.message.reply_text(T(lang, "group_only"))
        return
    db.track_chat(chat.id, chat.title)
    if not await is_admin(ctx, chat.id, user.id):
        await update.message.reply_text(T(lang, "settings_admin"))
        return
    text, kb = _menu(chat.id)
    await update.message.reply_text(text, reply_markup=kb)


async def cb_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    chat_id = q.message.chat_id
    if not await is_admin(ctx, chat_id, q.from_user.id):
        await q.answer(T(db.get_lang(chat_id), "settings_admin"), show_alert=True)
        return
    parts = q.data.split(":")
    if len(parts) == 3 and parts[1] in KEYS:
        key, value = parts[1], parts[2]
        if db.set_setting(chat_id, key, value):
            g = games.get(chat_id)
            if key == "lang" and g:
                g.lang = value
            await q.answer(T(db.get_lang(chat_id), "settings_saved"))
        text, kb = _submenu(chat_id, key)
    elif len(parts) == 2 and parts[1] in KEYS:
        await q.answer()
        text, kb = _submenu(chat_id, parts[1])
    else:
        await q.answer()
        text, kb = _menu(chat_id)
    try:
        await q.edit_message_text(text, reply_markup=kb)
    except TelegramError:
        pass                                    # message not modified
