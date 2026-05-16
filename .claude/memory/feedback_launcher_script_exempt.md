---
name: Launcher Script ATT Standard Exempt
description: usr/bin/archlinux-tweak-tool must NEVER be made ATT Script Standard compliant
type: feedback
originSessionId: 9a3d3b0b-1e68-4a21-b649-2b1599868bde
---
`usr/bin/archlinux-tweak-tool` is explicitly exempt from the ATT Script Standard.

**Why:** User's explicit instruction — this is the system launcher script and must remain in its current plain bash style. Do not add tput colors, helper functions, set -euo pipefail, or any ATT Script Standard structure to it.

**How to apply:** When touching this file for any reason (e.g. Wayland/Hyprland fixes), make only the targeted change. Never bring it into ATT Script Standard compliance, even partially.
