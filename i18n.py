"""User-facing strings (English / Italian) and language helpers."""

DEFAULT_LANG = "en"
LANGUAGES = ("en", "it")


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
    "start_group": {"en": "To play, use /newgame in this group.", "it": "Per giocare usa /newgame in questo gruppo."},
    "group_only": {"en": "Use this command in a group.", "it": "Usa questo comando in un gruppo."},
    "game_exists": {"en": "There is already a round in this group.", "it": "C'è già un round in questo gruppo."},
    "already_in_game": {"en": "You are already in an active round.", "it": "Sei già in un round attivo."},
    "need_start": {
        "en": "{name}, please activate the bot in private first, then try again.",
        "it": "{name}, prima attiva il bot in privato, poi riprova.",
    },
    "btn_activate": {"en": "Activate Artichoke", "it": "Attiva Artichoke"},
    "mode_artichoke": {"en": "Artichoke", "it": "Artichoke"},
    "mode_stargate": {"en": "Stargate", "it": "Stargate"},
    "btn_artichoke": {"en": "🧪 Artichoke", "it": "🧪 Artichoke"},
    "btn_stargate": {"en": "🕵️ Stargate", "it": "🕵️ Stargate"},
    "pick_mode": {
        "en": (
            "🎲 {name}, choose a game mode:\n\n"
            "🧪 Artichoke (2+ players): Patient K is an amnesiac who knows a secret identity but cannot say it. "
            "The researchers must find it with yes/no questions. With 5+ players a mad scientist, Dr. A, may be "
            "hiding among them.\n\n"
            "🕵️ Stargate (3+ players): teams of researchers race to identify K's identities. The first team with "
            "2 points wins. A CIA agent, Skip, may secretly join the hunt."
        ),
        "it": (
            "🎲 {name}, scegli la modalità di gioco:\n\n"
            "🧪 Artichoke (2+ giocatori): il Paziente K è un amnesico che conosce un'identità segreta ma non può "
            "dirla. I ricercatori devono scoprirla con domande sì/no. Con 5+ giocatori uno scienziato pazzo, il "
            "Dr. A, può nascondersi tra loro.\n\n"
            "🕵️ Stargate (3+ giocatori): squadre di ricercatori in gara per scoprire le identità di K. Vince la "
            "prima squadra che ottiene 2 punti. Un agente della CIA, Skip, può unirsi in segreto alla caccia."
        ),
    },
    "pick_teams": {
        "en": "🕵️ Stargate: how many teams? Minimum players: 2 teams → 3, 3 teams → 7, 4 teams → 9.",
        "it": "🕵️ Stargate: quante squadre? Giocatori minimi: 2 squadre → 3, 3 squadre → 7, 4 squadre → 9.",
    },
    "pick_moves": {
        "en": "{mode}: how many moves (questions + attempts) does each person get?",
        "it": "{mode}: quante mosse (domande + tentativi) ha ogni persona?",
    },
    "config_expired": {"en": "⌛ No choice made: round cancelled.", "it": "⌛ Nessuna scelta: round annullato."},
    "only_creator": {
        "en": "Only the player who created the round can choose.",
        "it": "Solo chi ha creato il round può scegliere.",
    },
    "stale": {"en": "This choice is no longer valid.", "it": "Scelta non più valida."},
    "moves_auto": {"en": "automatic", "it": "automatiche"},
    "teams_n": {"en": "{n} teams", "it": "{n} squadre"},
    "lobby_text": {
        "en": (
            "🎲 {creator} created a round: {mode}.\n"
            "Moves per person: {moves}. Minimum players: {min}.\n"
            "/join to enter · /ready to start now · /wait <minutes> to extend sign-ups (max 10). "
            "Sign-ups close in 5 minutes."
        ),
        "it": (
            "🎲 {creator} ha creato un round: {mode}.\n"
            "Mosse a testa: {moves}. Giocatori minimi: {min}.\n"
            "/join per entrare · /ready per partire subito · /wait <minuti> per prolungare le iscrizioni "
            "(max 10). Le iscrizioni chiudono tra 5 minuti."
        ),
    },
    "lobby_none": {"en": "There is no round waiting for players.", "it": "Nessun round in attesa di giocatori."},
    "join_wait_config": {
        "en": "Wait until the creator has finished choosing the options.",
        "it": "Aspetta che chi ha creato il round finisca di scegliere le opzioni.",
    },
    "join_already": {"en": "You are already in.", "it": "Sei già dentro."},
    "join_other": {"en": "You are already in an active round elsewhere.", "it": "Hai già un round attivo altrove."},
    "joined": {"en": "✅ {name} joined ({n} players).", "it": "✅ {name} si è unito ({n} giocatori)."},
    "only_players": {
        "en": "Only players who joined can use this command.",
        "it": "Solo i giocatori iscritti possono usare questo comando.",
    },
    "ready_need": {
        "en": "At least {min} players are needed ({n} joined so far).",
        "it": "Servono almeno {min} giocatori (finora {n}).",
    },
    "ready_layout": {
        "en": "With {teams} teams the teams must be even: {n} players don't work. Valid numbers: {list}.",
        "it": "Con {teams} squadre le squadre devono essere uguali: {n} giocatori non vanno bene. Numeri validi: {list}.",
    },
    "wait_usage": {
        "en": "Usage: /wait <minutes> (max 10, decimals allowed, e.g. /wait 3.5)",
        "it": "Uso: /wait <minuti> (max 10, anche decimali, es. /wait 3.5)",
    },
    "wait_max": {"en": "The maximum is 10 minutes per use.", "it": "Il massimo è 10 minuti per volta."},
    "wait_ok": {
        "en": "⏳ Sign-ups extended by {added}. Time left: {left}.",
        "it": "⏳ Iscrizioni prolungate di {added}. Tempo rimasto: {left}.",
    },
    "not_enough": {
        "en": "Not enough players: round cancelled. (Tip: /wait extends the sign-ups.)",
        "it": "Giocatori insufficienti: round annullato. (Suggerimento: /wait prolunga le iscrizioni.)",
    },
    "bad_layout": {
        "en": "The players can't be split into even teams: round cancelled. Valid numbers of players: {list}.",
        "it": "I giocatori non si dividono in squadre uguali: round annullato. Numeri di giocatori validi: {list}.",
    },
    "stop_denied": {
        "en": "Only the creator or a group admin can stop the round.",
        "it": "Solo chi ha creato il round o un admin può fermarlo.",
    },
    "stopped": {"en": "🛑 Round cancelled.", "it": "🛑 Round annullato."},

    # ------------------------------------------------------------ settings
    "settings_title": {"en": "⚙️ Group settings", "it": "⚙️ Impostazioni del gruppo"},
    "settings_admin": {
        "en": "Only group admins can change the settings.",
        "it": "Solo gli admin del gruppo possono cambiare le impostazioni.",
    },
    "settings_saved": {"en": "Saved.", "it": "Salvato."},
    "btn_back": {"en": "⬅️ Back", "it": "⬅️ Indietro"},
    "set_lang": {"en": "🌐 Language", "it": "🌐 Lingua"},
    "set_breaks": {"en": "⏸ Allow breaks", "it": "⏸ Consenti pause"},
    "set_attempts": {"en": "🎯 Attempts", "it": "🎯 Tentativi"},
    "set_dra": {"en": "🧑‍🔬 Dr. A", "it": "🧑‍🔬 Dr. A"},
    "set_lang_en": {"en": "English", "it": "English"},
    "set_lang_it": {"en": "Italiano", "it": "Italiano"},
    "set_breaks_on": {"en": "Everyone", "it": "Tutti"},
    "set_breaks_admins": {"en": "Admins only", "it": "Solo admin"},
    "set_breaks_off": {"en": "Off", "it": "Disattivate"},
    "set_attempts_auto": {"en": "Automatic", "it": "Automatici"},
    "set_attempts_creator": {"en": "Chosen by the creator", "it": "Scelti da chi crea il round"},
    "set_dra_random": {"en": "30% chance of absence", "it": "30% di non comparire"},
    "set_dra_always": {"en": "Always present (5+ players)", "it": "Sempre presente (5+ giocatori)"},
    "settings_sub_lang": {"en": "Choose the language of the group.", "it": "Scegli la lingua del gruppo."},
    "settings_sub_breaks": {
        "en": "Who can use /hold to pause a round.",
        "it": "Chi può usare /hold per mettere in pausa un round.",
    },
    "settings_sub_attempts": {
        "en": "Moves per person: computed from the number of players, or chosen (5/7/10/15/20) by the round creator.",
        "it": "Mosse a testa: calcolate in base ai giocatori, oppure scelte (5/7/10/15/20) da chi crea il round.",
    },
    "settings_sub_dra": {
        "en": "In Artichoke rounds with 5+ players: Dr. A is always there, or has a 30% chance of being absent.",
        "it": "Nei round Artichoke con 5+ giocatori: il Dr. A c'è sempre, oppure ha il 30% di probabilità di non esserci.",
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
    "announce_artichoke": {
        "en": (
            "🧪 Artichoke starts with {n} players!\n"
            "🧠 Patient K: {k}\n"
            "🔬 Everyone else is a researcher: find K's secret identity with yes/no questions.\n"
            "⏱ Moves per person: {moves}{extra}"
        ),
        "it": (
            "🧪 Artichoke parte con {n} giocatori!\n"
            "🧠 Paziente K: {k}\n"
            "🔬 Tutti gli altri sono ricercatori: scoprite l'identità segreta di K con domande sì/no.\n"
            "⏱ Mosse a testa: {moves}{extra}"
        ),
    },
    "announce_artichoke_vote": {
        "en": "\n⚠️ Someone may be hiding among the researchers… if nobody guesses, you will vote.",
        "it": "\n⚠️ Qualcuno potrebbe nascondersi tra i ricercatori… se nessuno indovina, voterete.",
    },
    "announce_stargate": {
        "en": (
            "🕵️ Stargate starts with {n} players!\n"
            "🧠 Patient K: {k}\n"
            "🏷 Teams in play: {teams}\n"
            "Your team is secret: check your private chat. The first team to guess 2 identities wins.\n"
            "⏱ Moves per person (for each identity): {moves}"
        ),
        "it": (
            "🕵️ Stargate parte con {n} giocatori!\n"
            "🧠 Paziente K: {k}\n"
            "🏷 Squadre in gioco: {teams}\n"
            "La tua squadra è segreta: controlla la chat privata. Vince la prima squadra che indovina 2 identità.\n"
            "⏱ Mosse a testa (per ogni identità): {moves}"
        ),
    },
    "no_delete_perm": {
        "en": "⚠️ I'm not an admin with the “Delete messages” permission, so I can't remove spoilers.",
        "it": "⚠️ Non sono admin con il permesso «Elimina messaggi»: non potrò rimuovere gli spoiler.",
    },
    "dm_patient_a": {
        "en": (
            "You are Patient K 🧠. Send me the name of a famous person or character (real or fictional, with a "
            "Wikipedia page). You won't be able to change it. You will answer the researchers' questions "
            "publicly, within 5 minutes each."
        ),
        "it": (
            "Sei il Paziente K 🧠. Scrivimi il nome di un personaggio famoso (reale o di fantasia, con una pagina "
            "su Wikipedia). Non potrai cambiarlo. Risponderai pubblicamente alle domande dei ricercatori, "
            "entro 5 minuti ciascuna."
        ),
    },
    "dm_patient_s": {
        "en": (
            "You are Patient K 🧠. Send me the name of a famous person or character (real or fictional, with a "
            "Wikipedia page). You will answer the questions of ALL the teams, within 5 minutes each, and you "
            "will have to pick a new identity every time a team guesses one."
        ),
        "it": (
            "Sei il Paziente K 🧠. Scrivimi il nome di un personaggio famoso (reale o di fantasia, con una pagina "
            "su Wikipedia). Risponderai alle domande di TUTTE le squadre, entro 5 minuti ciascuna, e dovrai "
            "scegliere una nuova identità ogni volta che una squadra ne indovina una."
        ),
    },
    "dm_researcher_a": {
        "en": (
            "You are a researcher 🔬. Patient K is {k}. Ask yes/no questions with /ask <text> and name the "
            "identity with /try <name>, in the group. You have {moves} moves. The first to find the identity "
            "wins together with K."
        ),
        "it": (
            "Sei un ricercatore 🔬. Il Paziente K è {k}. Fai domande sì/no con /ask <testo> e indica l'identità "
            "con /try <nome>, nel gruppo. Hai {moves} mosse. Il primo che scopre l'identità vince insieme a K."
        ),
    },
    "dm_researcher_s": {
        "en": (
            "You are a researcher 🔬 of team {team}. Teams in play: {teams}. Teammates are secret, even to you. "
            "Patient K is {k}. Use /ask and /try in the group: you have {moves} moves for each identity. "
            "The first team to guess 2 identities wins."
        ),
        "it": (
            "Sei un ricercatore 🔬 della squadra {team}. Squadre in gioco: {teams}. I compagni sono segreti, "
            "anche per te. Il Paziente K è {k}. Usa /ask e /try nel gruppo: hai {moves} mosse per ogni identità. "
            "Vince la prima squadra che indovina 2 identità."
        ),
    },
    "dm_dr_a": {
        "en": (
            "You are Dr. A 🧑‍🔬, the mad scientist behind Project Artichoke. You'll receive K's identity as soon as "
            "it is chosen. Nobody must find out you are involved: pretend to investigate, ask questions and try "
            "solutions to mislead the others (your /try can never win). You have {moves} moves."
        ),
        "it": (
            "Sei il Dr. A 🧑‍🔬, lo scienziato pazzo dietro il Progetto Artichoke. Riceverai l'identità di K appena "
            "sarà scelta. Nessuno deve scoprire che sei coinvolto: fingi di indagare, fai domande e tenta "
            "soluzioni per sviare gli altri (il tuo /try non può mai vincere). Hai {moves} mosse."
        ),
    },
    "dm_skip": {
        "en": (
            "You are Agent Skip 🕶, a CIA subject in a remote-viewing study. You can ask questions ({moves} per "
            "identity) but you start with 0 attempts: you gain one (up to 5 at a time) every time a researcher "
            "guesses wrong. Patient K is {k}. You win ALONE if you guess an identity before the round ends. "
            "Use /try <name> in the group once you have attempts."
        ),
        "it": (
            "Sei l'agente Skip 🕶, soggetto CIA di uno studio sul remote viewing. Puoi fare domande ({moves} per "
            "identità) ma inizi con 0 tentativi: ne guadagni uno (fino a 5 alla volta) ogni volta che un "
            "ricercatore sbaglia. Il Paziente K è {k}. Vinci DA SOLO se indovini un'identità prima della fine del "
            "round. Usa /try <nome> nel gruppo quando hai tentativi."
        ),
    },
    "identity_not_found": {
        "en": "I can't find a Wikipedia page with that name. Write it as it appears on Wikipedia (e.g. “Leonardo da Vinci”) and try again.",
        "it": "Non trovo una pagina Wikipedia con questo nome. Scrivilo come compare su Wikipedia (es. «Leonardo da Vinci») e riprova.",
    },
    "identity_not_character": {
        "en": "“{title}” has a Wikipedia page but is not a character (real person, fictional character, deity…). Pick another one.",
        "it": "«{title}» ha una pagina Wikipedia ma non è un personaggio (persona reale, personaggio di fantasia, divinità…). Scegline un altro.",
    },
    "identity_taken": {
        "en": "That identity was already used in this round. Pick a different one.",
        "it": "Questa identità è già stata usata in questo round. Scegline un'altra.",
    },
    "identity_saved": {
        "en": "Got it: {title}. The game can begin!",
        "it": "Ricevuto: {title}. Il gioco può iniziare!",
    },
    "identity_unverified": {
        "en": "⚠️ I couldn't verify this identity on Wikipedia/Wikidata, so I accepted it as is.",
        "it": "⚠️ Non sono riuscito a verificare questa identità su Wikipedia/Wikidata, quindi l'ho accettata così com'è.",
    },
    "choice_timeout": {
        "en": "⌛ Identity not chosen in time: round cancelled.",
        "it": "⌛ Identità non scelta in tempo: round annullato.",
    },
    "dm_identity_dra": {"en": "🤫 K's identity is: {title}", "it": "🤫 L'identità di K è: {title}"},
    "identity_next_go": {
        "en": "▶️ Identity {n} is set! Moves are reset. Score: {score}",
        "it": "▶️ Identità {n} scelta! Le mosse sono azzerate. Punteggio: {score}",
    },
    "play_start_artichoke": {
        "en": (
            "🔬 The investigation begins! Each researcher has {moves} moves (questions and attempts).\n"
            "/ask <text> · /try <name> · /summary · /hold\n"
            "The round ends after 10 minutes without activity."
        ),
        "it": (
            "🔬 Le indagini hanno inizio! Ogni ricercatore ha {moves} mosse (domande e tentativi).\n"
            "/ask <testo> · /try <nome> · /summary · /hold\n"
            "Il round termina dopo 10 minuti di inattività."
        ),
    },
    "play_start_stargate": {
        "en": (
            "🕵️ The hunt begins! Each researcher has {moves} moves for each identity. The first team to guess "
            "2 identities wins.\n/ask <text> · /try <name> · /summary · /hold\n"
            "The round ends after 10 minutes without activity."
        ),
        "it": (
            "🕵️ La caccia inizia! Ogni ricercatore ha {moves} mosse per ogni identità. Vince la prima squadra che "
            "indovina 2 identità.\n/ask <testo> · /try <nome> · /summary · /hold\n"
            "Il round termina dopo 10 minuti di inattività."
        ),
    },

    # ------------------------------------------------------------ playing
    "round_not_playing": {
        "en": "The round is not in its playing phase right now.",
        "it": "Il round non è in fase di gioco in questo momento.",
    },
    "round_none": {"en": "There is no round in progress.", "it": "Nessun round in corso."},
    "game_paused": {
        "en": "⏸ The round is paused. /ready to resume.",
        "it": "⏸ Il round è in pausa. /ready per riprendere.",
    },
    "ask_forbidden": {"en": "Only researchers can do that.", "it": "Solo i ricercatori possono farlo."},
    "ask_usage": {"en": "Usage: /ask <your question>", "it": "Uso: /ask <la tua domanda>"},
    "try_usage": {"en": "Usage: /try <character name>", "it": "Uso: /try <nome del personaggio>"},
    "ask_pending": {
        "en": "Wait for {patient} to answer the pending question.",
        "it": "Aspetta che {patient} risponda alla domanda in sospeso.",
    },
    "no_moves": {"en": "You have no moves left.", "it": "Non hai più mosse."},
    "question_msg": {
        "en": "❓ {who} ({used}/{limit}): {text}\n\n{patient}, please answer:",
        "it": "❓ {who} ({used}/{limit}): {text}\n\n{patient}, rispondi:",
    },
    "btn_yes": {"en": "✅ Yes", "it": "✅ Sì"},
    "btn_no": {"en": "❌ No", "it": "❌ No"},
    "btn_unknown": {"en": "🤷 Don't know", "it": "🤷 Non lo so"},
    "answered_msg": {"en": "❓ {who}: {text}\n\n➡️ {answer}", "it": "❓ {who}: {text}\n\n➡️ {answer}"},
    "res_y": {"en": "YES", "it": "SÌ"},
    "res_n": {"en": "NO", "it": "NO"},
    "res_u": {"en": "DON'T KNOW", "it": "NON LO SO"},
    "res_wrong": {"en": "❌", "it": "❌"},
    "question_closed": {
        "en": "❓ {who}: {text}\n\n⏹ Round over.",
        "it": "❓ {who}: {text}\n\n⏹ Round terminato.",
    },
    "answer_stale": {"en": "This question is no longer pending.", "it": "Questa domanda non è più in attesa."},
    "answer_not_patient": {"en": "Only {patient} can answer this.", "it": "Solo {patient} può rispondere."},
    "answer_timeout": {
        "en": "⌛ {patient} didn't answer in time: round cancelled.\nIdentities: {ids}",
        "it": "⌛ {patient} non ha risposto in tempo: round annullato.\nIdentità: {ids}",
    },
    "try_wrong": {
        "en": "❌ {who}: “{text}” is not the right identity. Moves left for {who}: {left}.",
        "it": "❌ {who}: «{text}» non è l'identità giusta. Mosse rimaste a {who}: {left}.",
    },
    "try_wrong_skip": {
        "en": "❌ “{text}” is not the right identity.",
        "it": "❌ «{text}» non è l'identità giusta.",
    },
    "try_forbidden": {
        "en": "Only researchers can make attempts here.",
        "it": "Qui solo i ricercatori possono fare tentativi.",
    },
    "skip_no_tries": {
        "en": "You have no attempts right now: you gain one when a researcher guesses wrong.",
        "it": "Al momento non hai tentativi: ne guadagni uno quando un ricercatore sbaglia.",
    },
    "skip_gain": {
        "en": "➕ A researcher guessed wrong: you gained an attempt (now {n}/5).",
        "it": "➕ Un ricercatore ha sbagliato: guadagni un tentativo (ora {n}/5).",
    },
    "skip_gain_max": {
        "en": "A researcher guessed wrong, but you already hold the maximum of {n} attempts.",
        "it": "Un ricercatore ha sbagliato, ma hai già il massimo di {n} tentativi.",
    },
    "summary_head_artichoke": {"en": "📋 Summary · Artichoke", "it": "📋 Riepilogo · Artichoke"},
    "summary_head_stargate": {"en": "📋 Summary · Stargate", "it": "📋 Riepilogo · Stargate"},
    "summary_empty": {"en": "No answers yet.", "it": "Ancora nessuna risposta."},
    "summary_identity": {"en": "— Identity {n} —", "it": "— Identità {n} —"},
    "summary_pending": {
        "en": "⏳ Waiting for {patient}: {who}: {text}",
        "it": "⏳ In attesa di {patient}: {who}: {text}",
    },
    "summary_moves": {"en": "Moves left: {moves}", "it": "Mosse rimaste: {moves}"},
    "summary_points": {"en": "Score: {score}", "it": "Punteggio: {score}"},
    "spoiler_removed": {
        "en": "🚫 {name}'s message was removed: spoiler.",
        "it": "🚫 Messaggio di {name} rimosso: era uno spoiler.",
    },

    # ------------------------------------------------------------ /hold
    "hold_usage": {
        "en": "Usage: /hold <minutes> (max 10, decimals allowed)",
        "it": "Uso: /hold <minuti> (max 10, anche decimali)",
    },
    "hold_max": {"en": "The maximum is 10 minutes per pause.", "it": "Il massimo è 10 minuti per pausa."},
    "hold_off": {"en": "Pauses are disabled in this group.", "it": "Le pause sono disattivate in questo gruppo."},
    "hold_admins": {
        "en": "In this group only admins can pause the round.",
        "it": "In questo gruppo solo gli admin possono mettere in pausa il round.",
    },
    "hold_used": {
        "en": "You already used your pause in this round.",
        "it": "Hai già usato la tua pausa in questo round.",
    },
    "hold_already": {"en": "The round is already paused.", "it": "Il round è già in pausa."},
    "hold_none_left": {
        "en": "No pause time left in this round (30 minutes in total).",
        "it": "Nessun tempo di pausa rimasto in questo round (30 minuti in totale).",
    },
    "hold_started": {
        "en": "⏸ {name} paused the round for {dur}. Any player can resume earlier with /ready.",
        "it": "⏸ {name} ha messo in pausa il round per {dur}. Qualsiasi giocatore può riprendere prima con /ready.",
    },
    "hold_ended": {"en": "▶️ The round resumes.", "it": "▶️ Il round riprende."},

    # ------------------------------------------------------------ endings
    "reveal_dr_a": {"en": "\n🧑‍🔬 Dr. A was {name}.", "it": "\n🧑‍🔬 Il Dr. A era {name}."},
    "reveal_skip": {"en": "\n🕶 Agent Skip was {name}.", "it": "\n🕶 L'agente Skip era {name}."},
    "reveal_team": {"en": "\n🏷 {team}: {members}", "it": "\n🏷 {team}: {members}"},
    "solved_artichoke": {
        "en": "🎉 {guesser} found the identity: {title}!\n🏆 Winners: {k} (Patient K) and {guesser}.",
        "it": "🎉 {guesser} ha scoperto l'identità: {title}!\n🏆 Vincitori: {k} (Paziente K) e {guesser}.",
    },
    "point_scored": {
        "en": "🎯 {guesser} guessed {title}: point for team {team}! Score: {score}",
        "it": "🎯 {guesser} ha indovinato {title}: punto per la squadra {team}! Punteggio: {score}",
    },
    "next_identity_group": {
        "en": "🧠 {k} is choosing a new identity… (moves are reset)",
        "it": "🧠 {k} sta scegliendo una nuova identità… (le mosse si azzerano)",
    },
    "dm_next_identity": {
        "en": "A team scored! Pick a new identity, different from the previous ones. You have 2 minutes.",
        "it": "Una squadra ha segnato! Scegli una nuova identità, diversa dalle precedenti. Hai 2 minuti.",
    },
    "team_win": {
        "en": "🏆 Team {team} wins with {pts} points!\nWinners: {winners}\nIdentities: {ids}",
        "it": "🏆 La squadra {team} vince con {pts} punti!\nVincitori: {winners}\nIdentità: {ids}",
    },
    "team_win_lead": {
        "en": "🏁 The round is over: team {team} leads with {pts} points and wins!\nWinners: {winners}\nIdentities: {ids}",
        "it": "🏁 Il round è finito: la squadra {team} è in testa con {pts} punti e vince!\nVincitori: {winners}\nIdentità: {ids}",
    },
    "skip_win": {
        "en": "🕶 Agent Skip ({skip}) guessed {title} and wins alone!\nIdentities: {ids}",
        "it": "🕶 L'agente Skip ({skip}) ha indovinato {title} e vince da solo!\nIdentità: {ids}",
    },
    "no_winner_artichoke": {
        "en": "🏁 Nobody found the identity: {title}. No winner.",
        "it": "🏁 Nessuno ha scoperto l'identità: {title}. Nessun vincitore.",
    },
    "no_winner_stargate": {
        "en": "🏁 Round over: the teams are tied ({score}). No winner.\nIdentities: {ids}",
        "it": "🏁 Round terminato: le squadre sono in parità ({score}). Nessun vincitore.\nIdentità: {ids}",
    },
    "none_label": {"en": "none", "it": "nessuno"},
    "vote_option_none": {"en": "No Dr. A", "it": "Nessun Dr. A"},
    "btn_vote_skip": {"en": "⏭ Skip", "it": "⏭ Salta"},
    "vote_start": {
        "en": (
            "🗳 Nobody found the identity. Is there a Dr. A among you? Vote for who you suspect, or for “No Dr. A” "
            "(secret ballot, no changes, not for yourself). The correct option needs a clear plurality. "
            "Skip to abstain. You have {secs} seconds."
        ),
        "it": (
            "🗳 Nessuno ha scoperto l'identità. C'è un Dr. A tra voi? Votate chi sospettate, oppure «Nessun Dr. A» "
            "(voto segreto, non modificabile, non per se stessi). L'opzione corretta deve avere la maggioranza "
            "relativa. Salta per astenerti. Avete {secs} secondi."
        ),
    },
    "vote_status": {
        "en": "Votes: {n}/{total}\nLeading: {leaders} ({top})",
        "it": "Voti: {n}/{total}\nIn testa: {leaders} ({top})",
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
    "vote_skipped": {"en": "You abstained.", "it": "Ti sei astenuto."},
    "vote_ok_dra": {
        "en": "🔎 Dr. A was {a} and has been unmasked! Winners (correct voters): {winners}.\nIdentity: {title}\nVotes: {tally}",
        "it": "🔎 Il Dr. A era {a} ed è stato smascherato! Vincitori (chi ha votato giusto): {winners}.\nIdentità: {title}\nVoti: {tally}",
    },
    "vote_ok_none": {
        "en": "✅ There was no Dr. A, and you got it right! Winners: {winners}.\nIdentity: {title}\nVotes: {tally}",
        "it": "✅ Non c'era nessun Dr. A, e avete indovinato! Vincitori: {winners}.\nIdentità: {title}\nVoti: {tally}",
    },
    "vote_fail_dra": {
        "en": "😈 Dr. A was {a} and got away with it! Dr. A wins alone.\nIdentity: {title}\nVotes: {tally}",
        "it": "😈 Il Dr. A era {a} e l'ha fatta franca! Vince il Dr. A da solo.\nIdentità: {title}\nVoti: {tally}",
    },
    "vote_fail_none": {
        "en": "❌ There was no Dr. A, and the vote went wrong. Nobody wins.\nIdentity: {title}\nVotes: {tally}",
        "it": "❌ Non c'era nessun Dr. A, e il voto è sbagliato. Non vince nessuno.\nIdentità: {title}\nVoti: {tally}",
    },

    # ------------------------------------------------------------ statistics
    "role_patient": {"en": "Patient", "it": "Paziente"},
    "role_researcher": {"en": "Researcher", "it": "Ricercatore"},
    "role_dr_a": {"en": "Dr. A", "it": "Dr. A"},
    "role_skip": {"en": "Agent Skip", "it": "Agente Skip"},
    "stats_title": {"en": "📊 Group stats", "it": "📊 Statistiche del gruppo"},
    "stats_empty": {
        "en": "No completed rounds in this group yet.",
        "it": "Nessun round completato in questo gruppo.",
    },
    "stats_rounds": {"en": "Rounds played: {total} ({breakdown})", "it": "Round giocati: {total} ({breakdown})"},
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
    "stats_skip": {"en": "🕶 Agent Skip wins: {n}", "it": "🕶 Vittorie dell'agente Skip: {n}"},
    "my_title": {"en": "👤 Stats for {name} ({scope})", "it": "👤 Statistiche di {name} ({scope})"},
    "scope_group": {"en": "this group", "it": "questo gruppo"},
    "scope_all": {"en": "all groups", "it": "tutti i gruppi"},
    "my_empty": {"en": "No completed rounds yet.", "it": "Ancora nessun round completato."},
    "my_total": {
        "en": "Rounds: {played} · wins: {wins} ({pct}%)",
        "it": "Round: {played} · vittorie: {wins} ({pct}%)",
    },
    "my_modes": {"en": "By mode (wins/played): {text}", "it": "Per modalità (vittorie/giocati): {text}"},
    "my_roles": {"en": "By role (wins/played): {text}", "it": "Per ruolo (vittorie/giocati): {text}"},
    "my_favorite": {"en": "Most played role: {role} ({n})", "it": "Ruolo più giocato: {role} ({n})"},
    "my_guessed": {"en": "Identities guessed: {n}", "it": "Identità indovinate: {n}"},
    "my_fastest": {"en": "Fastest solve: {moves} moves", "it": "Soluzione più rapida: {moves} mosse"},
    "my_caught": {"en": "Caught as Dr. A: {c} of {n}", "it": "Scoperto come Dr. A: {c} su {n}"},

    # ------------------------------------------------------------ /rules
    "rules_sent": {
        "en": "📩 {name}, I sent you the rules in private.",
        "it": "📩 {name}, ti ho inviato le regole in privato.",
    },
    "rules_general": {
        "en": (
            "📖 Artichoke: how it works\n\n"
            "Guess a famous identity (a real or fictional person, a deity…) by asking yes/no questions. "
            "Each mode is inspired by a secret psychological program of the Cold War.\n\n"
            "Modes: Artichoke (2+ players) and Stargate (3+ players).\n\n"
            "Round flow: /newgame (the creator picks the mode and options) → /join → the round starts when the "
            "5 minutes of sign-ups are over, or earlier with /ready (any joined player, if there are enough "
            "players). /wait <minutes> extends the sign-ups (max 10 per use, decimals allowed). Everyone must "
            "have pressed /start in my private chat.\n\n"
            "Pause: /hold <minutes> freezes the round (max 10 minutes, once per player per round, 30 minutes "
            "in total); /ready resumes it. Group admins can disable or restrict it in /settings.\n\n"
            "Answers: the Patient answers Yes, No or Don't know within 5 minutes. “Don't know” doesn't cost a move.\n\n"
            "Commands: /ask <text> · /try <name> · /summary · /hold · /stats · /mystats · /rules · /stop · /settings"
        ),
        "it": (
            "📖 Artichoke: come funziona\n\n"
            "Indovina un'identità famosa (una persona reale o di fantasia, una divinità…) facendo domande sì/no. "
            "Ogni modalità è ispirata a un programma psicologico segreto della Guerra Fredda.\n\n"
            "Modalità: Artichoke (2+ giocatori) e Stargate (3+ giocatori).\n\n"
            "Svolgimento: /newgame (chi crea il round sceglie modalità e opzioni) → /join → il round parte allo "
            "scadere dei 5 minuti di iscrizioni, o prima con /ready (qualsiasi giocatore iscritto, se ci sono "
            "abbastanza giocatori). /wait <minuti> prolunga le iscrizioni (max 10 per volta, anche decimali). "
            "Tutti devono aver premuto /start nella mia chat privata.\n\n"
            "Pausa: /hold <minuti> ferma il round (max 10 minuti, una volta a testa per round, 30 minuti in "
            "totale); /ready lo riprende. Gli admin del gruppo possono disattivarla o limitarla in /settings.\n\n"
            "Risposte: il Paziente risponde Sì, No o Non lo so entro 5 minuti. «Non lo so» non costa una mossa.\n\n"
            "Comandi: /ask <testo> · /try <nome> · /summary · /hold · /stats · /mystats · /rules · /stop · /settings"
        ),
    },
    "rules_artichokemode": {
        "en": (
            "🧪 Artichoke: rules\n\n"
            "Inspired by Project Artichoke, the CIA experiments on interrogation and amnesia. 2+ players, roles "
            "drawn at random:\n"
            "• 🧠 Patient K (1 player): an amnesiac who secretly picks a famous identity (with a Wikipedia page) "
            "and answers the researchers' questions in public.\n"
            "• 🔬 Researchers (everyone else): try to work out K's identity.\n"
            "• 🧑‍🔬 Dr. A (only with 5+ players, 70% chance by default): the mad scientist. Knows the identity and "
            "must stay undercover: pretends to investigate and misleads the others (his attempts can never win).\n\n"
            "Moves: every researcher (and Dr. A) has the same number of moves, questions and attempts together. "
            "Automatic count: 2 players 25 · 3 players 15 each · 4 to 6 players 10 each · 7-8 players 7 each · "
            "9-15 players 5 each · 16+ players 3 each (group admins can let the creator choose in /settings). "
            "/ask asks a yes/no question, one at a time; /try makes an attempt, and a wrong attempt costs a move.\n\n"
            "The round ends when a researcher guesses, when all researchers are out of moves, or after 10 minutes "
            "without activity.\n\n"
            "How to win:\n"
            "• K and the first researcher who guesses win together; everyone else loses.\n"
            "• If nobody guesses and there are 5+ players, everyone votes (90 seconds): for a player, for “No Dr. A”, "
            "or Skip to abstain. Secret ballot, no changes, not for yourself. The correct option (Dr. A, or “No Dr. A” "
            "if he isn't in the game) must get a clear plurality, ties don't count. If it does, only those who voted "
            "for it win. Otherwise Dr. A wins alone, or nobody wins if he isn't there.\n"
            "• With fewer than 5 players, if nobody guesses everybody loses."
        ),
        "it": (
            "🧪 Artichoke: regole\n\n"
            "Ispirata al Progetto Artichoke, gli esperimenti della CIA su interrogatori e amnesia. 2+ giocatori, "
            "ruoli estratti a caso:\n"
            "• 🧠 Paziente K (1 giocatore): un amnesico che sceglie in segreto un'identità famosa (con una pagina "
            "su Wikipedia) e risponde pubblicamente alle domande dei ricercatori.\n"
            "• 🔬 Ricercatori (tutti gli altri): cercano di scoprire l'identità di K.\n"
            "• 🧑‍🔬 Dr. A (solo con 5+ giocatori, 70% di probabilità di default): lo scienziato pazzo. Conosce "
            "l'identità e deve restare nell'ombra: finge di indagare e svia gli altri (i suoi tentativi non "
            "possono mai vincere).\n\n"
            "Mosse: ogni ricercatore (e il Dr. A) ha lo stesso numero di mosse, domande e tentativi insieme. "
            "Conteggio automatico: 2 giocatori 25 · 3 giocatori 15 a testa · da 4 a 6 giocatori 10 a testa · "
            "7-8 giocatori 7 a testa · 9-15 giocatori 5 a testa · 16+ giocatori 3 a testa (gli admin possono far "
            "scegliere a chi crea il round in /settings). /ask fa una domanda sì/no, una alla volta; /try fa un "
            "tentativo, e un tentativo sbagliato costa una mossa.\n\n"
            "Il round finisce quando un ricercatore indovina, quando tutti i ricercatori hanno finito le mosse, "
            "o dopo 10 minuti di inattività.\n\n"
            "Come si vince:\n"
            "• K e il primo ricercatore che indovina vincono insieme; tutti gli altri perdono.\n"
            "• Se nessuno indovina e ci sono 5+ giocatori, tutti votano (90 secondi): per un giocatore, per "
            "«Nessun Dr. A», o Salta per astenersi. Voto segreto, non modificabile, non per se stessi. L'opzione "
            "corretta (il Dr. A, o «Nessun Dr. A» se non è in gioco) deve avere la maggioranza relativa, i "
            "pareggi non contano. In quel caso vincono solo coloro che l'hanno votata. Altrimenti vince il Dr. A "
            "da solo, o nessuno se non c'è.\n"
            "• Con meno di 5 giocatori, se nessuno indovina perdono tutti."
        ),
    },
    "rules_stargatemode": {
        "en": (
            "🕵️ Stargate: rules\n\n"
            "Inspired by the Stargate Project, the CIA remote-viewing program. 3+ players, 2 to 4 teams chosen by "
            "the creator. Each team needs the same number of researchers, at least 2 (1 is enough with two teams): "
            "minimum players are 3 (2 teams), 7 (3 teams), 9 (4 teams). If the players can't be split evenly the "
            "round doesn't start.\n\n"
            "Roles:\n"
            "• 🧠 Patient K: picks a secret identity and answers the questions of all teams in public.\n"
            "• 🔬 Researchers: split into teams named at random (Grill Flame, Center Lane, Sun Streak, Gondola "
            "Wish). Everyone knows the teams in play and their own team, but not their teammates.\n"
            "• 🕶 Agent Skip (only when the total number of players is even): a CIA subject of remote-viewing "
            "studies, belonging to no team. Asks questions like the others but starts with 0 attempts, gaining "
            "one (up to 5 at a time) every time a researcher guesses wrong.\n\n"
            "How to play: /ask and /try work as in Artichoke, one question at a time. Attempts are public. Each "
            "researcher has the same number of moves for each identity (automatic count by number of players, as "
            "in Artichoke). When a team guesses an identity it scores 1 point and K picks a new identity; moves "
            "reset. There is no time limit, only the 10-minute inactivity rule. /summary lists every question and "
            "answer, with no team shown.\n\n"
            "How to win:\n"
            "• The first team with 2 points wins, together with K.\n"
            "• Agent Skip wins ALONE (everyone else loses) by guessing an identity before the round ends.\n"
            "• If all researchers run out of moves or the round goes inactive, the team with most points wins; "
            "a tie means no winner."
        ),
        "it": (
            "🕵️ Stargate: regole\n\n"
            "Ispirata al Progetto Stargate, il programma CIA di remote viewing. 3+ giocatori, da 2 a 4 squadre "
            "scelte da chi crea il round. Ogni squadra ha lo stesso numero di ricercatori, almeno 2 (basta 1 con "
            "due squadre): i giocatori minimi sono 3 (2 squadre), 7 (3 squadre), 9 (4 squadre). Se i giocatori "
            "non si dividono in modo uguale il round non parte.\n\n"
            "Ruoli:\n"
            "• 🧠 Paziente K: sceglie un'identità segreta e risponde pubblicamente alle domande di tutte le squadre.\n"
            "• 🔬 Ricercatori: divisi in squadre dai nomi estratti a caso (Grill Flame, Center Lane, Sun Streak, "
            "Gondola Wish). Tutti conoscono le squadre in gioco e la propria, ma non i compagni.\n"
            "• 🕶 Agente Skip (solo se il numero totale di giocatori è pari): soggetto CIA di studi sul remote "
            "viewing, senza squadra. Fa domande come gli altri ma inizia con 0 tentativi, ne guadagna uno (fino a "
            "5 alla volta) ogni volta che un ricercatore sbaglia.\n\n"
            "Come si gioca: /ask e /try funzionano come in Artichoke, una domanda alla volta. I tentativi sono "
            "pubblici. Ogni ricercatore ha lo stesso numero di mosse per ogni identità (conteggio automatico in "
            "base ai giocatori, come in Artichoke). Quando una squadra indovina un'identità ottiene 1 punto e K "
            "sceglie una nuova identità; le mosse si azzerano. Non c'è limite di tempo, solo la regola dei 10 "
            "minuti di inattività. /summary elenca tutte le domande e risposte, senza indicare le squadre.\n\n"
            "Come si vince:\n"
            "• La prima squadra con 2 punti vince, insieme a K.\n"
            "• L'agente Skip vince DA SOLO (tutti gli altri perdono) se indovina un'identità prima della fine.\n"
            "• Se tutti i ricercatori finiscono le mosse o il round va in inattività, vince la squadra con più "
            "punti; a pari punti non vince nessuno."
        ),
    },
}
