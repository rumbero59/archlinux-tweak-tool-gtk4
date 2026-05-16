---
name: Distro Guards Are Intentional
description: fn.distr checks throughout codebase are multi-distro support features
type: feedback
originSessionId: 2a60f01d-b4ca-4151-ad28-48141fb328d5
---
## Distro Detection Guards

Objective 11 states: "keep `fn.distr` detection guards that conditionally show/hide UI to avoid conflicts on specific systems"

These are intentional:
- **services_gui.py:482** — `if not (fn.distr == "garuda" or fn.distr == "manjaro")`
- **functions.py:683-686** — Display name mapping for all distros
- Any other `fn.distr == "..."` checks

**Why:** ATT is multi-distro. These guards allow certain features/UI elements to only show on specific distros where they're relevant or safe.

**Action:** Never remove distro guards. Keep them so ATT works correctly across all supported Arch-based systems.
