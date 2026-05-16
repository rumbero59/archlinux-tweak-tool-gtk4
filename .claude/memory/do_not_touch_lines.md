---
name: Lines to Never Modify
description: Specific line ranges in archlinux-tweak-tool.py that should not be touched
type: feedback
originSessionId: 621b79f3-a0fa-454b-9903-7b0ae4fad7ca
---
## archlinux-tweak-tool.py - Do NOT Modify

**Lines 76-104**: Distro support list in debug output
- Contains references to all distros ATT runs on (Arch, EndeavourOS, Garuda, ArcoLinux, etc.)
- This list is intentional and should remain as-is
- Do not remove or modify distro references in this section

**Why:** These lines document all supported Arch-based distributions. Even though Kiro is the primary focus, ATT is designed to work on these other distros too. Removing them would be misleading.

## functions.py - Do NOT Modify

**`change_distro_label()` (line ~681)**: Maps internal distro IDs to display names (e.g. "garuda" → "Garuda", "endeavouros" → "EndeavourOS")
- ATT runs on many Arch-based distros; this function exists purely to show a nice name in the UI
- Never remove or modify any distro entry — even distros not actively targeted still deserve a readable label
- Removing an entry here would show a raw lowercase ID to users on that distro
