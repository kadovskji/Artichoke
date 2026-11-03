# Artichoke 🕵️

A Telegram party game bot about guessing famous identities with yes/no questions. Each mode is inspired by a secret Cold War psychological program: [Project Artichoke](https://en.wikipedia.org/wiki/Project_Artichoke) and the [Stargate Project](https://en.wikipedia.org/wiki/Stargate_Project). English and Italian interface, per-group settings, statistics per group and per player.

## Game modes

An *identity* is a famous person or character (real or fictional, deity included) that has a Wikipedia page. Every move is either a question (`/ask`) or an attempt (`/try`). Send `/rules` to the bot to get the rules in private: if you are in a round, you receive only the rules of the mode you are playing.

### Moves per person

Computed automatically from the number of players (group admins can let the round creator choose among 5/7/10/15/20 in `/settings`):

| Players | Moves each |
|---|---|
| 2 | 25 |
| 3 | 15 |
| 4–6 | 10 |
| 7–8 | 7 |
| 9–15 | 5 |
| 16+ | 3 |

#
### 🧪 Artichoke (`artichokemode`, 2+ players)

| Role | Who | Goal |
|:---:|:---:|:---:|
| 🧠 **Patient K** | 1 player | Secretly picks the identity and answers the questions in public (Yes / No / Don't know) within 5 minutes each. Wins with the first researcher who guesses. |
| 🔬 **Researchers** | everyone else | Find K's identity. The first to guess wins with K; the other researchers lose. |
| 🧑‍🔬 **Dr. A** | 1 player, only with 5+ players | Knows the identity and must stay undercover: pretends to investigate and misleads the others (his attempts can never win). Present in 70% of the rounds with 5+ players (always, if the group chooses so in `/settings`). |

**End of the round.** The round ends when a researcher guesses, when all researchers are out of moves, or after 10 minutes without activity.

**If a researcher guesses**, K and that researcher win together; everyone else loses.

**If nobody guesses:**
- **2–4 players:** everybody loses.
- **5+ players:** everybody votes for 90 seconds to find out who Dr. A is. Secret ballot, no changes, no self-votes; the bot shows the current leader after each vote. The options are:
  - every other player (if you suspect that player);
  - *No Dr. A* (if you think there is no Dr. A).

**To win the vote:**
- you must have voted for the right option (Dr. A, or *No Dr. A* if he isn't in the game);
- the right option must get strictly more votes than any other option, so ties don't count;
- only the players who voted for it win.

Otherwise Dr. A (if present) wins alone; if he isn't in the game, nobody wins.  

#
### 🕵️ Stargate (`stargatemode`, 4+ players)

The creator picks 2, 3 or 4 teams. Teams are named at random among *Grill Flame*, *Center Lane*, *Sun Streak* and *Gondola Wish*. Everyone knows which teams are in play and their own team, but not their teammates.

| Teams | Minimum players (K and Agent Skip included) |
|---|---|
| 2 | 4 |
| 3 | 8 |
| 4 | 10 |

Besides Whistleblower K and Agent Skip, the researchers are split into teams of the **same size**: at least 2 per team (1 is enough with two teams). If the players can't be split evenly, the bot says which numbers of players work and the round does not start.

| Role | Who | Goal |
|:---:|:---:|:---:|
| 🔬 **Researchers** | in teams | Name the secret identity. The first team to do it wins together with K. |
| 🧠 **Whistleblower K** | 1 player, **secret** | Hides among the researchers and picks the only identity of the round. K answers every question **in private** (the bot publishes the answer without saying who gave it). To blend in, K also asks questions and makes attempts: K can answer their own questions only with *Don't know*, and K's attempts are always wrong. K wins with the team that names the identity. |
| 🕶 **Agent Skip** | 1 player, **known to all** | Find out who Whistleblower K is and arrest them. |

- Everybody (K and Skip too) has the same number of moves, questions and attempts together. In this mode *Don't know* **does cost a move**, for everyone, so that the moves left shown in `/summary` can't give K away.
- `/summary` doesn't show the teams.
- **Agent Skip's arrests:** Skip starts with 0 and gains one every time a player guesses wrong (K's wrong attempts count too, max 2 at a time). `/arrest` lets Skip pick the player they think is K. While the round is on Skip can use **only 1** arrest; the other one is for the end of the round. Wrong arrests are public (the arrested player is not K).
- **End of the round:** the round ends when a team names the identity, when all researchers are out of moves, or after 10 minutes without activity. If Skip still has arrests, Skip has 90 seconds to use them. The result is announced after that, unless Skip finds K.
- **Skip can also** ask questions, and try the identity **in private** with `/try <name>`: if Skip guesses it, `/summary` is disabled for all the other players.

**How to win:**

- The first team that names the identity wins together with K.
- Agent Skip wins **alone** (everyone else loses) by arresting K, even at the end of the round.
- If nobody names the identity and Skip doesn't find K, nobody wins.


## Common rules

- *Don't know* answers don't cost the asker a move; a wrong attempt costs a move. Attempts are matched ignoring case, spaces, accents and punctuation, and through Wikipedia redirects (so "Dante" matches "Dante Alighieri").
- Identities are validated on Wikipedia and Wikidata: places, events, works, groups and real animals are refused, and so are disambiguation pages. Write the name as it appears on Wikipedia.
- If the bot is a group admin with the *Delete messages* permission, it removes messages that reveal the identity.
- **Pause**: `/hold <minutes>` freezes every timer of the round (max 10 minutes per pause, once per player, 30 minutes in total per round). `/ready` from any player resumes it early. Group admins can disable it or restrict it to admins in `/settings`.

## Commands

| Command | Description |
|---|---|
| `/start` | Run it once in a private chat with the bot, so it can message you |
| `/newgame` | Create a round: choose the mode (and teams, and moves if the group allows it) |
| `/join` | Join the round |
| `/ready` | Start the round now (any joined player, if there are enough players); during a pause, resume the round |
| `/wait <minutes>` | Extend the sign-up window (max 10 per use, decimals allowed, e.g. `/wait 3.5`) |
| `/hold <minutes>` | Pause the round (see above) |
| `/ask <text>` | Ask a yes/no question (one at a time) |
| `/try <name>` | Try to name the identity (Agent Skip: in private chat) |
| `/arrest` | Stargate, Agent Skip only: arrest the player you think is Whistleblower K |
| `/summary` | Questions and answers so far, and moves left (no teams shown) |
| `/rules` | Receive the rules in private |
| `/stats` | Group statistics: top winners, most identities guessed, best player per mode, least caught Dr. A, fastest solve, Skip wins |
| `/mystats` | Your statistics: wins per mode and per role, most played role, identities guessed, fastest solve, times caught as Dr. A (this group, or all groups if used in private) |
| `/settings` | Group settings (group admins): see below |
| `/stop` | Cancel the round (its creator or a group admin) |
| `/admin` | **Bot owner only**, private chat only. Not shown in the command menu or in `/rules`: see below |

Sign-ups last 5 minutes. `/setlan` no longer exists: the language is now in `/settings`.

### Group settings (`/settings`)

| Setting | Options | Default |
|---|---|---|
| 🌐 Language | English / Italiano | English |
| ⏸ Allow breaks | Everyone / Admins only / Off | Everyone |
| 🎯 Attempts | Automatic / Chosen by the creator (5, 7, 10, 15, 20) | Automatic |
| 🧑‍🔬 Dr. A | 30% chance of absence / Always present (5+ players) | 30% absence |

### Bot administration (`/admin`)

Only the Telegram user IDs listed in the `ADMIN_ID` environment variable can use it, and only in a private chat with the bot (for anyone else the command does nothing). Find your ID with [@userinfobot](https://t.me/userinfobot). The panel is in Italian and has four buttons:

- **📢 Update**: you write an announcement in English and in Italian; after a preview it is sent to every group where the bot is present, in the language of each group.
- **🔁 Restart**: restarts the bot process (after confirmation; rounds in progress are lost). With `systemd` the service keeps running under the same unit.
- **⬇️ Pull**: runs `git pull --ff-only` and `pip install -r requirements.txt` in the bot's folder and shows the result, with a shortcut to restart.
- **📜 Log**: the last 50 log lines of the past hour.

## Setup

Requirements: Python 3.10+ and a bot token from [@BotFather](https://t.me/BotFather) (`/newbot`).

```bash
git clone https://github.com/kadovskji/Artichoke.git
cd Artichoke
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set the variables and start the bot:

```bash
export BOT_TOKEN=your_token     # Windows: set BOT_TOKEN=your_token
export ADMIN_ID=123456789       # your Telegram user ID (optional, enables /admin)
python artichoke.py
```

In PyCharm, set `BOT_TOKEN` and `ADMIN_ID` in the *Environment variables* of the Run Configuration, with `artichoke.py` as the script.

> ⚠️ Never commit the token. If it leaks, revoke it from BotFather (`/mybots` → your bot → *API Token* → *Revoke*).

Then:

1. Every player opens a private chat with the bot and presses `/start`.
2. Add the bot to the group and make it an **admin** with the *Delete messages* permission (needed for the spoiler filter).
3. Someone writes `/newgame`.

### Configuration

| Variable | Default | Meaning |
|---|---|---|
| `BOT_TOKEN` | required | Telegram bot token |
| `ADMIN_ID` | empty | Comma-separated Telegram user IDs allowed to use `/admin` |
| `DB_FILE` | `artichoke.db` | SQLite database path |
| `LOG_FILE` | `artichoke.log` | Log file (rotating, 1 MB × 3 files) |
| `CONTACT_URL` | this repository | Contact URL put in the User-Agent of Wikipedia/Wikidata requests (Wikimedia asks for it): set it to your own repository or website |
| `REQUIRE_TAG` | empty | Comma-separated commands handled in groups only as `/command@BotName`, useful if another bot uses the same command (e.g. `summary,stats`) |

### Always-on hosting

The bot uses long polling, so it needs no domain or open ports. On a Linux server, a `systemd` unit keeps it running (the `.env` file holds `BOT_TOKEN=...` and `ADMIN_ID=...`; protect it with `chmod 600 .env`):

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

To update the server by hand: `cd Artichoke && git pull && sudo systemctl restart artichoke` (or use `/admin` → Pull, Restart).

## Project structure

| File | Purpose |
|---|---|
| `artichoke.py` | Entry point: registers commands and handlers |
| `lobby.py` | `/newgame` (mode, teams, moves buttons), `/join`, `/ready`, `/wait`, `/stop` |
| `roles.py` | Role assignment, identity selection, start of play |
| `play.py` | Questions, attempts, Stargate points, Dr. A vote, `/hold`, `/summary`, round endings, spoiler filter |
| `settings.py` | `/settings` menu |
| `admin.py` | `/admin` panel (Update, Restart, Pull, Log) |
| `logs.py` | Log file setup and reader |
| `wiki.py` | Wikipedia / Wikidata validation and guess matching |
| `stats.py` | `/stats` and `/mystats` |
| `rules.py` | `/rules` |
| `db.py` | SQLite persistence |
| `game.py` | Game model, constants, timers and helpers |
| `i18n.py` | English and Italian strings |
| `check_identity.py` | Diagnostic tool: shows how a name is validated against Wikipedia and Wikidata |

## Troubleshooting

- **The bot says it couldn't verify an identity, or accepts anything** (even places): Wikipedia or Wikidata can't be reached from the server. Check the log with `sudo journalctl -u artichoke --no-pager | grep "check failed"`. A `403 Forbidden` usually means the User-Agent was refused: set `CONTACT_URL` to your own repository or website. Run `python check_identity.py "Roma"` to see exactly what the bot sees (the expected decision is REFUSE).
- **`Conflict: terminated by other getUpdates request`**: another copy of the bot is running with the same token. Stop it (PyCharm, another terminal or server).
- **`KeyError: 'BOT_TOKEN'`**: the token isn't set. Check the `.env` file (server) or the Run Configuration (PyCharm).
- **`/admin` does nothing**: `ADMIN_ID` is missing or wrong, or you are not writing in a private chat.
- **Pull fails with "not a git repository" or a merge error**: the bot's folder isn't a clone, or has local changes; fix it by hand over SSH.
- **`ModuleNotFoundError`**: a `.py` file is missing, or the dependencies aren't installed (`pip install -r requirements.txt`).

## Notes

- Rounds in progress live in memory: a restart cancels them (statistics are kept in the database). Rounds recorded with the old game modes are removed from the database at startup, because their rules were different.
- If Wikipedia or Wikidata can't be reached, an identity is accepted without validation so the game isn't blocked: the patient is warned in private and the reason is written in the log.
- The accepted Wikidata classes can be widened in `wiki.py` (`CHARACTER_CLASSES`, `CHARACTER_LABELS`).

## License

Released under the MIT License: see [LICENSE](LICENSE).
