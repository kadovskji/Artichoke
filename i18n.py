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
        "en": "🎲 {name}, choose a game mode:\n\n🧪 Artichoke (2+ players): Patient K is an amnesiac who knows a secret identity but cannot say it. The researchers must find it with yes/no questions. With 5+ players a mad scientist, Dr. A, may be hiding among them.\n\n🕵️ Stargate (4+ players): teams of researchers race to identify a secret identity, while the Whistleblower K hides among them. Agent Skip, known to all, must find out who K is and arrest them.",
        "it": "🎲 {name}, scegli la modalità di gioco:\n\n🧪 Artichoke (2+ giocatori): il Paziente K è un amnesico che conosce un'identità segreta ma non può dirla. I ricercatori devono scoprirla con domande sì/no. Con 5+ giocatori uno scienziato pazzo, il Dr. A, può nascondersi tra loro.\n\n🕵️ Stargate (4+ giocatori): squadre di ricercatori in gara per scoprire un'identità segreta, mentre il Whistleblower K si nasconde tra loro. L'agente Skip, noto a tutti, deve scoprire chi è K e arrestarlo.",
    },
    "pick_teams": {
        "en": "🕵️ Stargate: how many teams? Minimum players (K and Agent Skip included): 2 teams → 4, 3 teams → 8, 4 teams → 10.",
        "it": "🕵️ Stargate: quante squadre? Giocatori minimi (K e l'agente Skip compresi): 2 squadre → 4, 3 squadre → 8, 4 squadre → 10.",
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
    "dm_failed_s": {
        "en": "I can't message one of the players privately. Round cancelled: everyone must press /start in my private chat.",
        "it": "Non riesco a scrivere in privato a uno dei giocatori. Round annullato: ognuno deve premere /start nella mia chat privata.",
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
        "en": "🕵️ Stargate starts with {n} players!\n🕶 Agent Skip: {skip}\n🏷 Teams in play: {teams}\n🧠 The Whistleblower K hides among the others: nobody knows who!\nYour role is secret: check your private chat. The first team to guess the identity wins together with K. Agent Skip must find out who K is and arrest them.\n⏱ Moves per person: {moves}",
        "it": "🕵️ Stargate parte con {n} giocatori!\n🕶 Agente Skip: {skip}\n🏷 Squadre in gioco: {teams}\n🧠 Il Whistleblower K si nasconde tra gli altri: nessuno sa chi sia!\nIl tuo ruolo è segreto: controlla la chat privata. La prima squadra che indovina l'identità vince insieme a K. L'agente Skip deve scoprire chi è K e arrestarlo.\n⏱ Mosse a testa: {moves}",
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
        "en": "You are the Whistleblower K 🧠, in secret. Send me the name of a famous person or character (real or fictional, with a Wikipedia page): it will be the only identity of the round. You must hide among the researchers: ask questions and make attempts like them (your attempts are always wrong), and answer EVERY question here in private, within 5 minutes. To your own questions you can only answer “Don't know”. You win together with the team that guesses the identity. Teams in play: {teams}. Agent Skip ({skip}) is trying to find out who you are and arrest you!",
        "it": "Sei il Whistleblower K 🧠, in segreto. Scrivimi il nome di un personaggio famoso (reale o di fantasia, con una pagina su Wikipedia): sarà l'unica identità del round. Devi nasconderti tra i ricercatori: fai domande e tentativi come loro (i tuoi tentativi sono sempre sbagliati) e rispondi a OGNI domanda qui in privato, entro 5 minuti. Alle tue domande puoi rispondere solo «Non lo so». Vinci insieme alla squadra che indovina l'identità. Squadre in gioco: {teams}. L'agente Skip ({skip}) cerca di scoprire chi sei per arrestarti!",
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
        "en": "You are a researcher 🔬 of team {team}. Teams in play: {teams}. Teammates are secret, even to you. Somewhere among the players hides the Whistleblower K, who knows the identity. Use /ask and /try in the group: you have {moves} moves, and “Don't know” answers cost a move too. The first team to guess the identity wins together with K.",
        "it": "Sei un ricercatore 🔬 della squadra {team}. Squadre in gioco: {teams}. I compagni sono segreti, anche per te. Tra i giocatori si nasconde il Whistleblower K, che conosce l'identità. Usa /ask e /try nel gruppo: hai {moves} mosse, e anche le risposte «Non lo so» costano una mossa. La prima squadra che indovina l'identità vince insieme a K.",
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
        "en": "You are Agent Skip 🕶, a CIA subject in a remote-viewing study, known to all. Your goal: find out who the Whistleblower K is, hiding among the players, and arrest them. You can follow the questions (and ask yours: {moves} moves). You start with 0 arrests and gain one every time a player guesses wrong (up to 2). While the round is on you can make only 1 arrest, with /arrest; the other one is for the end of the round (you have 90 seconds). You win ALONE by arresting K. In this private chat you can also try the identity with /try <name>: if you guess it, /summary is disabled for all the other players.",
        "it": "Sei l'agente Skip 🕶, soggetto CIA di uno studio sul remote viewing, noto a tutti. Il tuo obiettivo: scoprire chi è il Whistleblower K, nascosto tra i giocatori, e arrestarlo. Puoi seguire le domande (e farne: {moves} mosse). Inizi con 0 arresti e ne guadagni uno ogni volta che un giocatore sbaglia un tentativo (fino a 2). Durante il round puoi fare un solo arresto, con /arrest; l'altro è per la fine del round (hai 90 secondi). Vinci DA SOLO arrestando K. In questa chat privata puoi anche provare l'identità con /try <nome>: se la indovini, /summary viene disattivato per tutti gli altri giocatori.",
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
        "en": "🕵️ The hunt begins! Each player has {moves} moves. The first team to name the identity wins together with the Whistleblower K, who is hiding among you.\n/ask <text> · /try <name> · /arrest (Agent Skip) · /summary · /hold\nThe round ends after 10 minutes without activity.",
        "it": "🕵️ La caccia inizia! Ogni giocatore ha {moves} mosse. La prima squadra che nomina l'identità vince insieme al Whistleblower K, nascosto tra voi.\n/ask <testo> · /try <nome> · /arrest (agente Skip) · /summary · /hold\nIl round termina dopo 10 minuti di inattività.",
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
    "ask_pending_s": {
        "en": "Wait for the answer to the pending question.",
        "it": "Aspetta la risposta alla domanda in sospeso.",
    },
    "no_moves": {"en": "You have no moves left.", "it": "Non hai più mosse."},
    "question_msg": {
        "en": "❓ {who} ({used}/{limit}): {text}\n\n{patient}, please answer:",
        "it": "❓ {who} ({used}/{limit}): {text}\n\n{patient}, rispondi:",
    },
    "question_msg_s": {
        "en": "❓ {who} ({used}/{limit}): {text}\n\n⏳ Waiting for the Whistleblower's answer…",
        "it": "❓ {who} ({used}/{limit}): {text}\n\n⏳ In attesa della risposta del Whistleblower…",
    },
    "dm_question": {
        "en": "❓ {who} asks: {text}\n\nAnswer within 5 minutes:",
        "it": "❓ {who} chiede: {text}\n\nRispondi entro 5 minuti:",
    },
    "dm_question_own": {
        "en": "❓ You asked: {text}\n\nTo hide among the others you must answer your own question, but only with “Don't know”:",
        "it": "❓ Hai chiesto: {text}\n\nPer mimetizzarti devi rispondere alla tua domanda, ma solo «Non lo so»:",
    },
    "dm_question_done": {
        "en": "✅ Answered: {answer}",
        "it": "✅ Risposta data: {answer}",
    },
    "btn_yes": {"en": "✅ Yes", "it": "✅ Sì"},
    "btn_no": {"en": "❌ No", "it": "❌ No"},
    "btn_unknown": {"en": "🤷 Don't know", "it": "🤷 Non lo so"},
    "answer_own_only": {
        "en": "To your own question you can only answer “Don't know”.",
        "it": "Alla tua domanda puoi rispondere solo «Non lo so».",
    },
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
    "answer_timeout_s": {
        "en": "⌛ The Whistleblower didn't answer in time: round cancelled.\nIdentity: {ids}",
        "it": "⌛ Il Whistleblower non ha risposto in tempo: round annullato.\nIdentità: {ids}",
    },
    "try_wrong": {
        "en": "❌ {who}: “{text}” is not the right identity. Moves left for {who}: {left}.",
        "it": "❌ {who}: «{text}» non è l'identità giusta. Mosse rimaste a {who}: {left}.",
    },
    "arrest_menu": {
        "en": "🕶 Agent Skip, who do you think is the Whistleblower K? Arrests: {n}.",
        "it": "🕶 Agente Skip, chi pensi sia il Whistleblower K? Arresti: {n}.",
    },
    "arrest_forbidden": {
        "en": "Only Agent Skip can arrest.",
        "it": "Solo l'agente Skip può arrestare.",
    },
    "arrest_none": {
        "en": "You have no arrests: you gain one when a player guesses wrong.",
        "it": "Non hai arresti: ne guadagni uno quando un giocatore sbaglia un tentativo.",
    },
    "arrest_wait_end": {
        "en": "While the round is on you can make only 1 arrest: the other one is for the end of the round.",
        "it": "Durante il round puoi fare un solo arresto: l'altro è per la fine del round.",
    },
    "arrest_wrong": {
        "en": "❌ Agent Skip arrested {name} on suspicion of being the Whistleblower: but {name} is just a researcher. Arrests left: {n}.",
        "it": "❌ L'agente Skip ha arrestato {name} con l'accusa di essere il Whistleblower: ma {name} è solo un ricercatore. Arresti rimasti: {n}.",
    },
    "arrest_done": {
        "en": "Arrest made.",
        "it": "Arresto effettuato.",
    },
    "arrest_stale": {
        "en": "This arrest is no longer possible.",
        "it": "Questo arresto non è più possibile.",
    },
    "final_window": {
        "en": "🏁 The round is over, but Agent Skip has {secs} seconds to use the remaining arrests with /arrest. Who is the Whistleblower?",
        "it": "🏁 Il round è finito, ma l'agente Skip ha {secs} secondi per usare gli arresti rimasti con /arrest. Chi è il Whistleblower?",
    },
    "agent_try_private": {
        "en": "Agent Skip: try the identity here in private, not in the group.",
        "it": "Agente Skip: prova l'identità qui in privato, non nel gruppo.",
    },
    "agent_identity_ok": {
        "en": "✅ Correct! /summary is now disabled for all the other players.",
        "it": "✅ Esatto! Ora /summary è disattivato per tutti gli altri giocatori.",
    },
    "agent_identity_wrong": {
        "en": "❌ Wrong identity.",
        "it": "❌ Identità sbagliata.",
    },
    "agent_identity_already": {
        "en": "You already guessed the identity.",
        "it": "Hai già indovinato l'identità.",
    },
    "try_forbidden": {
        "en": "Only researchers can make attempts here.",
        "it": "Qui solo i ricercatori possono fare tentativi.",
    },
    "skip_gain": {
        "en": "➕ A player guessed wrong: you gained an arrest (now {n}/2).",
        "it": "➕ Un giocatore ha sbagliato: guadagni un arresto (ora {n}/2).",
    },
    "skip_gain_max": {
        "en": "A player guessed wrong, but you already hold the maximum of {n} arrests.",
        "it": "Un giocatore ha sbagliato, ma hai già il massimo di {n} arresti.",
    },
    "summary_head_artichoke": {"en": "📋 Summary · Artichoke", "it": "📋 Riepilogo · Artichoke"},
    "summary_head_stargate": {"en": "📋 Summary · Stargate", "it": "📋 Riepilogo · Stargate"},
    "summary_empty": {"en": "No answers yet.", "it": "Ancora nessuna risposta."},
    "summary_pending_s": {
        "en": "⏳ Waiting for the answer: {who}: {text}",
        "it": "⏳ In attesa della risposta: {who}: {text}",
    },
    "summary_pending": {
        "en": "⏳ Waiting for {patient}: {who}: {text}",
        "it": "⏳ In attesa di {patient}: {who}: {text}",
    },
    "summary_moves": {"en": "Moves left: {moves}", "it": "Mosse rimaste: {moves}"},
    "summary_off": {
        "en": "⛔ /summary is not available right now.",
        "it": "⛔ /summary non è disponibile al momento.",
    },
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
    "reveal_patient": {
        "en": "\n🧠 Whistleblower K was {name}.",
        "it": "\n🧠 Il Whistleblower K era {name}.",
    },
    "reveal_skip": {"en": "\n🕶 Agent Skip was {name}.", "it": "\n🕶 L'agente Skip era {name}."},
    "reveal_team": {"en": "\n🏷 {team}: {members}", "it": "\n🏷 {team}: {members}"},
    "solved_artichoke": {
        "en": "🎉 {guesser} found the identity: {title}!\n🏆 Winners: {k} (Patient K) and {guesser}.",
        "it": "🎉 {guesser} ha scoperto l'identità: {title}!\n🏆 Vincitori: {k} (Paziente K) e {guesser}.",
    },
    "team_win": {
        "en": "🏆 Team {team} named the identity: {title}!\nWinners: {winners}",
        "it": "🏆 La squadra {team} ha nominato l'identità: {title}!\nVincitori: {winners}",
    },
    "skip_win": {
        "en": "🕶 Agent Skip ({skip}) arrested the Whistleblower K: {k}! The Agent wins alone.\nIdentity: {ids}",
        "it": "🕶 L'agente Skip ({skip}) ha arrestato il Whistleblower K: {k}! L'agente vince da solo.\nIdentità: {ids}",
    },
    "no_winner_artichoke": {
        "en": "🏁 Nobody found the identity: {title}. No winner.",
        "it": "🏁 Nessuno ha scoperto l'identità: {title}. Nessun vincitore.",
    },
    "no_winner_stargate": {
        "en": "🏁 Round over: nobody named the identity ({ids}). No winner.",
        "it": "🏁 Round terminato: nessuno ha nominato l'identità ({ids}). Nessun vincitore.",
    },
    "none_label": {"en": "none", "it": "nessuno"},
    "vote_option_none": {"en": "No Dr. A", "it": "Nessun Dr. A"},
    "vote_start": {
        "en": "🗳 Nobody found the identity. Is there a Dr. A among you? Vote for who you suspect, or for “No Dr. A” (secret ballot, no changes, not for yourself). The correct option needs strictly more votes than any other. You have {secs} seconds.",
        "it": "🗳 Nessuno ha scoperto l'identità. C'è un Dr. A tra voi? Votate chi sospettate, oppure «Nessun Dr. A» (voto segreto, non modificabile, non per se stessi). L'opzione corretta deve avere strettamente più voti di ogni altra. Avete {secs} secondi.",
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
    "role_patient": {"en": "Patient / Whistleblower", "it": "Paziente / Whistleblower"},
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
        "en": "📖 Artichoke: how it works\n\nGuess a famous identity (a real or fictional person, a deity…) by asking yes/no questions. Each mode is inspired by a secret psychological program of the Cold War.\n\nModes: Artichoke (2+ players) and Stargate (4+ players).\n\nRound flow:\n• /newgame: the creator picks the mode and the options.\n• /join: everyone who wants to play (they must have pressed /start in my private chat).\n• The round starts when the 5 minutes of sign-ups are over, or earlier with /ready (any joined player, if there are enough players). /wait <minutes> extends the sign-ups (max 10 per use, decimals allowed).\n\nMoves: every player has the same number of moves (questions + attempts), decided by the number of players: 2 → 25 · 3 → 15 · 4-6 → 10 · 7-8 → 7 · 9-15 → 5 · 16+ → 3 (group admins can let the creator choose).\n\nPause: /hold <minutes> freezes the round (max 10 minutes, once per player per round, 30 minutes in total); /ready resumes it. Group admins can disable it or restrict it to admins in /settings.\n\nCommands: /ask <text> · /try <name> · /arrest (Stargate, Agent Skip) · /summary · /hold · /stats · /mystats · /rules · /stop · /settings",
        "it": "📖 Artichoke: come funziona\n\nIndovina un'identità famosa (una persona reale o di fantasia, una divinità…) facendo domande sì/no. Ogni modalità è ispirata a un programma psicologico segreto della Guerra Fredda.\n\nModalità: Artichoke (2+ giocatori) e Stargate (4+ giocatori).\n\nSvolgimento:\n• /newgame: chi lo scrive sceglie la modalità e le opzioni.\n• /join: chiunque voglia giocare (deve aver premuto /start nella mia chat privata).\n• Il round parte allo scadere dei 5 minuti di iscrizioni, o prima con /ready (qualsiasi giocatore iscritto, se ci sono abbastanza giocatori). /wait <minuti> prolunga le iscrizioni (max 10 per volta, anche decimali).\n\nMosse: ogni giocatore ha lo stesso numero di mosse (domande + tentativi), deciso dal numero di giocatori: 2 → 25 · 3 → 15 · 4-6 → 10 · 7-8 → 7 · 9-15 → 5 · 16+ → 3 (gli admin possono far scegliere a chi crea il round).\n\nPausa: /hold <minuti> ferma il round (max 10 minuti, una volta a testa per round, 30 minuti in totale); /ready lo riprende. Gli admin del gruppo possono disattivarla o limitarla agli admin in /settings.\n\nComandi: /ask <testo> · /try <nome> · /arrest (Stargate, agente Skip) · /summary · /hold · /stats · /mystats · /rules · /stop · /settings",
    },
    "rules_artichokemode": {
        "en": "🧪 Artichoke: rules\n\nInspired by Project Artichoke, the CIA experiments on interrogation and amnesia. 2+ players.\n\nROLES (drawn at random)\n• 🧠 Patient K (1 player): an amnesiac who secretly picks a famous identity (with a Wikipedia page) and answers the researchers' questions in public (Yes / No / Don't know) within 5 minutes each.\n• 🔬 Researchers (everyone else): try to work out K's identity.\n• 🧑‍🔬 Dr. A (only with 5+ players, present in 70% of the rounds by default): the mad scientist. Knows the identity and must stay undercover: pretends to investigate and misleads the others (his attempts can never win).\n\nMOVES\n• Everyone has the same number of moves, questions and attempts together: 2 players 25 · 3 players 15 each · 4-6 players 10 each · 7-8 players 7 each · 9-15 players 5 each · 16+ players 3 each (group admins can let the creator choose in /settings).\n• /ask asks a yes/no question, one at a time. “Don't know” doesn't cost a move.\n• /try makes an attempt. A wrong attempt costs a move.\n\nEND OF THE ROUND\nThe round ends when a researcher guesses, when all researchers are out of moves, or after 10 minutes without activity.\n\nIf a researcher guesses\n• K and that researcher win together; everyone else loses.\n\nIf nobody guesses\n• 2-4 players: everybody loses.\n• 5+ players: everybody votes for 90 seconds to find out who Dr. A is. Secret ballot, no changes, no self-votes; the bot shows the current leader after each vote. The options are:\n   – every other player (if you suspect that player);\n   – No Dr. A (if you think there is no Dr. A).\n\nTo win the vote\n• You must have voted for the right option: Dr. A, or “No Dr. A” if he isn't in the game.\n• The right option must get strictly more votes than any other option, so ties don't count.\n• Only the players who voted for it win.\n\nOtherwise Dr. A (if present) wins alone; if he isn't in the game, nobody wins.",
        "it": "🧪 Artichoke: regole\n\nIspirata al Progetto Artichoke, gli esperimenti della CIA su interrogatori e amnesia. 2+ giocatori.\n\nRUOLI (estratti a caso)\n• 🧠 Paziente K (1 giocatore): un amnesico che sceglie in segreto un'identità famosa (con una pagina su Wikipedia) e risponde pubblicamente alle domande dei ricercatori (Sì / No / Non lo so) entro 5 minuti ciascuna.\n• 🔬 Ricercatori (tutti gli altri): cercano di scoprire l'identità di K.\n• 🧑‍🔬 Dr. A (solo con 5+ giocatori, presente nel 70% dei round di default): lo scienziato pazzo. Conosce l'identità e deve restare nell'ombra: finge di indagare e svia gli altri (i suoi tentativi non possono mai vincere).\n\nMOSSE\n• Tutti hanno lo stesso numero di mosse, domande e tentativi insieme: 2 giocatori 25 · 3 giocatori 15 a testa · 4-6 giocatori 10 a testa · 7-8 giocatori 7 a testa · 9-15 giocatori 5 a testa · 16+ giocatori 3 a testa (gli admin possono far scegliere a chi crea il round in /settings).\n• /ask fa una domanda sì/no, una alla volta. «Non lo so» non costa una mossa.\n• /try fa un tentativo. Un tentativo sbagliato costa una mossa.\n\nFINE DEL ROUND\nIl round finisce quando un ricercatore indovina, quando tutti i ricercatori hanno finito le mosse, o dopo 10 minuti di inattività.\n\nSe un ricercatore indovina\n• K e quel ricercatore vincono insieme; tutti gli altri perdono.\n\nSe nessuno indovina\n• 2-4 giocatori: perdono tutti.\n• 5+ giocatori: tutti votano per 90 secondi per scoprire chi è il Dr. A. Voto segreto, non modificabile, non per se stessi; il bot mostra chi è in testa dopo ogni voto. Le opzioni sono:\n   – ogni altro giocatore (se sospetti quel giocatore);\n   – Nessun Dr. A (se pensi che non ci sia).\n\nPer vincere il voto\n• Devi aver votato l'opzione giusta: il Dr. A, oppure «Nessun Dr. A» se non è in gioco.\n• L'opzione giusta deve avere strettamente più voti di ogni altra, quindi i pareggi non contano.\n• Vincono solo i giocatori che l'hanno votata.\n\nAltrimenti vince il Dr. A (se presente) da solo; se non è in gioco non vince nessuno.",
    },
    "rules_stargatemode": {
        "en": "🕵️ Stargate: rules\n\nInspired by the Stargate Project, the CIA remote-viewing program. 4+ players, with 2 to 4 teams chosen by the creator.\n\nSETUP\n• Minimum players: 2 teams → 4 · 3 teams → 8 · 4 teams → 10.\n• Besides the Whistleblower K and Agent Skip, the researchers are split into teams of the SAME size: at least 2 researchers per team (1 is enough with two teams). If the players can't be split evenly, the bot says which numbers of players work and the round doesn't start.\n• Teams get random names among Grill Flame, Center Lane, Sun Streak and Gondola Wish. Everyone knows the teams in play and their own team, but not their teammates.\n\nROLES\n• 🔬 Researchers: find the secret identity with their team.\n• 🧠 Whistleblower K: SECRET. Hides among the researchers, knows the only identity of the round (chosen by K) and answers every question in private; the bot publishes the answers without saying who gave them. K also asks questions and makes attempts to blend in: K can answer their own questions only with “Don't know”, and K's attempts are always wrong.\n• 🕶 Agent Skip: KNOWN to all. Must find out who the Whistleblower K is and arrest them.\n\nMOVES\n• Everyone (K and Agent Skip too) has the same number of moves, questions and attempts together, decided by the number of players (see the general rules).\n• In this mode “Don't know” DOES cost a move, for everyone, so that the moves left (shown in /summary) don't give K away.\n• /ask asks a question, one at a time; /try makes an attempt.\n\nAGENT SKIP\n• Starts with 0 arrests and gains one every time a player guesses wrong (max 2).\n• /arrest: pick the player you think is K. While the round is on you can make only 1 arrest; the other one is for the end of the round, when you have 90 seconds.\n• Wrong arrests are public: the arrested player is not K.\n• Skip can also ask questions. In private chat with the bot Skip can try the identity with /try <name>: if Skip guesses it, /summary is disabled for all the other players.\n\nEND OF THE ROUND\nThe round ends when a team names the identity, when all researchers are out of moves, or after 10 minutes without activity. Then Skip has 90 seconds to use the remaining arrests.\n\nHOW TO WIN\n• The first team that names the identity wins together with K.\n• Agent Skip wins ALONE (everyone else loses) by arresting K, even at the end of the round.\n• If nobody names the identity and Skip doesn't arrest K, nobody wins.",
        "it": "🕵️ Stargate: regole\n\nIspirata al Progetto Stargate, il programma CIA di remote viewing. 4+ giocatori, con 2-4 squadre scelte da chi crea il round.\n\nPREPARAZIONE\n• Giocatori minimi: 2 squadre → 4 · 3 squadre → 8 · 4 squadre → 10.\n• Oltre al Whistleblower K e all'agente Skip, i ricercatori sono divisi in squadre della STESSA dimensione: almeno 2 ricercatori per squadra (ne basta 1 con due squadre). Se i giocatori non si dividono in modo uguale, il bot dice quali numeri di giocatori vanno bene e il round non parte.\n• Le squadre hanno nomi estratti a caso tra Grill Flame, Center Lane, Sun Streak e Gondola Wish. Tutti conoscono le squadre in gioco e la propria, ma non i compagni.\n\nRUOLI\n• 🔬 Ricercatori: scoprono l'identità segreta con la propria squadra.\n• 🧠 Whistleblower K: SEGRETO. Si nasconde tra i ricercatori, conosce l'unica identità del round (scelta da K) e risponde a ogni domanda in privato; il bot pubblica le risposte senza dire chi le ha date. K fa anche domande e tentativi per mimetizzarsi: alle proprie domande può rispondere solo «Non lo so» e i suoi tentativi sono sempre sbagliati.\n• 🕶 Agente Skip: NOTO a tutti. Deve scoprire chi è il Whistleblower K e arrestarlo.\n\nMOSSE\n• Tutti (anche K e l'agente Skip) hanno lo stesso numero di mosse, domande e tentativi insieme, deciso dal numero di giocatori (vedi le regole generali).\n• In questa modalità «Non lo so» COSTA una mossa, per tutti, così le mosse rimaste (mostrate in /summary) non rivelano K.\n• /ask fa una domanda, una alla volta; /try fa un tentativo.\n\nAGENTE SKIP\n• Inizia con 0 arresti e ne guadagna uno ogni volta che un giocatore sbaglia un tentativo (max 2).\n• /arrest: scegli il giocatore che pensi sia K. Durante il round puoi fare un solo arresto; l'altro è per la fine del round, quando hai 90 secondi.\n• Gli arresti sbagliati sono pubblici: il giocatore arrestato non è K.\n• Skip può fare anche domande. Nella chat privata con il bot può provare l'identità con /try <nome>: se la indovina, /summary viene disattivato per tutti gli altri giocatori.\n\nFINE DEL ROUND\nIl round finisce quando una squadra nomina l'identità, quando tutti i ricercatori hanno finito le mosse, o dopo 10 minuti di inattività. Poi Skip ha 90 secondi per usare gli arresti rimasti.\n\nCOME SI VINCE\n• La prima squadra che nomina l'identità vince insieme a K.\n• L'agente Skip vince DA SOLO (tutti gli altri perdono) arrestando K, anche a fine round.\n• Se nessuno nomina l'identità e Skip non arresta K, non vince nessuno.",
    },
}
