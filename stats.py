"""/stats (group statistics) and /mystats (player statistics)."""
from telegram import Update
from telegram.ext import ContextTypes

import db
from game import ENIGMA, PSYOPS
from i18n import T

MIN_DR_A_GAMES = 3      # Dr. A ranking needs at least this many games as Dr. A

# Shared SQL: one row per (round, player) of a group
_BASE = ("FROM round_players rp JOIN rounds r ON r.id = rp.round_id "
         "LEFT JOIN users u ON u.user_id = rp.user_id WHERE r.chat_id = ?")
_NAME = "COALESCE(u.name, MAX(rp.name))"


def _mode_names(lang: str) -> dict[str, str]:
    return {ENIGMA: T(lang, "mode_enigma"), PSYOPS: T(lang, "mode_psyops")}


def _ranking(rows: list[tuple]) -> list[str]:
    return [f"{i}. {name}: {n}" for i, (name, n) in enumerate(rows, 1)]


async def stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    lang = db.get_lang(chat.id)
    if chat.type == "private":
        await update.message.reply_text(T(lang, "group_only"))
        return
    cid = (chat.id,)

    by_mode = db.query("SELECT mode, COUNT(*) FROM rounds WHERE chat_id = ? GROUP BY mode", cid)
    if not by_mode:
        await update.message.reply_text(T(lang, "stats_empty"))
        return
    names = _mode_names(lang)
    total = sum(n for _, n in by_mode)
    breakdown = " · ".join(f"{names.get(m, m)} {n}" for m, n in by_mode)
    lines = [T(lang, "stats_title"), T(lang, "stats_rounds", total=total, breakdown=breakdown)]

    # Top 5 by round wins / by identities guessed
    top_wins = db.query(
        f"SELECT {_NAME}, SUM(rp.won) AS n {_BASE} GROUP BY rp.user_id "
        "HAVING n > 0 ORDER BY n DESC, rp.user_id LIMIT 5", cid)
    if top_wins:
        lines += ["", T(lang, "stats_top_wins")] + _ranking(top_wins)
    top_guess = db.query(
        f"SELECT {_NAME}, SUM(rp.guessed) AS n {_BASE} GROUP BY rp.user_id "
        "HAVING n > 0 ORDER BY n DESC, rp.user_id LIMIT 5", cid)
    if top_guess:
        lines += ["", T(lang, "stats_top_guess")] + _ranking(top_guess)

    # Player with most wins in each mode
    best = []
    for mode in (ENIGMA, PSYOPS):
        row = db.query(
            f"SELECT {_NAME}, SUM(rp.won) AS n {_BASE} AND r.mode = ? "
            "GROUP BY rp.user_id HAVING n > 0 ORDER BY n DESC, rp.user_id LIMIT 1",
            cid + (mode,))
        if row:
            best.append(f"{names[mode]}: {row[0][0]} ({row[0][1]})")
    if best:
        lines += ["", T(lang, "stats_mode_best"), " · ".join(best)]

    # Dr. A who was caught least often (by rate, min. games)
    lines.append("")
    dra = db.query(
        f"SELECT {_NAME}, COUNT(*) AS n, SUM(rp.caught) AS c {_BASE} AND rp.role = 'dr_a' "
        "GROUP BY rp.user_id HAVING n >= ? ORDER BY (c * 1.0 / n) ASC, n DESC LIMIT 1",
        cid + (MIN_DR_A_GAMES,))
    if dra:
        lines.append(T(lang, "stats_dra", min=MIN_DR_A_GAMES, name=dra[0][0],
                       c=dra[0][2], n=dra[0][1]))
    else:
        lines.append(T(lang, "stats_dra_none", min=MIN_DR_A_GAMES))

    # Extras: fastest solve, spy wins
    fast = db.query(
        f"SELECT COALESCE(u.name, rp.name), rp.moves {_BASE} "
        "AND rp.guessed > 0 AND rp.role != 'spy' ORDER BY rp.moves ASC LIMIT 1", cid)
    if fast:
        lines.append(T(lang, "stats_fastest", name=fast[0][0], moves=fast[0][1]))
    spy_wins = db.query(
        "SELECT COUNT(*) FROM rounds WHERE chat_id = ? AND outcome = 'spy_win'", cid)[0][0]
    if spy_wins:
        lines.append(T(lang, "stats_spy", n=spy_wins))

    await update.message.reply_text("\n".join(lines))


async def mystats(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    chat, user = update.effective_chat, update.effective_user
    in_group = chat.type != "private"
    lang = db.get_lang(chat.id) if in_group else (
        "it" if (user.language_code or "").startswith("it") else "en")

    cond = "rp.user_id = ?" + (" AND r.chat_id = ?" if in_group else "")
    params = (user.id, chat.id) if in_group else (user.id,)
    base = f"FROM round_players rp JOIN rounds r ON r.id = rp.round_id WHERE {cond}"

    played, wins, guessed, fastest = db.query(
        "SELECT COUNT(*), COALESCE(SUM(rp.won), 0), COALESCE(SUM(rp.guessed), 0), "
        f"MIN(CASE WHEN rp.guessed > 0 AND rp.role != 'spy' THEN rp.moves END) {base}",
        params)[0]
    if not played:
        await update.message.reply_text(T(lang, "my_empty"))
        return

    names = _mode_names(lang)
    modes = db.query(f"SELECT r.mode, COUNT(*), SUM(rp.won) {base} GROUP BY r.mode", params)
    roles = db.query(
        f"SELECT rp.role, COUNT(*), SUM(rp.won) {base} GROUP BY rp.role "
        "ORDER BY COUNT(*) DESC", params)
    dra_n, dra_c = db.query(
        f"SELECT COUNT(*), COALESCE(SUM(rp.caught), 0) {base} AND rp.role = 'dr_a'",
        params)[0]

    scope = T(lang, "scope_group" if in_group else "scope_all")
    lines = [
        T(lang, "my_title", name=user.first_name, scope=scope),
        T(lang, "my_total", played=played, wins=wins, pct=round(100 * wins / played)),
        T(lang, "my_modes", text=" · ".join(
            f"{names.get(m, m)} {w}/{n}" for m, n, w in modes)),
        T(lang, "my_roles", text=" · ".join(
            f"{T(lang, 'role_' + r)} {w}/{n}" for r, n, w in roles)),
        T(lang, "my_favorite", role=T(lang, "role_" + roles[0][0]), n=roles[0][1]),
        T(lang, "my_guessed", n=guessed),
    ]
    if fastest is not None:
        lines.append(T(lang, "my_fastest", moves=fastest))
    if dra_n:
        lines.append(T(lang, "my_caught", c=dra_c, n=dra_n))
    await update.message.reply_text("\n".join(lines))
