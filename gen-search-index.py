#!/usr/bin/env python3
"""Generate search_index.json from the live pages in gui.py + search_synonyms.json.

Run automatically by up.sh. Page titles are scraped from gui.py's add_titled()
calls; aliases come from the hand-authored search_synonyms.json. Any alias keyed
to a page title that no longer exists is reported as drift (non-fatal).
"""

import json
import re
import sys
from os import path

SCRIPT_DIR = path.dirname(path.realpath(__file__))
GUI_PY = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool/gui.py")
SYNONYMS = path.join(SCRIPT_DIR, "search_synonyms.json")
OUTPUT = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool/search_index.json")

ADD_TITLED = re.compile(r'add_titled\(\s*[A-Za-z0-9_]+\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)')


def info(msg):
    print(f"[search-index] {msg}")


def warn(msg):
    print(f"[search-index] WARN: {msg}", file=sys.stderr)


def scrape_pages():
    """Return {title: child_name} for every add_titled() call in gui.py."""
    with open(GUI_PY, encoding="utf-8") as f:
        source = f.read()
    pages = {}
    for child, title in ADD_TITLED.findall(source):
        pages[title] = child
    return pages


def load_synonyms():
    """Return {title: [keywords]} from the seed file, ignoring the _comment key."""
    with open(SYNONYMS, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def main():
    pages = scrape_pages()
    info(f"Found {len(pages)} pages in gui.py")
    synonyms = load_synonyms()

    for title in synonyms:
        if title not in pages:
            warn(f"synonym key '{title}' matches no page title in gui.py — drift, skipping")

    entries = []
    for title in sorted(pages):
        entries.append({
            "title": title,
            "child": pages[title],
            "keywords": synonyms.get(title, []),
        })

    out = {
        "_generated": "by gen-search-index.py — do not edit; edit search_synonyms.json",
        "pages": entries,
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    info(f"Wrote {len(entries)} pages to {OUTPUT}")


if __name__ == "__main__":
    main()
