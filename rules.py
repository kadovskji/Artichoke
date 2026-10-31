"""/rules: send the rules in private (only the mode being played, if in a round)."""
from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import db
import lobby
from game import ENIGMA, PSYOPS, games, user_game
from i18n import T


async def rules(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    in_group = chat.type != "private"
    g = games.get(user_game.get(user.id))       # the round this user takes part in, if any

    if g:
        lang = g.lang
    elif in_group:
        lang = db.get_lang(chat.id)
    else:
        lang = "it" if (user.language_code or "").startswith("it") else "en"

    # Inside a round: only the rules of the mode being played (if already chosen)
    modes = [g.mode] if g and g.mode else [ENIGMA, PSYOPS]
    try:
        for key in ["rules_general"] + [f"rules_{m}" for m in modes]:
            await ctx.bot.send_message(user.id, T(lang, key))
    except TelegramError:                       # the user never pressed /start in private
        if in_group:
            await lobby.ask_activation(update, ctx, lang)
        return
    if in_group:
        await update.message.reply_text(T(lang, "rules_sent", name=user.first_name))
