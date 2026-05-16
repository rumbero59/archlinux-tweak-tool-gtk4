---
name: GTK Pango markup ampersand escaping
description: The & character must be escaped as &amp; in GTK set_markup() calls or the label silently fails to render
type: feedback
originSessionId: 09521d1d-2ba7-4595-ab63-4e345e975295
---
Always escape `&` as `&amp;` in any `set_markup()` call in GTK/Pango markup.

**Why:** A bare `&` in Pango markup causes the parser to fail silently — the label renders nothing with no error message. This has happened twice in this project (network_gui.py section titles).

**How to apply:** Any time a label text contains `&` (e.g. "Network & Tracking"), use `&amp;` instead: `"<b>Network &amp; Tracking Protection</b>"`. Applies to all `set_markup()` calls throughout the codebase.
