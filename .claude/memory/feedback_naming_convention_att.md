---
name: Naming Convention — Use ATT not Kiro in UI Labels
description: When replacing arco/garuda refs in user-facing UI text, use "ATT" not "Kiro"
type: feedback
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
Use **ATT** (not "Kiro") when replacing distro-specific names in user-facing labels, button text, and UI strings.

**Why:** ATT is the product name and applies across all supported Arch-based distros. "Kiro" is one specific distro; using it in UI labels would be misleading on other systems.

**How to apply:** When clearing arco/garuda/endeavouros refs in `set_text()`, `set_label()`, `set_markup()`, or any visible string, replace the distro name with "ATT". Example: "Get the original ArcoLinux /etc/pacman.conf" → "Get the original ATT /etc/pacman.conf".
