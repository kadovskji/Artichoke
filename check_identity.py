"""Diagnostic tool: shows what the bot sees when it validates an identity.

Usage:  python check_identity.py "Roma" [en|it]
It needs no BOT_TOKEN and does not touch the database.
"""
import asyncio
import sys

import httpx

import wiki
from game import wiki_langs


async def main(name: str, lang: str) -> None:
    langs = wiki_langs(lang)
    print(f"Name: {name!r}  | Wikipedia editions, in order: {langs}")
    print(f"User-Agent: {wiki.HEADERS['User-Agent']}\n")

    found = await wiki.verify_wikipedia(name, langs)
    print("1) Wikipedia  ->", found)
    if found is None:
        print("   No page (or only a disambiguation page): the bot would refuse it.")
        return
    title, qid = found
    if not qid:
        print("   No Wikidata id (or Wikipedia unreachable, see the warning above):")
        print("   the bot would accept it without verification.")
        return

    print(f"\n2) Wikidata item: {qid}")
    try:
        async with httpx.AsyncClient(timeout=15, headers=wiki.SPARQL_HEADERS) as client:
            r = await client.get(wiki.SPARQL_URL, params={
                "query": wiki.character_query(qid), "format": "json"})
        print(f"   HTTP status: {r.status_code}")
        print(f"   Response: {r.text[:300]!r}")
    except httpx.HTTPError as exc:
        print(f"   Request failed: {exc!r}")

    verdict = await wiki.is_character(qid)
    label = {True: "ACCEPT (it is a person/character)",
             False: "REFUSE (not a person/character)",
             None: "ACCEPT WITHOUT VERIFICATION (Wikidata check failed)"}[verdict]
    print(f"\n3) Bot decision for “{title}”: {label}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: python check_identity.py "Name" [en|it]')
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "en"))
