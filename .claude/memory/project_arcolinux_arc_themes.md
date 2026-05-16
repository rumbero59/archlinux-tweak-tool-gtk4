---
name: arcolinux-arc-* theme names are untouchable
description: arcolinux-arc-* package names in themes.py and themes_gui.py are real AUR package names — do not rename or remove
type: project
originSessionId: 5fb4fe9c-d68b-408c-a66d-04f09c0c2778
---
**CRITICAL: These are REAL AUR PACKAGE NAMES. They MUST STAY UNCHANGED.**

All `arcolinux-arc-*` references (157+ instances) in `themes.py` and `themes_gui.py` are the actual upstream AUR package names for GTK themes:
- `arcolinux-arc-aqua-git`
- `arcolinux-arc-azul-git`
- `arcolinux-arc-blue-sky-git`
- ... (54 total arcolinux-arc-* packages)

**Why:** These are upstream package names on AUR. Renaming them breaks installation. They work on any Arch-based system regardless of distro. They are NOT brand references.

**How to apply:** 
- L1 (themes_gui.py, 109 refs) — **SKIP ENTIRELY** (all real package names)
- L2 (themes.py, 547 refs) — **SKIP ENTIRELY** (all real package names)
- Never suggest grepping/replacing these
- When user asks about them, remind: "These are real AUR packages, we keep them"
