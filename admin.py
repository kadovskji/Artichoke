"""Global bot administration: /admin (private chat only, ADMIN_ID users only).

Buttons: Update (announcement to all groups), Restart, Pull (git pull + pip), Log.
The command is intentionally absent from /rules and from the command menu.
Messages are in Italian: the panel is for the bot owner only.
"""
import asyncio
import html
import json
import logging
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import Forbidden, TelegramError
from telegram.ext import ContextTypes

import db
import logs
from game import games

LOG = logging.getLogger("artichoke.admin")

# Where /admin → Restart remembers the panel message, to confirm the restart afterwards
RESTART_FILE = os.environ.get("RESTART_FILE", "restart.flag")

ADMIN_IDS = {int(x) for x in os.environ.get("ADMIN_ID", "").replace(" ", "").split(",")
             if x.strip().isdigit()}

# user_id -> {"step": "en" | "it" | "confirm", "en": str, "it": str}
pending: dict[int, dict] = {}


def is_bot_admin(uid: int) -> bool:
    return uid in ADMIN_IDS


def _menu() -> tuple[str, InlineKeyboardMarkup]:
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Update", callback_data="ad:update"),
         InlineKeyboardButton("🔁 Restart", callback_data="ad:restart")],
        [InlineKeyboardButton("⬇️ Pull", callback_data="ad:pull"),
         InlineKeyboardButton("📜 Log", callback_data="ad:log")],
    ])
    return f"🛠 Pannello admin\nRound attivi: {len(games)}", kb


def _back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Menu", callback_data="ad:menu")]])


async def admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    if chat.type != "private" or not is_bot_admin(user.id):
        return                                  # silent: the command doesn't "exist"
    pending.pop(user.id, None)
    text, kb = _menu()
    await update.message.reply_text(text, reply_markup=kb)


async def cb_admin(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    uid = q.from_user.id
    if not is_bot_admin(uid):
        await q.answer()
        return
    action = q.data.split(":", 1)[1]
    await q.answer()

    if action == "menu":
        pending.pop(uid, None)
        text, kb = _menu()
        await q.edit_message_text(text, reply_markup=kb)

    elif action == "update":
        pending[uid] = {"step": "en"}
        await q.edit_message_text(
            "📢 Invio un avviso a tutti i gruppi attivi.\n"
            "Scrivimi il testo in INGLESE (per i gruppi in inglese).",
            reply_markup=_back())

    elif action == "send":
        data = pending.pop(uid, None)
        if not data or data.get("step") != "confirm":
            await q.edit_message_text("Nessun avviso in sospeso.", reply_markup=_back())
            return
        await q.edit_message_text("Invio in corso…")
        sent, failed = await _broadcast(ctx, data)
        LOG.info("announcement sent by %s: %d ok, %d failed", uid, sent, failed)
        await q.edit_message_text(f"✅ Avviso inviato a {sent} gruppi ({failed} errori).",
                                  reply_markup=_back())

    elif action == "restart":
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Riavvia ora", callback_data="ad:restart_yes"),
            InlineKeyboardButton("⬅️ Annulla", callback_data="ad:menu")]])
        await q.edit_message_text(
            f"🔁 Riavviare il bot?\nRound attivi che andranno persi: {len(games)}", reply_markup=kb)

    elif action == "restart_yes":
        await q.edit_message_text("🔁 Riavvio in corso…")
        await restart(update, ctx)

    elif action == "pull":
        await q.edit_message_text("⬇️ Eseguo git pull e aggiorno le dipendenze…")
        out = await pull()
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Riavvia", callback_data="ad:restart")],
            [InlineKeyboardButton("⬅️ Menu", callback_data="ad:menu")]])
        await q.edit_message_text(f"⬇️ Pull completato:\n\n{out}"[:4000], reply_markup=kb)

    elif action == "log":
        lines = logs.recent(minutes=60, limit=50)
        body = "\n".join(lines) if lines else "(nessun evento nell'ultima ora)"
        body = body[-3500:]
        await q.edit_message_text(
            f"📜 Log dell'ultima ora (max 50 righe):\n<pre>{html.escape(body)}</pre>",
            parse_mode="HTML", reply_markup=_back())


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> bool:
    """Private text from the admin while composing an announcement. True if consumed."""
    uid = update.effective_user.id
    data = pending.get(uid)
    if not data or not is_bot_admin(uid):
        return False
    text = update.message.text.strip()
    if data["step"] == "en":
        data["en"], data["step"] = text, "it"
        await update.message.reply_text("Ora il testo in ITALIANO.")
    elif data["step"] == "it":
        data["it"], data["step"] = text, "confirm"
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("📤 Invia", callback_data="ad:send"),
            InlineKeyboardButton("⬅️ Annulla", callback_data="ad:menu")]])
        await update.message.reply_text(
            f"Anteprima\n\n🇬🇧 {data['en']}\n\n🇮🇹 {data['it']}\n\n"
            f"Gruppi in inglese: {len(db.chats_by_lang('en'))} · "
            f"in italiano: {len(db.chats_by_lang('it'))}", reply_markup=kb)
    else:
        return False
    return True


async def _broadcast(ctx, data: dict) -> tuple[int, int]:
    sent = failed = 0
    for lang in ("en", "it"):
        for chat_id in db.chats_by_lang(lang):
            try:
                await ctx.bot.send_message(chat_id, data[lang])
                sent += 1
            except Forbidden:
                db.set_chat_active(chat_id, False)      # the bot was removed from the group
                failed += 1
            except TelegramError:
                failed += 1
            await asyncio.sleep(0.05)                   # stay well under Telegram's limits
    return sent, failed


async def pull() -> str:
    """git pull --ff-only, then pip install -r requirements.txt."""
    out = []
    for cmd in (["git", "pull", "--ff-only"],
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
            raw, _ = await asyncio.wait_for(proc.communicate(), timeout=180)
            text = raw.decode("utf-8", "replace").strip()
            tail = "\n".join(text.splitlines()[-8:])
            out.append(f"$ {' '.join(cmd[:3])}\n{tail}\n(codice {proc.returncode})")
        except (OSError, asyncio.TimeoutError) as e:
            out.append(f"$ {' '.join(cmd[:3])}\nerrore: {e}")
    return "\n\n".join(out)


async def restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Replace the process with a fresh one.

    The update that triggered the restart is acknowledged first, so Telegram doesn't
    deliver it again to the new process (which would restart it forever).
    """
    LOG.info("restart requested by %s", update.effective_user.id)
    msg = update.callback_query.message if update.callback_query else None
    if msg:
        try:
            with open(RESTART_FILE, "w", encoding="utf-8") as f:
                json.dump({"chat_id": msg.chat_id, "message_id": msg.message_id}, f)
        except OSError as e:
            LOG.warning("could not save the restart marker: %s", e)
    try:
        await ctx.bot.get_updates(offset=update.update_id + 1, limit=1, timeout=0)
    except TelegramError as e:
        LOG.warning("could not acknowledge the update before restarting: %s", e)
    logging.shutdown()
    os.execv(sys.executable, [sys.executable] + sys.argv)


async def notify_restart(bot) -> None:
    """After a restart requested from /admin: turn the panel message into a confirmation."""
    try:
        with open(RESTART_FILE, encoding="utf-8") as f:
            info = json.load(f)
        os.remove(RESTART_FILE)
    except (OSError, ValueError):
        return
    text, kb = _menu()
    try:
        await bot.edit_message_text("✅ Bot riavviato.\n\n" + text, chat_id=info["chat_id"],
                                    message_id=info["message_id"], reply_markup=kb)
    except (TelegramError, KeyError) as e:
        LOG.warning("could not confirm the restart: %s", e)
