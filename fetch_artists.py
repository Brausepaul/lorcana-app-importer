#!/usr/bin/env python3
"""Fill the "Künstler/-in" column in Encanto.csv from the official Lorcana card gallery."""

import csv
import html
import re
import sys
import time
import urllib.request

MAPPING = "mapping.csv"
CARDS = "Encanto.csv"
URL = "https://cards.disneylorcana.com/de-DE/?cardId={}"
ARTIST_RE = re.compile(r"Illustration(?:<!-- -->)?:\s*(?:<!-- -->)?(.*?)</p>", re.S)


def load_mapping():
    with open(MAPPING, newline="", encoding="utf-8") as f:
        return {
            (row["Set"].strip(), row["Card Number"].strip()): row["ID"].strip()
            for row in csv.DictReader(f)
        }


def fetch_artist(card_id):
    req = urllib.request.Request(
        URL.format(card_id), headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        page = resp.read().decode("utf-8", "replace")
    m = ARTIST_RE.search(page)
    if not m:
        return None
    text = re.sub(r"<!-- -->", "", m.group(1))
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def main():
    mapping = load_mapping()
    with open(CARDS, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)

    cache = {}
    for row in rows:
        key = (row["Set Number"].strip(), row["Card Number"].strip())
        if key not in cache:
            card_id = mapping.get(key)
            if not card_id:
                print(f"no mapping for set {key[0]} card {key[1]}", file=sys.stderr)
                cache[key] = ""
            else:
                try:
                    cache[key] = fetch_artist(card_id) or ""
                except Exception as exc:  # network hiccup -> leave blank, report
                    print(f"fetch failed for id {card_id}: {exc}", file=sys.stderr)
                    cache[key] = ""
                print(f"{key[0]}/{key[1]} (id {card_id}): {cache[key]}")
                time.sleep(0.5)
        row["Künstler/-in"] = cache[key]

    with open(CARDS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
