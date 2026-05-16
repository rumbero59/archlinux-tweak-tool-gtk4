---
name: no-repeat-tips-in-best-practices-md
description: Tips written to best_practices.md only at end-of-day session close; never mid-session; always check for duplicates first
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 799e33f4-016c-482a-9e06-616a3dacf1be
---

Tips are written to ~/.claude/best_practices.md **only when the user explicitly says "close shop"** — not on "write all changes away" or any other wrap-up signal. Never write tips mid-session or during regular end-of-task commits.

Before writing, read the file and verify each tip is not already present (same concept, even if worded differently).

**Why:** "Write all changes away" = commit docs/changelog. "Close shop" = true end-of-day signal that includes tips. The two are distinct; treat them differently.

**How to apply:** Hold tip candidates until the user says "close shop". Then read best_practices.md, check concepts, write only genuinely new tips.
