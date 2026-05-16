---
name: Critical Bug - Orphan Removal and Network Discovery Interaction
description: pacman -Rns $(pacman -Qdtq) removes packages too aggressively, especially after uninstalling network discovery
type: project
originSessionId: ccb87572-1bec-460b-8ec1-cdf56da52796
---
## The Bug Chain

**Commit b0c1deb** (2026-04-15): Added "Clear orphans" feature that runs:
```bash
sudo pacman -Rns $(pacman -Qdtq)
```

The problem:
- `pacman -Qdtq` lists all "unneeded" packages (installed as dependencies, no longer needed)
- `-Rs` removes packages AND their dependencies **without confirmation**
- No safeguards for corrupted databases or mis-identified orphans

**Connection to network discovery**: When you uninstall network discovery (avahi, nss-mdns, gvfs-smb via `remove_discovery()` in functions.py:2088), it removes those packages with `pacman -Rs` which marks other packages as orphaned. If the user then runs "Clear orphans", the cascade of dependency removals can be catastrophic.

**Result**: On a real machine, this deleted most/all system packages and user code because:
1. The orphan detection misidentified packages as unneeded
2. The aggressive dependency removal cascaded
3. No confirmation required before massive deletion

**Fix Applied (2026-04-27)**: Completely removed the "Clear orphans" feature
- Removed hbox24 GUI element from maintenance_gui.py
- Removed on_click_clear_orphans() handler from archlinux-tweak-tool.py
- No remaining references to the feature

This was the safest solution since pacman orphan detection is not reliable enough for automatic removal.

**Commits involved**:
- b0c1deb: Clear orphans feature added (2026-04-15) — now removed
- 2969731: Remove pacman lock feature (related, still safe)
- functions.py line 2088: remove_discovery() function (still active but safe)

Why: Convenience feature for system cleanup without realizing the destructive potential
