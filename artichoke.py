"""Artichoke - a Telegram party game bot about guessing famous identities.

Modes: Artichoke and Stargate (rules: /rules in the bot, or README.md).

Run:  BOT_TOKEN=xxxx python artichoke.py
"""
import logging
import os

import logs

logs.setup()

from telegram import BotCommand, Update                               # noqa: E402
from telegram.ext import (Application, CallbackQueryHandler, ChatMemberHandler,  # noqa: E402
                          CommandHandler, ContextTypes, MessageHandler, filters)

import admin                                                          # noqa: E402
import db                                                             # noqa: E402
import lobby                                                          # noqa: E402
import play                                                           # noqa: E402
import roles                                                          # noqa: E402
import rules                                                          # noqa: E402
import settings                                                       # noqa: E402
import stats                                                          # noqa: E402

LOG = logging.getLogger("artichoke")

TOKEN = os.environ["BOT_TOKEN"]

# Commands that, in groups, are handled only when written with the bot's tag
# (e.g. /summary@ArtichokeBot). Useful when another bot in the group uses the same
# command. Comma-separated list in the REQUIRE_TAG environment variable.
REQUIRE_TAG = {c.strip().lstrip("/")
               for c in os.environ.get("REQUIRE_TAG", "").split(",") if c.strip()}


class ExplicitCommand(filters.MessageFilter):
    """Accept a command only if written as /command@BotName (in groups)."""

    def filter(self, message) -> bool:
        if message.chat.type == "private":
            return True
        for e in message.entities or []:
            if e.type == "bot_command" and e.offset == 0:
                return "@" in message.parse_entity(e)
        return False


EXPLICIT = ExplicitCommand()

# (command, English description, Italian description). /admin is deliberately not listed.
COMMANDS = [
    ("newgame", "Create a new round", "Crea un nuovo round"),
    ("join", "Join the round", "Unisciti al round"),
    ("nextgame", "Get notified when the next round opens (again: cancel)", "Ricevi un avviso all'apertura del prossimo round (di nuovo: annulla)"),
    ("ready", "Start the round now / resume after a pause", "Avvia subito / riprendi dopo la pausa"),
    ("wait", "Extend sign-ups: /wait <minutes>", "Prolunga le iscrizioni: /wait <minuti>"),
    ("hold", "Pause the round: /hold <minutes>", "Pausa il round: /hold <minuti>"),
    ("ask", "Ask a yes/no question", "Fai una domanda sì/no"),
    ("try", "Try to name the identity", "Prova a indovinare l'identità"),
    ("arrest", "Stargate: Agent Skip arrests K", "Stargate: l'agente Skip arresta K"),
    ("summary", "Questions and answers so far", "Domande e risposte finora"),
    ("rules", "Get the rules in private", "Ricevi le regole in privato"),
    ("stats", "Group statistics", "Statistiche del gruppo"),
    ("mystats", "Your statistics", "Le tue statistiche"),
    ("settings", "Group settings (admins)", "Impostazioni del gruppo (admin)"),
    ("stop", "Cancel the current round", "Annulla il round in corso"),
]

_seen_chats: set[int] = set()


async def post_init(app: Application) -> None:
    await admin.notify_restart(app.bot)
    await app.bot.set_my_commands([BotCommand(c, en) for c, en, _ in COMMANDS])
    await app.bot.set_my_commands([BotCommand(c, it) for c, _, it in COMMANDS],
                                  language_code="it")


async def track_group(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Remember every group where the bot sees activity (for admin announcements)."""
    chat = update.effective_chat
    if chat and chat.id not in _seen_chats:
        _seen_chats.add(chat.id)
        db.track_chat(chat.id, chat.title)


async def my_chat_member(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """The bot was added to / removed from a group."""
    change = update.my_chat_member
    if change.chat.type == "private":
        return
    active = change.new_chat_member.status in ("member", "administrator")
    db.set_chat_active(change.chat.id, active, change.chat.title)
    if active:
        _seen_chats.add(change.chat.id)
    else:
        _seen_chats.discard(change.chat.id)


async def private_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Private text: the bot admin composing an announcement, or K sending an identity."""
    if await admin.handle_text(update, ctx):
        return
    if await roles.on_prediction(update, ctx):
        return
    await roles.on_identity(update, ctx)


async def on_error(update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    LOG.error("unhandled error", exc_info=ctx.error)


def main() -> None:
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    def command(name: str, handler) -> None:
        app.add_handler(CommandHandler(
            name, handler, filters=EXPLICIT if name in REQUIRE_TAG else None))

    command("start", lobby.start)
    command("newgame", lobby.newgame)
    command("nextgame", lobby.nextgame)
    command("join", lobby.join)
    command("ready", lobby.ready)
    command("wait", lobby.wait)
    command("stop", lobby.stop)
    command("hold", play.hold)
    command("ask", play.ask)
    command("try", play.try_cmd)
    command("arrest", play.arrest)
    command("summary", play.summary)
    command("settings", settings.settings)
    command("rules", rules.rules)
    command("stats", stats.stats)
    command("mystats", stats.mystats)
    app.add_handler(CommandHandler("admin", admin.admin, filters=filters.ChatType.PRIVATE))
    app.add_handler(CommandHandler("undo", roles.undo_prediction, filters=filters.ChatType.PRIVATE))

    app.add_handler(CallbackQueryHandler(lobby.cb_mode, pattern=r"^m:"))
    app.add_handler(CallbackQueryHandler(lobby.cb_variant, pattern=r"^r:"))
    app.add_handler(CallbackQueryHandler(lobby.cb_teams, pattern=r"^t:"))
    app.add_handler(CallbackQueryHandler(lobby.cb_moves, pattern=r"^n:"))
    app.add_handler(CallbackQueryHandler(play.cb_answer, pattern=r"^a:"))
    app.add_handler(CallbackQueryHandler(play.cb_vote, pattern=r"^v:"))
    app.add_handler(CallbackQueryHandler(play.cb_arrest, pattern=r"^k:"))
    app.add_handler(CallbackQueryHandler(settings.cb_settings, pattern=r"^s:"))
    app.add_handler(CallbackQueryHandler(admin.cb_admin, pattern=r"^ad:"))

    app.add_handler(MessageHandler(filters.ChatType.GROUPS, track_group), group=-2)
    app.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, private_text))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, play.spoiler))
    app.add_error_handler(on_error)

    LOG.info("bot starting (admins: %d)", len(admin.ADMIN_IDS))
    app.run_polling()


if __name__ == "__main__":
    main()
