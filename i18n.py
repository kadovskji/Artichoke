"""User-facing strings (English / Italian) and language helpers."""

DEFAULT_LANG = "en"

LANG_ALIASES = {
    "en": "en", "eng": "en", "english": "en",
    "it": "it", "ita": "it", "italiano": "it",
}


def parse_lang(arg: str | None) -> str | None:
    """Map a user-supplied language argument to 'en' / 'it' (None if unknown)."""
    return LANG_ALIASES.get((arg or "").strip().lower())


def T(lang: str, key: str, **kw) -> str:
    """Return the string `key` in `lang` (falls back to English)."""
    entry = STRINGS[key]
    text = entry.get(lang) or entry[DEFAULT_LANG]
    return text.format(**kw) if kw else text


STRINGS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------ lobby
    "start_private": {
        "en": "Great, I can now message you privately. Go back to the group and use /join (or /newgame to create a round).",
        "it": "Perfetto, ora posso scriverti in privato. Torna nel gruppo e usa /join (o /newgame per creare un round).",
    },
    "start_group": {
        "en": "To play, use /newgame in this group.",
        "it": "Per giocare usa /newgame in questo gruppo.",
    },
    "group_only": {
        "en": "Use this command in a group.",
        "it": "Usa questo comando in un gruppo.",
    },
    "game_exists": {
        "en": "There is already a round in this group.",
        "it": "C'è già un round in questo gruppo.",
    },
    "already_in_game": {
        "en": "You are already in an active round.",
        "it": "Sei già in un round attivo.",
    },
    "need_start": {
        "en": "{name}, please activate the bot in private first, then try again.",
        "it": "{name}, prima attiva il bot in privato, poi riprova.",
    },
    "btn_activate": {"en": "Activate Artichoke", "it": "Attiva Artichoke"},
    "mode_enigma": {"en": "K.H. Enigma", "it": "K.H. Enigma"},
    "mode_psyops": {"en": "PSY-OPS", "it": "PSY-OPS"},
    "btn_enigma": {"en": "🧪 K.H. Enigma", "it": "🧪 K.H. Enigma"},
    "btn_psyops": {"en": "🕵️ PSY-OPS", "it": "🕵️ PSY-OPS"},
    "pick_mode": {
        "en": (
            "🎲 {name}, choose a game mode:\n\n"
            "🧪 K.H. Enigma (2+ players): Patient K is an amnesiac who knows a secret identity "
            "but cannot say it. Everyone else is a researcher and must find it with yes/no "
            "questions. With 5+ players one researcher is secretly Dr. A, who knows the answer "
            "and tries to mislead.\n\n"
            "🕵️ PSY-OPS (4+ players): teams Artichoke and Bluebird race to identify their own "
            "patient within 10 minutes. With an odd number of players a KGB spy tries to "
            "steal both identities."
        ),
        "it": (
            "🎲 {name}, scegli la modalità di gioco:\n\n"
            "🧪 K.H. Enigma (2+ giocatori): il Paziente K è un amnesico che conosce un'identità "
            "segreta ma non può dirla. Tutti gli altri sono ricercatori e devono scoprirla con "
            "domande sì/no. Con 5+ giocatori un ricercatore è in segreto il Dr. A, che conosce "
            "la risposta e cerca di sviare le indagini.\n\n"
            "🕵️ PSY-OPS (4+ giocatori): le squadre Artichoke e Bluebird sono in gara per "
            "identificare il proprio paziente entro 10 minuti. Con un numero dispari di "
            "giocatori una spia del KGB cerca di rubare entrambe le identità."
        ),
    },
    "pick_moves": {
        "en": "{mode}: how many moves (questions + attempts) does each participant get?",
        "it": "{mode}: quante mosse (domande + tentativi) ha ogni partecipante?",
    },
    "config_expired": {
        "en": "⌛ No choice made: round cancelled.",
        "it": "⌛ Nessuna scelta: round annullato.",
    },
    "only_creator": {
        "en": "Only the player who created the round can choose.",
        "it": "Solo chi ha creato il round può scegliere.",
    },
    "stale": {
        "en": "This choice is no longer valid.",
        "it": "Scelta non più valida.",
    },
    "lobby_text": {
        "en": (
            "🎲 {creator} created a {mode} round with {moves} moves per player.\n"
            "Minimum players: {min}.\n"
            "/join to enter · /ready to start now · /wait <minutes> to extend sign-ups (max 10). "
            "Sign-ups close in 5 minutes."
        ),
        "it": (
            "🎲 {creator} ha creato un round {mode} con {moves} mosse a testa.\n"
            "Giocatori minimi: {min}.\n"
            "/join per entrare · /ready per partire subito · /wait <minuti> per prolungare le "
            "iscrizioni (max 10). Le iscrizioni chiudono tra 5 minuti."
        ),
    },
    "lobby_none": {
        "en": "There is no round waiting for players.",
        "it": "Nessun round in attesa di giocatori.",
    },
    "join_wait_config": {
        "en": "Wait until the creator has chosen the mode and the moves.",
        "it": "Aspetta che chi ha creato il round scelga modalità e mosse.",
    },
    "join_already": {"en": "You are already in.", "it": "Sei già dentro."},
    "join_other": {
        "en": "You are already in an active round elsewhere.",
        "it": "Hai già un round attivo altrove.",
    },
    "joined": {
        "en": "✅ {name} joined ({n} players).",
        "it": "✅ {name} si è unito ({n} giocatori).",
    },
    "only_players": {
        "en": "Only players who joined can use this command.",
        "it": "Solo i giocatori iscritti possono usare questo comando.",
    },
    "ready_need": {
        "en": "At least {min} players are needed ({n} joined so far).",
        "it": "Servono almeno {min} giocatori (finora {n}).",
    },
    "wait_usage": {
        "en": "Usage: /wait <minutes> (max 10, decimals allowed, e.g. /wait 3.5)",
        "it": "Uso: /wait <minuti> (max 10, anche decimali, es. /wait 3.5)",
    },
    "wait_max": {
        "en": "The maximum is 10 minutes per use.",
        "it": "Il massimo è 10 minuti per volta.",
    },
    "wait_ok": {
        "en": "⏳ Sign-ups extended by {added}. Time left: {left}.",
        "it": "⏳ Iscrizioni prolungate di {added}. Tempo rimasto: {left}.",
    },
    "not_enough": {
        "en": "Not enough players: round cancelled. (Tip: /wait extends the sign-ups.)",
        "it": "Giocatori insufficienti: round annullato. (Suggerimento: /wait prolunga le iscrizioni.)",
    },
    "stop_denied": {
        "en": "Only the creator or a group admin can stop the round.",
        "it": "Solo chi ha creato il round o un admin può fermarlo.",
    },
    "stopped": {"en": "🛑 Round cancelled.", "it": "🛑 Round annullato."},
    "setlan_admin": {
        "en": "Only group admins can change the language.",
        "it": "Solo gli admin del gruppo possono cambiare la lingua.",
    },
    "setlan_usage": {
        "en": "Usage: /setlan en  or  /setlan ita",
        "it": "Uso: /setlan en  oppure  /setlan ita",
    },
    "setlan_ok": {
        "en": "Language set to English. 🇬🇧",
        "it": "Lingua impostata su italiano. 🇮🇹",
    },

    # ------------------------------------------------------------ round setup
    "dm_failed": {
        "en": "I can't message {name} privately. Round cancelled: everyone must press /start in my private chat.",
        "it": "Non riesco a scrivere in privato a {name}. Round annullato: ognuno deve premere /start nella mia chat privata.",
    },
    "dm_warn": {
        "en": "⚠️ I couldn't message: {names}. They must press /start in my private chat.",
        "it": "⚠️ Non sono riuscito a scrivere a: {names}. Devono premere /start nella mia chat privata.",
    },
    "announce_enigma": {
        "en": (
            "🧪 K.H. Enigma starts with {n} players!\n"
            "🧠 Patient K: {k}\n"
            "🔬 Everyone else is a researcher: find K's secret identity with yes/no questions.{extra}"
        ),
        "it": (
            "🧪 K.H. Enigma parte con {n} giocatori!\n"
            "🧠 Paziente K: {k}\n"
            "🔬 Tutti gli altri sono ricercatori: scoprite l'identità segreta di K con domande sì/no.{extra}"
        ),
    },
    "announce_enigma_dra": {
        "en": "\n⚠️ One of the researchers is secretly Dr. A…",
        "it": "\n⚠️ Uno dei ricercatori è in segreto il Dr. A…",
    },
    "announce_psyops": {
        "en": (
            "🕵️ PSY-OPS starts with {n} players!\n"
            "🟢 Team Artichoke, patient K: {k}\n"
            "🔵 Team Bluebird, patient H: {h}\n"
            "The researchers' teams are secret: check your private chat for your role.{spy}"
        ),
        "it": (
            "🕵️ PSY-OPS parte con {n} giocatori!\n"
            "🟢 Squadra Artichoke, paziente K: {k}\n"
            "🔵 Squadra Bluebird, paziente H: {h}\n"
            "Le squadre dei ricercatori sono segrete: controlla la chat privata per scoprire il tuo ruolo.{spy}"
        ),
    },
    "announce_psyops_spy": {
        "en": "\n🕶 A KGB spy is hiding among you.",
        "it": "\n🕶 Una spia del KGB si nasconde tra voi.",
    },
    "dm_patient_enigma": {
        "en": (
            "You are Patient K 🧠. Send me the name of a famous person or character "
            "(real or fictional, with a Wikipedia page). You won't be able to change it. "
            "You will answer the researchers' questions publicly."
        ),
        "it": (
            "Sei il Paziente K 🧠. Scrivimi il nome di un personaggio famoso "
            "(reale o di fantasia, con una pagina su Wikipedia). Non potrai cambiarlo. "
            "Risponderai pubblicamente alle domande dei ricercatori."
        ),
    },
    "dm_researcher_enigma": {
        "en": (
            "You are a researcher 🔬. Patient K is {k}. Ask yes/no questions with /ask <text> "
            "and name the identity with /try <name>, in the group. You have {moves} moves. "
            "The first to find the identity wins together with K."
        ),
        "it": (
            "Sei un ricercatore 🔬. Il Paziente K è {k}. Fai domande sì/no con /ask <testo> "
            "e indica l'identità con /try <nome>, nel gruppo. Hai {moves} mosse. "
            "Il primo che scopre l'identità vince insieme a K."
        ),
    },
    "dm_dr_a": {
        "en": (
            "You are Dr. A 🧑‍🔬, the mad scientist behind Project Artichoke. "
            "You'll receive K's identity as soon as it is chosen. Nobody must find out you are involved: "
            "pretend to investigate, ask questions and try solutions to mislead the others "
            "(your /try can never win). You have {moves} moves."
        ),
        "it": (
            "Sei il Dr. A 🧑‍🔬, lo scienziato pazzo dietro il Progetto Artichoke. "
            "Riceverai l'identità di K appena sarà scelta. Nessuno deve scoprire che sei coinvolto: "
            "fingi di indagare, fai domande e tenta soluzioni per sviare gli altri "
            "(il tuo /try non può mai vincere). Hai {moves} mosse."
        ),
    },
    "dm_patient_psyops": {
        "en": (
            "You are patient {letter} 🧠 of team {team}. Your researchers: {mates}.\n"
            "Send me the name of a famous person or character (real or fictional, with a "
            "Wikipedia page). You won't be able to change it. You will answer only your own "
            "team's questions."
        ),
        "it": (
            "Sei il paziente {letter} 🧠 della squadra {team}. I tuoi ricercatori: {mates}.\n"
            "Scrivimi il nome di un personaggio famoso (reale o di fantasia, con una pagina su "
            "Wikipedia). Non potrai cambiarlo. Risponderai solo alle domande della tua squadra."
        ),
    },
    "dm_researcher_psyops": {
        "en": (
            "You are a researcher of team {team} 🔬. Your patient is {patient} ({letter}). "
            "Teammates: {mates}.\nUse /ask and /try in the group. You have {moves} moves. "
            "The first team to name its patient's identity wins (10 minutes in total)."
        ),
        "it": (
            "Sei un ricercatore della squadra {team} 🔬. Il tuo paziente è {patient} ({letter}). "
            "Compagni: {mates}.\nUsa /ask e /try nel gruppo. Hai {moves} mosse. "
            "La prima squadra che indica l'identità del proprio paziente vince (10 minuti in totale)."
        ),
    },
    "dm_spy": {
        "en": (
            "You are the KGB spy 🕶. You can't ask questions and you start with 0 attempts: "
            "you gain 1 attempt every time a researcher guesses wrong. Use /try <name> here, "
            "in private. You win if you name BOTH patients' identities before a team does."
        ),
        "it": (
            "Sei la spia del KGB 🕶. Non puoi fare domande e parti con 0 tentativi: "
            "ne guadagni 1 ogni volta che un ricercatore sbaglia. Usa /try <nome> qui, "
            "in privato. Vinci se indichi ENTRAMBE le identità dei pazienti prima di una squadra."
        ),
    },
    "none_label": {"en": "none", "it": "nessuno"},
    "identity_not_found": {
        "en": "I can't find a Wikipedia page with that name. Write it as it appears on Wikipedia (e.g. “Leonardo da Vinci”) and try again.",
        "it": "Non trovo una pagina Wikipedia con questo nome. Scrivilo come compare su Wikipedia (es. «Leonardo da Vinci») e riprova.",
    },
    "identity_not_character": {
        "en": "“{title}” has a Wikipedia page but is not a character (real person, fictional character, deity…). Pick another one.",
        "it": "«{title}» ha una pagina Wikipedia ma non è un personaggio (persona reale, personaggio di fantasia, divinità…). Scegline un altro.",
    },
    "identity_taken": {
        "en": "That identity can't be used. Pick a different one.",
        "it": "Questa identità non è utilizzabile. Scegline un'altra.",
    },
    "identity_saved": {
        "en": "Got it: {title}. The game can begin!",
        "it": "Ricevuto: {title}. Il gioco può iniziare!",
    },
    "identity_waiting": {
        "en": "Got it: {title}. Waiting for the other patient…",
        "it": "Ricevuto: {title}. Aspetto l'altro paziente…",
    },
    "choice_timeout": {
        "en": "⌛ Identity not chosen in time: round cancelled.",
        "it": "⌛ Identità non scelta in tempo: round annullato.",
    },
    "no_delete_perm": {
        "en": "⚠️ I'm not an admin with the “Delete messages” permission, so I can't remove spoilers.",
        "it": "⚠️ Non sono admin con il permesso «Elimina messaggi»: non potrò rimuovere gli spoiler.",
    },
    "dm_identity_dra": {
        "en": "🤫 K's identity is: {title}",
        "it": "🤫 L'identità di K è: {title}",
    },
    "play_start_enigma": {
        "en": (
            "🔬 The investigation begins! Each researcher has {moves} moves (questions and attempts).\n"
            "/ask <text> · /try <name> · /summary\n"
            "The round ends after 10 minutes without activity."
        ),
        "it": (
            "🔬 Le indagini hanno inizio! Ogni ricercatore ha {moves} mosse (domande e tentativi).\n"
            "/ask <testo> · /try <nome> · /summary\n"
            "Il round termina dopo 10 minuti di inattività."
        ),
    },
    "play_start_psyops": {
        "en": (
            "⏱ The race begins! You have 10 minutes. Each researcher has {moves} moves.\n"
            "/ask <text> · /try <name> · /summary"
        ),
        "it": (
            "⏱ La gara inizia! Avete 10 minuti. Ogni ricercatore ha {moves} mosse.\n"
            "/ask <testo> · /try <nome> · /summary"
        ),
    },

    # ------------------------------------------------------------ playing
    "round_not_playing": {
        "en": "The round is not in its playing phase right now.",
        "it": "Il round non è in fase di gioco in questo momento.",
    },
    "round_none": {
        "en": "There is no round in progress.",
        "it": "Nessun round in corso.",
    },
    "ask_forbidden": {
        "en": "Only researchers can do that.",
        "it": "Solo i ricercatori possono farlo.",
    },
    "ask_usage": {"en": "Usage: /ask <your question>", "it": "Uso: /ask <la tua domanda>"},
    "try_usage": {"en": "Usage: /try <character name>", "it": "Uso: /try <nome del personaggio>"},
    "ask_pending": {
        "en": "Wait for {patient} to answer the pending question.",
        "it": "Aspetta che {patient} risponda alla domanda in sospeso.",
    },
    "no_moves": {"en": "You have no moves left.", "it": "Non hai più mosse."},
    "question_msg": {
        "en": "❓ {who}{team} ({used}/{limit}): {text}\n\n{patient}, please answer:",
        "it": "❓ {who}{team} ({used}/{limit}): {text}\n\n{patient}, rispondi:",
    },
    "btn_yes": {"en": "✅ Yes", "it": "✅ Sì"},
    "btn_no": {"en": "❌ No", "it": "❌ No"},
    "btn_unknown": {"en": "🤷 Don't know", "it": "🤷 Non lo so"},
    "answered_msg": {
        "en": "❓ {who}{team}: {text}\n\n➡️ {answer}",
        "it": "❓ {who}{team}: {text}\n\n➡️ {answer}",
    },
    "res_y": {"en": "YES", "it": "SÌ"},
    "res_n": {"en": "NO", "it": "NO"},
    "res_u": {"en": "DON'T KNOW", "it": "NON LO SO"},
    "res_wrong": {"en": "❌", "it": "❌"},
    "question_closed": {
        "en": "❓ {who}: {text}\n\n⏹ Round over.",
        "it": "❓ {who}: {text}\n\n⏹ Round terminato.",
    },
    "answer_stale": {
        "en": "This question is no longer pending.",
        "it": "Questa domanda non è più in attesa.",
    },
    "answer_not_patient": {
        "en": "Only {patient} can answer this.",
        "it": "Solo {patient} può rispondere.",
    },
    "answer_timeout": {
        "en": "⌛ {patient} didn't answer in time: round cancelled.\nIdentity: {ids}",
        "it": "⌛ {patient} non ha risposto in tempo: round annullato.\nIdentità: {ids}",
    },
    "try_wrong": {
        "en": "❌ {who}: “{text}” is not the right identity. Moves left for {who}: {left}.",
        "it": "❌ {who}: «{text}» non è l'identità giusta. Mosse rimaste a {who}: {left}.",
    },
    "try_forbidden": {
        "en": "Only researchers can make attempts here.",
        "it": "Qui solo i ricercatori possono fare tentativi.",
    },
    "spy_use_private": {
        "en": "Use /try here, in our private chat, so nobody finds out who you are.",
        "it": "Usa /try qui, nella nostra chat privata, così nessuno scopre chi sei.",
    },
    "spy_no_tries": {
        "en": "You have no attempts available right now.",
        "it": "Al momento non hai tentativi disponibili.",
    },
    "spy_wrong": {
        "en": "❌ Not a match. Attempts left: {left}.",
        "it": "❌ Nessuna corrispondenza. Tentativi rimasti: {left}.",
    },
    "spy_partial": {
        "en": "✅ That's one of the two identities! ({found}/2). Attempts left: {left}.",
        "it": "✅ È una delle due identità! ({found}/2). Tentativi rimasti: {left}.",
    },
    "spy_gain": {
        "en": "➕ A researcher guessed wrong: you gained an attempt (now {n}).",
        "it": "➕ Un ricercatore ha sbagliato: guadagni un tentativo (ora {n}).",
    },
    "summary_head_enigma": {"en": "📋 Summary · K.H. Enigma", "it": "📋 Riepilogo · K.H. Enigma"},
    "summary_head_psyops": {"en": "📋 Summary · PSY-OPS", "it": "📋 Riepilogo · PSY-OPS"},
    "summary_empty": {"en": "No answers yet.", "it": "Ancora nessuna risposta."},
    "summary_pending": {
        "en": "⏳ Waiting for {patient}: {who}: {text}",
        "it": "⏳ In attesa di {patient}: {who}: {text}",
    },
    "summary_moves": {"en": "Moves left: {moves}", "it": "Mosse rimaste: {moves}"},
    "summary_team": {"en": "{icon} Team {team}", "it": "{icon} Squadra {team}"},
    "spoiler_removed": {
        "en": "🚫 {name}'s message was removed: spoiler.",
        "it": "🚫 Messaggio di {name} rimosso: era uno spoiler.",
    },

    # ------------------------------------------------------------ endings
    "reveal_dr_a": {"en": "\n🧑‍🔬 Dr. A was {name}.", "it": "\n🧑‍🔬 Il Dr. A era {name}."},
    "reveal_spy": {"en": "\n🕶 The KGB spy was {name}.", "it": "\n🕶 La spia del KGB era {name}."},
    "reveal_teams": {
        "en": "\n🟢 Artichoke: {a}\n🔵 Bluebird: {b}",
        "it": "\n🟢 Artichoke: {a}\n🔵 Bluebird: {b}",
    },
    "solved_enigma": {
        "en": "🎉 {guesser} found the identity: {title}!\n🏆 Winners: {k} (Patient K) and {guesser}.",
        "it": "🎉 {guesser} ha scoperto l'identità: {title}!\n🏆 Vincitori: {k} (Paziente K) e {guesser}.",
    },
    "solved_psyops": {
        "en": "🎉 Team {team} wins! {guesser} identified {title}.\n🏆 Winners: {winners}\nThe other identity was: {other}.",
        "it": "🎉 Vince la squadra {team}! {guesser} ha identificato {title}.\n🏆 Vincitori: {winners}\nL'altra identità era: {other}.",
    },
    "spy_win": {
        "en": "🕶 The KGB spy {spy} identified both identities ({a} and {b}) and wins!",
        "it": "🕶 La spia del KGB {spy} ha identificato entrambe le identità ({a} e {b}) e vince!",
    },
    "no_winner_enigma": {
        "en": "🏁 Nobody found the identity: {title}. Everyone loses.",
        "it": "🏁 Nessuno ha scoperto l'identità: {title}. Perdono tutti.",
    },
    "no_winner_psyops": {
        "en": "🏁 Round over: nobody identified their patient. The identities were {a} (Artichoke) and {b} (Bluebird). No winner.",
        "it": "🏁 Round terminato: nessuno ha identificato il proprio paziente. Le identità erano {a} (Artichoke) e {b} (Bluebird). Nessun vincitore.",
    },
    "vote_start": {
        "en": "🗳 Nobody found the identity, but one of you is Dr. A! Vote for who you suspect (secret ballot, no changes, not for yourself). You have {secs} seconds.",
        "it": "🗳 Nessuno ha scoperto l'identità, ma uno di voi è il Dr. A! Votate chi sospettate (voto segreto, non modificabile, non per se stessi). Avete {secs} secondi.",
    },
    "vote_status": {
        "en": "Votes: {n}/{total}\nMost voted so far: {leaders} ({top})",
        "it": "Voti: {n}/{total}\nIl più votato finora: {leaders} ({top})",
    },
    "vote_status_none": {"en": "Votes: 0/{total}", "it": "Voti: 0/{total}"},
    "vote_closed": {"en": "The vote is closed.", "it": "La votazione è chiusa."},
    "vote_not_player": {
        "en": "Only players of this round can vote.",
        "it": "Possono votare solo i giocatori di questo round.",
    },
    "vote_self": {"en": "You can't vote for yourself.", "it": "Non puoi votare te stesso."},
    "vote_already": {
        "en": "You have already voted: votes can't be changed.",
        "it": "Hai già votato: il voto non si può modificare.",
    },
    "vote_recorded": {"en": "Vote recorded.", "it": "Voto registrato."},
    "vote_caught": {
        "en": "🔎 Dr. A was {a} and has been caught! {k} (Patient K) and the researchers win.\nThe identity was: {title}.\nVotes: {tally}",
        "it": "🔎 Il Dr. A era {a} ed è stato scoperto! Vincono {k} (Paziente K) e i ricercatori.\nL'identità era: {title}.\nVoti: {tally}",
    },
    "vote_escaped": {
        "en": "😈 Dr. A was {a} and got away with it! Dr. A wins.\nThe identity was: {title}.\nVotes: {tally}",
        "it": "😈 Il Dr. A era {a} e l'ha fatta franca! Vince il Dr. A.\nL'identità era: {title}.\nVoti: {tally}",
    },

    # ------------------------------------------------------------ statistics
    "role_patient": {"en": "Patient", "it": "Paziente"},
    "role_researcher": {"en": "Researcher", "it": "Ricercatore"},
    "role_dr_a": {"en": "Dr. A", "it": "Dr. A"},
    "role_spy": {"en": "KGB spy", "it": "Spia KGB"},
    "stats_title": {"en": "📊 Group stats", "it": "📊 Statistiche del gruppo"},
    "stats_empty": {
        "en": "No completed rounds in this group yet.",
        "it": "Nessun round completato in questo gruppo.",
    },
    "stats_rounds": {
        "en": "Rounds played: {total} ({breakdown})",
        "it": "Round giocati: {total} ({breakdown})",
    },
    "stats_top_wins": {"en": "🏆 Most round wins", "it": "🏆 Più round vinti"},
    "stats_top_guess": {"en": "🔎 Most identities guessed", "it": "🔎 Più identità indovinate"},
    "stats_mode_best": {"en": "👑 Top winner per mode", "it": "👑 Più vittorie per modalità"},
    "stats_dra": {
        "en": "🧑‍🔬 Least caught Dr. A (min. {min} games): {name}, caught {c}/{n}",
        "it": "🧑‍🔬 Dr. A scoperto meno volte (min. {min} partite): {name}, scoperto {c}/{n}",
    },
    "stats_dra_none": {
        "en": "🧑‍🔬 Least caught Dr. A: not enough data yet (min. {min} games)",
        "it": "🧑‍🔬 Dr. A scoperto meno volte: dati insufficienti (min. {min} partite)",
    },
    "stats_fastest": {
        "en": "⚡ Fastest solve: {name}, {moves} moves",
        "it": "⚡ Soluzione più rapida: {name}, {moves} mosse",
    },
    "stats_spy": {"en": "🕶 KGB spy wins: {n}", "it": "🕶 Vittorie della spia KGB: {n}"},
    "my_title": {"en": "👤 Stats for {name} ({scope})", "it": "👤 Statistiche di {name} ({scope})"},
    "scope_group": {"en": "this group", "it": "questo gruppo"},
    "scope_all": {"en": "all groups", "it": "tutti i gruppi"},
    "my_empty": {"en": "No completed rounds yet.", "it": "Ancora nessun round completato."},
    "my_total": {
        "en": "Rounds: {played} · wins: {wins} ({pct}%)",
        "it": "Round: {played} · vittorie: {wins} ({pct}%)",
    },
    "my_modes": {
        "en": "By mode (wins/played): {text}",
        "it": "Per modalità (vittorie/giocati): {text}",
    },
    "my_roles": {
        "en": "By role (wins/played): {text}",
        "it": "Per ruolo (vittorie/giocati): {text}",
    },
    "my_favorite": {
        "en": "Most played role: {role} ({n})",
        "it": "Ruolo più giocato: {role} ({n})",
    },
    "my_guessed": {"en": "Identities guessed: {n}", "it": "Identità indovinate: {n}"},
    "my_fastest": {"en": "Fastest solve: {moves} moves", "it": "Soluzione più rapida: {moves} mosse"},
    "my_caught": {
        "en": "Caught as Dr. A: {c} of {n}",
        "it": "Scoperto come Dr. A: {c} su {n}",
    },

    # ------------------------------------------------------------ /rules
    "rules_sent": {
        "en": "📩 {name}, I sent you the rules in private.",
        "it": "📩 {name}, ti ho inviato le regole in privato.",
    },
    "rules_general": {
        "en": (
            "📖 Artichoke: how it works\n\n"
            "Guess a famous identity (a real or fictional person, a deity…) by asking yes/no questions.\n\n"
            "Modes: K.H. Enigma (2+ players) and PSY-OPS (4+ players).\n\n"
            "Round flow: /newgame (the creator picks the mode and the moves per player) → /join → "
            "the round starts when the 5 minutes of sign-ups are over, or earlier with /ready "
            "(any joined player, if there are enough players). /wait <minutes> extends the sign-ups "
            "(max 10 per use, decimals allowed). Everyone must have pressed /start in my private chat.\n\n"
            "Commands: /ask <text> · /try <name> · /summary · /stats · /mystats · /rules · /stop · /setlan en|ita"
        ),
        "it": (
            "📖 Artichoke: come funziona\n\n"
            "Indovina un'identità famosa (una persona reale o di fantasia, una divinità…) facendo domande sì/no.\n\n"
            "Modalità: K.H. Enigma (2+ giocatori) e PSY-OPS (4+ giocatori).\n\n"
            "Svolgimento: /newgame (chi crea il round sceglie modalità e mosse a testa) → /join → "
            "il round parte allo scadere dei 5 minuti di iscrizioni, o prima con /ready "
            "(qualsiasi giocatore iscritto, se ci sono abbastanza giocatori). /wait <minuti> prolunga le "
            "iscrizioni (max 10 per volta, anche decimali). Tutti devono aver premuto /start nella mia chat privata.\n\n"
            "Comandi: /ask <testo> · /try <nome> · /summary · /stats · /mystats · /rules · /stop · /setlan en|ita"
        ),
    },
    "rules_enigma": {
        "en": (
            "🧪 K.H. Enigma: rules\n\n"
            "Players: 2 or more. Roles are drawn at random when the round starts:\n"
            "• 🧠 Patient K (1 player): an amnesiac nicknamed Hauser, unable to communicate after a secret "
            "experiment. K secretly picks a famous identity (a real or fictional person, a deity… with a "
            "Wikipedia page) and answers the researchers' questions in public.\n"
            "• 🔬 Researchers (everyone else): they try to work out K's identity.\n"
            "• 🧑‍🔬 Dr. A (only with 5+ players): the mad scientist behind Project Artichoke. Knows the identity "
            "but must stay undercover: pretends to investigate, asks questions and makes attempts to mislead "
            "the others (his attempts can never win).\n\n"
            "How to play: every researcher (and Dr. A) has the same number of moves, questions and attempts "
            "together, set by the creator. /ask <text> asks a yes/no question; K answers Yes, No or Don't know "
            "(Don't know does not cost a move). One question at a time. /try <name> makes an attempt; a wrong "
            "attempt costs a move. /summary lists all answers so far.\n\n"
            "The round ends when a researcher guesses, when all researchers are out of moves, or after "
            "10 minutes without activity.\n\n"
            "How to win:\n"
            "🧠 Patient K: wins together with the first researcher who guesses the identity, or together with "
            "all the researchers if Dr. A is unmasked.\n"
            "🔬 Researcher: wins by being the first to guess (together with K); the other researchers lose. "
            "If nobody guesses and Dr. A is unmasked, all researchers win with K.\n"
            "🧑‍🔬 Dr. A: wins if nobody guesses and he is not unmasked. Loses if somebody guesses or he is unmasked.\n"
            "Without Dr. A (fewer than 5 players): if nobody guesses, everybody loses.\n\n"
            "Dr. A vote: if nobody guesses, everyone has 60 seconds to vote for who they suspect (secret ballot, "
            "no changes, no votes for yourself). After each vote the bot shows who is currently leading. "
            "Dr. A is unmasked only if he is strictly the most voted: ties don't count."
        ),
        "it": (
            "🧪 K.H. Enigma: regole\n\n"
            "Giocatori: 2 o più. I ruoli sono estratti a caso a inizio round:\n"
            "• 🧠 Paziente K (1 giocatore): un amnesico soprannominato Hauser, incapace di comunicare dopo un "
            "esperimento segreto. K sceglie in segreto un'identità famosa (una persona reale o di fantasia, "
            "una divinità… con una pagina su Wikipedia) e risponde pubblicamente alle domande dei ricercatori.\n"
            "• 🔬 Ricercatori (tutti gli altri): cercano di scoprire l'identità di K.\n"
            "• 🧑‍🔬 Dr. A (solo con 5+ giocatori): lo scienziato pazzo dietro il Progetto Artichoke. Conosce "
            "l'identità ma deve restare nell'ombra: finge di indagare, fa domande e tentativi per sviare gli "
            "altri (i suoi tentativi non possono mai vincere).\n\n"
            "Come si gioca: ogni ricercatore (e il Dr. A) ha lo stesso numero di mosse, domande e tentativi "
            "insieme, scelto da chi crea il round. /ask <testo> fa una domanda sì/no; K risponde Sì, No o Non lo "
            "so (Non lo so non costa una mossa). Una domanda alla volta. /try <nome> fa un tentativo; un tentativo "
            "sbagliato costa una mossa. /summary elenca tutte le risposte finora.\n\n"
            "Il round finisce quando un ricercatore indovina, quando tutti i ricercatori hanno finito le mosse, "
            "o dopo 10 minuti di inattività.\n\n"
            "Come si vince:\n"
            "🧠 Paziente K: vince insieme al primo ricercatore che indovina l'identità, o insieme a tutti i "
            "ricercatori se il Dr. A viene smascherato.\n"
            "🔬 Ricercatore: vince chi indovina per primo (insieme a K); gli altri ricercatori perdono. "
            "Se nessuno indovina e il Dr. A viene smascherato, tutti i ricercatori vincono con K.\n"
            "🧑‍🔬 Dr. A: vince se nessuno indovina e non viene smascherato. Perde se qualcuno indovina o viene smascherato.\n"
            "Senza Dr. A (meno di 5 giocatori): se nessuno indovina, perdono tutti.\n\n"
            "Voto sul Dr. A: se nessuno indovina, tutti hanno 60 secondi per votare chi sospettano (voto segreto, "
            "non modificabile, non per se stessi). Dopo ogni voto il bot mostra chi è in testa. "
            "Il Dr. A è smascherato solo se è il più votato in assoluto: i pareggi non contano."
        ),
    },
    "rules_psyops": {
        "en": (
            "🕵️ PSY-OPS: rules\n\n"
            "Players: 4 or more. Two teams, Artichoke 🟢 and Bluebird 🔵, race to identify the identity of "
            "their own patient.\n\n"
            "Setup: two patients are drawn (K for Artichoke, H for Bluebird) and announced in the group. The "
            "other players are split evenly into the two teams of researchers; the teams are secret (you learn "
            "your role in private). With an odd number of players one of them is a KGB spy and belongs to no "
            "team. Each patient privately picks a different famous identity (a real or fictional person, a "
            "deity… with a Wikipedia page).\n\n"
            "How to play: the round lasts 10 minutes in total. Every researcher has the same number of moves "
            "(questions and attempts together), set by the creator. /ask <text> sends a yes/no question to YOUR "
            "patient, the only one who can answer (Yes, No or Don't know; Don't know does not cost a move). "
            "Each team has one pending question at a time. Both teams play at once in the group and can see each "
            "other's questions. /try <name> makes an attempt at your patient's identity; a wrong attempt costs a "
            "move. /summary lists questions and answers, grouped by team.\n\n"
            "How to win:\n"
            "🧠🔬 Patient and researchers: the first team to name its patient's identity wins. If time or "
            "moves run out, nobody wins.\n"
            "🕶 KGB spy: can't ask questions and starts with 0 attempts, gaining one every time a researcher "
            "guesses wrong. Attempts are made with /try in my private chat, so the spy stays hidden; matches are "
            "confirmed in private only. The spy wins by naming BOTH identities before any team solves its own, "
            "and loses if a team wins first."
        ),
        "it": (
            "🕵️ PSY-OPS: regole\n\n"
            "Giocatori: 4 o più. Due squadre, Artichoke 🟢 e Bluebird 🔵, sono in gara per identificare "
            "l'identità del proprio paziente.\n\n"
            "Preparazione: si estraggono due pazienti (K per Artichoke, H per Bluebird), annunciati nel gruppo. "
            "Gli altri giocatori sono divisi equamente nelle due squadre di ricercatori; le squadre sono segrete "
            "(scopri il tuo ruolo in privato). Con un numero dispari di giocatori uno è una spia del KGB e non "
            "appartiene a nessuna squadra. Ogni paziente sceglie in privato un'identità famosa diversa (una "
            "persona reale o di fantasia, una divinità… con una pagina su Wikipedia).\n\n"
            "Come si gioca: il round dura 10 minuti in tutto. Ogni ricercatore ha lo stesso numero di mosse "
            "(domande e tentativi insieme), scelto da chi crea il round. /ask <testo> invia una domanda sì/no al "
            "TUO paziente, l'unico che può rispondere (Sì, No o Non lo so; Non lo so non costa una mossa). "
            "Ogni squadra ha una domanda in sospeso alla volta. Le due squadre giocano insieme nel gruppo e "
            "vedono le domande dell'altra. /try <nome> fa un tentativo sull'identità del tuo paziente; un "
            "tentativo sbagliato costa una mossa. /summary elenca domande e risposte, divise per squadra.\n\n"
            "Come si vince:\n"
            "🧠🔬 Paziente e ricercatori: vince la prima squadra che indica l'identità del proprio paziente. "
            "Se finiscono il tempo o le mosse, non vince nessuno.\n"
            "🕶 Spia del KGB: non può fare domande e parte con 0 tentativi, ne guadagna uno ogni volta che un "
            "ricercatore sbaglia. I tentativi si fanno con /try nella mia chat privata, così la spia resta "
            "nascosta; le corrispondenze sono confermate solo in privato. La spia vince se indica ENTRAMBE le "
            "identità prima che una squadra risolva la propria, e perde se una squadra vince per prima."
        ),
    },
}
