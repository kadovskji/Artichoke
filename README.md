# Artichoke 🕵️

A Telegram party game bot about guessing famous identities with yes/no questions, inspired by [Project Artichoke](https://en.wikipedia.org/wiki/Project_Artichoke). Two game modes, English and Italian interface, statistics per group and per player.

## Game modes

An *identity* is a famous person or character (real or fictional, deity included) that has a Wikipedia page. Every move is either a question (`/ask`) or an attempt (`/try`); the round creator decides how many moves each participant gets (5, 10, 15 or 20).

Send `/rules` to the bot to get the full rules in private: if you are in a round, you receive only the rules of the mode you are playing.

### 🧪 K.H. Enigma (2+ players)

Named after Kaspar Hauser. Roles are drawn at random:

| Role | Who | Goal |
|:---:|:---:|:---:|
| 🧠 **Patient K** | 1 player | Secretly picks the identity and answers the questions in public (Yes / No / Don't know). Wins together with the first researcher who guesses, or with all the researchers if Dr. A is unmasked. |
| 🔬 **Researchers** | Everyone else | Find K's identity. The first to guess wins with K; the other researchers lose. |
| 🧑‍🔬 **Dr. A** | 1 player, only with 5+ players | Knows the identity and must stay undercover: pretends to investigate and misleads the others (his attempts can never win). Wins if nobody guesses and he is not unmasked. |

If nobody guesses (all researchers out of moves, or 10 minutes without activity) and Dr. A is in the game, everyone has 60 seconds to vote for the player they suspect: secret ballot, no changes, no self-votes. After each vote the bot shows who currently leads. Dr. A is unmasked only if he is strictly the most voted, so ties don't count. Without Dr. A, if nobody guesses everybody loses.

### 🕵️ PSY-OPS (4+ players)

Two teams, **Artichoke** 🟢 and **Bluebird** 🔵, race against each other for 10 minutes.

- Each team has a patient (K for Artichoke, H for Bluebird), announced in the group, and a secret team of researchers (everyone learns their role in private).
- Each patient privately picks a different identity and answers only the questions of their own team. Both teams play at the same time in the group and see each other's questions.
- `/ask` goes to your own patient, and `/try` is checked against your own patient's identity. **The first team to name its patient's identity wins** (patient and researchers). If time or moves run out, nobody wins.
- With an odd number of players one is a **🕶 KGB spy**, who belongs to no team. The spy cannot ask questions and starts with 0 attempts, gaining one every time a researcher guesses wrong. The spy makes attempts with `/try` in private chat with the bot, and wins by naming **both** identities before any team solves its own.

### Common rules

- *Don't know* answers don't cost the asker a move.
- A wrong attempt costs a move. Attempts are matched ignoring case, spaces, accents and punctuation, and through Wikipedia redirects (so "Dante" matches "Dante Alighieri").
- Identities are validated on Wikipedia and Wikidata: places, events, works, groups and real animals are refused, and so are disambiguation pages. Write the name as it appears on Wikipedia: for example “Super Mario” is the video game series, so use “Mario” for the character.
- If the bot is a group admin with the *Delete messages* permission, it removes messages that reveal an identity.

## Commands

| Command | Description |
|---|---|
| `/start` | Run it once in a private chat with the bot, so it can message you |
| `/newgame` | Create a round: choose the mode and the moves per participant |
| `/join` | Join the round |
| `/ready` | Start the round now (any joined player, if there are enough players) |
| `/wait <minutes>` | Extend the sign-up window (max 10 per use, decimals allowed, e.g. `/wait 3.5`) |
| `/ask <text>` | Ask a yes/no question |
| `/try <name>` | Try to name the identity |
| `/summary` | Questions and answers so far (grouped by team in PSY-OPS) |
| `/rules` | Receive the rules in private |
| `/stats` | Group statistics: top winners, most identities guessed, best player per mode, least caught Dr. A, fastest solve, spy wins |
| `/mystats` | Your statistics: wins per mode and per role, most played role, identities guessed, fastest solve, times caught as Dr. A (this group, or all groups if used in private) |
| `/stop` | Cancel the round (its creator or a group admin) |
| `/setlan en` | Set the group language to English (group admins) |
| `/setlan ita` | Set the group language to Italian (group admins) |
****

Sign-ups last 5 minutes, and the minimum number of players is 2 for K.H. Enigma and 4 for PSY-OPS.

## Setup

Requirements: Python 3.10+ and a bot token from [@BotFather](https://t.me/BotFather) (`/newbot`).

```bash
git clone https://github.com/kadovskji/Artichoke.git
cd Artichoke
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set the token as an environment variable and start the bot:

```bash
export BOT_TOKEN=your_token     # Windows: set BOT_TOKEN=your_token
python artichoke.py
```

In PyCharm, set `BOT_TOKEN` in the *Environment variables* of the Run Configuration, with `artichoke.py` as the script.

> ⚠️ Never commit the token. If it leaks, revoke it from BotFather (`/mybots` → your bot → *API Token* → *Revoke*).

Then:

1. Every player opens a private chat with the bot and presses `/start`.
2. Add the bot to the group and make it an **admin** with the *Delete messages* permission (needed for the spoiler filter).
3. Someone writes `/newgame`.

### Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BOT_TOKEN` | required | Telegram bot token |
| `DB_FILE` | `artichoke.db` | SQLite database path |
| `CONTACT_URL` | this repository | Contact URL put in the User-Agent of Wikipedia/Wikidata requests (Wikimedia asks for it): set it to your own repository or website |
| `REQUIRE_TAG` | empty | Comma-separated commands handled in groups only as `/command@BotName`, useful if another bot uses the same command (e.g. `summary,stats`) |

### Always-on hosting

The bot uses long polling, so it needs no domain or open ports. On a Linux server, a `systemd` unit keeps it running:

```ini
[Unit]
Description=Artichoke bot
After=network-online.target

[Service]
User=artichoke
WorkingDirectory=/home/artichoke/Artichoke
EnvironmentFile=/home/artichoke/Artichoke/.env
ExecStart=/home/artichoke/Artichoke/venv/bin/python artichoke.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Run only one instance per token, otherwise Telegram reports a `Conflict` error.

## Project structure

| File | Purpose |
|---|---|
| `artichoke.py` | Entry point: registers commands and handlers |
| `lobby.py` | `/newgame`, `/join`, `/ready`, `/wait`, `/stop`, `/setlan` |
| `roles.py` | Role assignment, identity selection, start of play |
| `play.py` | Questions, attempts, votes, `/summary`, round endings, spoiler filter |
| `wiki.py` | Wikipedia / Wikidata validation and guess matching |
| `stats.py` | `/stats` and `/mystats` |
| `rules.py` | `/rules` |
| `db.py` | SQLite persistence |
| `game.py` | Game model, timers and helpers |
| `i18n.py` | English and Italian strings |
| `check_identity.py` | Diagnostic tool: shows how a name is validated against Wikipedia and Wikidata |

## Troubleshooting

- **The bot says it couldn't verify an identity, or accepts anything** (even places): Wikipedia or Wikidata can't be reached from the server. Check the log with `sudo journalctl -u artichoke --no-pager | grep "check failed"`. A `403 Forbidden` usually means the User-Agent was refused: set `CONTACT_URL` to your own repository or website. Run `python check_identity.py "Roma"` to see exactly what the bot sees (the expected decision is REFUSE).
- **`Conflict: terminated by other getUpdates request`**: another copy of the bot is running with the same token. Stop it (PyCharm, another terminal or server).
- **`KeyError: 'BOT_TOKEN'`**: the token isn't set. Check the `.env` file (server) or the Run Configuration (PyCharm).
- **`ModuleNotFoundError`**: a `.py` file is missing, or the dependencies aren't installed (`pip install -r requirements.txt`).

## Notes

- Rounds in progress live in memory: a restart cancels them (statistics are kept in the database).
- If Wikipedia or Wikidata can't be reached, an identity is accepted without validation so the game isn't blocked: the patient is warned in private and the reason is written in the log. `python check_identity.py "Roma"` shows what the bot sees when validating a name.
- The accepted Wikidata classes can be widened in `wiki.py` (`CHARACTER_CLASSES`, `CHARACTER_LABELS`).

## License

Released under the MIT License: see [LICENSE](LICENSE).
