"""Wikipedia / Wikidata helpers: identity validation and guess matching."""
import logging
import re

import httpx

from game import Identity, compact

# An identity must be a person or a character (real or fictional), not a place,
# an event or a work. The class of the Wikidata item is checked (subclasses included).
# To widen what is accepted, add entries below.
CHARACTER_CLASSES = (
    "Q5",          # human
    "Q95074",      # fictional character
    "Q15632617",   # fictional human
    "Q3542731",    # fictional animal character
    "Q178885",     # deity
)
CHARACTER_LABELS = (           # classes recognized by their English label
    "mythical character",
    "legendary figure",
    "human who may be fictional",
)

_HEADERS = {"User-Agent": "ArtichokeBot/1.0 (Telegram party game bot)"}


async def verify_wikipedia(name: str, langs: tuple[str, ...]) -> tuple[str, str | None] | None:
    """Return (title, Wikidata id) of the Wikipedia page for `name`, or None if missing.

    Redirects are followed; disambiguation pages are rejected. If Wikipedia can't be
    reached the name is accepted as is, as (name, None), so the game isn't blocked.
    """
    name = name.replace("|", " ").strip()
    if not name:
        return None
    variants = list(dict.fromkeys([name, name.title()]))
    try:
        async with httpx.AsyncClient(timeout=8, headers=_HEADERS) as client:
            for lang in langs:
                r = await client.get(
                    f"https://{lang}.wikipedia.org/w/api.php",
                    params={"action": "query", "format": "json", "formatversion": 2,
                            "titles": "|".join(variants), "redirects": 1,
                            "prop": "pageprops",
                            "ppprop": "disambiguation|wikibase_item"})
                r.raise_for_status()
                for page in r.json()["query"]["pages"]:
                    props = page.get("pageprops", {})
                    if (not page.get("missing") and not page.get("invalid")
                            and "disambiguation" not in props):
                        return page["title"], props.get("wikibase_item")
    except (httpx.HTTPError, KeyError, ValueError):
        logging.warning("Wikipedia unreachable, accepting %r without verification", name)
        return name, None
    return None


async def is_character(qid: str | None) -> bool:
    """True if the Wikidata item is a person or a character.

    If it can't be verified (no id, Wikidata unreachable) it is accepted,
    so the game isn't blocked.
    """
    if not qid or not re.fullmatch(r"Q\d+", qid):
        return True
    classes = ", ".join(f"wd:{c}" for c in CHARACTER_CLASSES)
    labels = ", ".join(f'"{x}"' for x in CHARACTER_LABELS)
    query = (
        "ASK { wd:" + qid + " wdt:P31/wdt:P279* ?c . ?c rdfs:label ?l . "
        'FILTER(lang(?l) = "en" && (?c IN (' + classes + ") || "
        "LCASE(STR(?l)) IN (" + labels + "))) }")
    try:
        async with httpx.AsyncClient(timeout=10, headers=_HEADERS) as client:
            r = await client.get("https://query.wikidata.org/sparql",
                                 params={"query": query, "format": "json"})
            r.raise_for_status()
            return bool(r.json()["boolean"])
    except (httpx.HTTPError, KeyError, ValueError):
        logging.warning("Wikidata unreachable, accepting %s without verification", qid)
        return True


async def match_identity(identities: dict[str, Identity], text: str,
                         langs: tuple[str, ...]) -> str | None:
    """Return the key of the identity that `text` names, or None.

    First a tolerant string comparison (case, spaces, accents, punctuation);
    then the text is resolved through Wikipedia redirects ("Dante" -> "Dante Alighieri").
    """
    guess = compact(text)
    for key, ident in identities.items():
        if guess in ident.accepted:
            return key
    found = await verify_wikipedia(text, langs)
    if found is None:
        return None
    resolved = compact(found[0])
    for key, ident in identities.items():
        if resolved in ident.accepted:
            return key
    return None
