---
name: ATT Multi-Distro Scope
description: ATT targets all Arch-based systems, not just Kiro — distro detection guards are intentional
type: project
originSessionId: 26646806-84f4-4ce4-8348-8e659e1f2d6c
---
ATT is designed to run on all Arch-based systems (Kiro, Artix, Manjaro, etc.). `fn.distr` checks that conditionally show/hide UI are intentional — they prevent features from appearing on distros where they would clash.

**Why:** The tool is not Kiro-exclusive. Removing distro guards would break functionality on other supported distros.

**How to apply:** When encountering `fn.distr == "garuda"` or similar guards, do NOT remove them blindly. ATT is installed and used on Garuda — some UI must still be hidden there. Only remove references to Garuda/EndeavourOS *repos and packages* (since ATT no longer ships those). Keep ALL `fn.distr` guards including Garuda and Manjaro — they hide UI that would clash on those distros. Never touch a `fn.distr` conditional without explicit user instruction.

**Test order:** Kiro first (user's own distro, primary test machine), then Arch Linux, then any other Arch-based distro (Garuda, CachyOS, Manjaro, etc.). "Test on Kiro" does not mean Kiro-only — it means Kiro is first in line. Never call ATT "Kiro-focused."
