"""Artichoke - a Telegram party game bot about guessing famous identities.

Modes: K.H. Enigma and PSY-OPS (rules: /rules in the bot, or README.md).

Run:  BOT_TOKEN=xxxx python artichoke.py
"""
import logging
import os

from telegram import BotCommand
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          MessageHandler, filters)

import lobby
import play
import roles
import rules
import stats

logging.basicConfig(level=logging.INFO)

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

# (command, English description, Italian description)
COMMANDS = [
    ("newgame", "Create a new round", "Crea un nuovo round"),
    ("join", "Join the round", "Unisciti al round"),
    ("ready", "Start the round now", "Avvia subito il round"),
    ("wait", "Extend sign-ups: /wait <minutes>", "Prolunga le iscrizioni: /wait <minuti>"),
    ("ask", "Ask a yes/no question", "Fai una domanda sì/no"),
    ("try", "Try to name the identity", "Prova a indovinare l'identità"),
    ("summary", "Questions and answers so far", "Domande e risposte finora"),
    ("rules", "Get the rules in private", "Ricevi le regole in privato"),
    ("stats", "Group statistics", "Statistiche del gruppo"),
    ("mystats", "Your statistics", "Le tue statistiche"),
    ("stop", "Cancel the current round", "Annulla il round in corso"),
    ("setlan", "Group language: en / ita", "Lingua del gruppo: en / ita"),
]


async def post_init(app: Application) -> None:
    await app.bot.set_my_commands([BotCommand(c, en) for c, en, _ in COMMANDS])
    await app.bot.set_my_commands([BotCommand(c, it) for c, _, it in COMMANDS],
                                  language_code="it")


def main() -> None:
    app = Application.builder().token(TOKEN).post_init(post_init).build()

    def command(name: str, handler) -> None:
        app.add_handler(CommandHandler(
            name, handler, filters=EXPLICIT if name in REQUIRE_TAG else None))

    command("start", lobby.start)
    command("newgame", lobby.newgame)
    command("join", lobby.join)
    command("ready", lobby.ready)
    command("wait", lobby.wait)
    command("stop", lobby.stop)
    command("setlan", lobby.setlan)
    command("ask", play.ask)
    command("try", play.try_cmd)
    command("summary", play.summary)
    command("rules", rules.rules)
    command("stats", stats.stats)
    command("mystats", stats.mystats)

    app.add_handler(CallbackQueryHandler(lobby.cb_mode, pattern=r"^m:"))
    app.add_handler(CallbackQueryHandler(lobby.cb_moves, pattern=r"^n:"))
    app.add_handler(CallbackQueryHandler(play.cb_answer, pattern=r"^a:"))
    app.add_handler(CallbackQueryHandler(play.cb_vote, pattern=r"^v:"))

    # Private text: a patient sending the identity they chose
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, roles.on_identity))
    # Group text: spoiler filter
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.GROUPS, play.spoiler))

    app.run_polling()


if __name__ == "__main__":
    main()
