#!/usr/bin/env python3
"""Generate search_index.json from the ATT GUI source + search_synonyms.json.

Run automatically by up.sh. For every page it records three things:

  * title    — scraped from gui.py's add_titled() calls (matched live by the app too)
  * keywords — hand-authored aliases from search_synonyms.json
  * labels   — button/label/markup text scraped from that page's *_gui module,
               so a control is findable by what it actually says on screen

The module->page link is derived from gui.py: each `<module>.gui(... vboxstack_x ...)`
call is tied to the `add_titled(vboxstack_x, "child", "Title")` that ships it.
Aliases keyed to a page title that no longer exists are reported as drift (non-fatal).
"""

import json
import re
import sys
from os import path

SCRIPT_DIR = path.dirname(path.realpath(__file__))
APP_DIR = path.join(SCRIPT_DIR, "usr/share/archlinux-tweak-tool")
GUI_PY = path.join(APP_DIR, "gui.py")
SYNONYMS = path.join(SCRIPT_DIR, "search_synonyms.json")
OUTPUT = path.join(APP_DIR, "search_index.json")

ADD_TITLED = re.compile(r'add_titled\(\s*([A-Za-z0-9_]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)')
MODULE_CALL = re.compile(r'([a-z_]+)\.gui\([^)]*?(vboxstack[A-Za-z0-9_]*)')
LABEL_TEXT = re.compile(r'(?:set_text|set_label|set_markup)\(\s*["\']([^"\']+)["\']')
LABEL_KWARG = re.compile(r'label\s*=\s*["\']([^"\']+)["\']')
MARKUP_TAG = re.compile(r"<[^>]+>")
WORD = re.compile(r"[a-z0-9]+")

# Generic UI verbs and English function words — present on nearly every page,
# so they carry no signal about WHICH page owns a control.
STOPWORDS = {
    "the", "and", "with", "for", "your", "you", "this", "that", "from", "into",
    "are", "was", "will", "not", "have", "has", "its", "out", "off", "all", "any",
    "use", "used", "via", "per", "page", "tab",
    "view", "install", "installed", "installing", "uninstall", "remove", "removed",
    "enable", "enabled", "disable", "disabled", "apply", "applied", "reset",
    "open", "close", "click", "set", "get", "show", "hide", "save", "edit",
    "current", "currently", "select", "selected", "please", "note",
}


def info(msg):
    print(f"[search-index] {msg}")


def warn(msg):
    print(f"[search-index] WARN: {msg}", file=sys.stderr)


def parse_gui():
    """Return (var_to_page, module_to_var) parsed from gui.py.

    var_to_page maps a vboxstack variable to {"child", "title"}; module_to_var
    maps a *_gui module name to the vboxstack variable it builds into.
    """
    with open(GUI_PY, encoding="utf-8") as f:
        source = f.read()
    var_to_page = {var: {"child": child, "title": title} for var, child, title in ADD_TITLED.findall(source)}
    module_to_var = {module: var for module, var in MODULE_CALL.findall(source)}
    return var_to_page, module_to_var


def load_synonyms():
    """Return {title: [keywords]} from the seed file, ignoring underscore keys."""
    with open(SYNONYMS, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def scrape_labels(module):
    """Return the set of meaningful word tokens in a module's button/label text."""
    module_path = path.join(APP_DIR, f"{module}.py")
    if not path.isfile(module_path):
        return set()
    with open(module_path, encoding="utf-8") as f:
        source = f.read()
    tokens = set()
    for raw in LABEL_TEXT.findall(source) + LABEL_KWARG.findall(source):
        clean = MARKUP_TAG.sub(" ", raw)
        for word in WORD.findall(clean.lower()):
            if len(word) >= 3 and not word.isdigit() and word not in STOPWORDS:
                tokens.add(word)
    return tokens


def main():
    var_to_page, module_to_var = parse_gui()
    info(f"Found {len(var_to_page)} pages, {len(module_to_var)} GUI modules in gui.py")
    synonyms = load_synonyms()

    titles = {page["title"] for page in var_to_page.values()}
    for title in synonyms:
        if title not in titles:
            warn(f"synonym key '{title}' matches no page title in gui.py — drift, skipping")

    # child -> scraped label tokens, accumulated across that page's module(s)
    labels_by_child = {}
    for module, var in module_to_var.items():
        page = var_to_page.get(var)
        if page is None:
            continue
        labels_by_child.setdefault(page["child"], set()).update(scrape_labels(module))

    entries = []
    for page in sorted(var_to_page.values(), key=lambda p: p["title"]):
        keywords = synonyms.get(page["title"], [])
        labels = sorted(labels_by_child.get(page["child"], set()) - {k.lower() for k in keywords})
        entries.append({
            "title": page["title"],
            "child": page["child"],
            "keywords": keywords,
            "labels": labels,
        })

    out = {
        "_generated": "by gen-search-index.py — do not edit; edit search_synonyms.json",
        "pages": entries,
    }
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    total_labels = sum(len(e["labels"]) for e in entries)
    info(f"Wrote {len(entries)} pages, {total_labels} scraped label tokens to {OUTPUT}")


if __name__ == "__main__":
    main()
