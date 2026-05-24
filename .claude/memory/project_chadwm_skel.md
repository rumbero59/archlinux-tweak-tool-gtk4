---
name: chadwm skel path
description: the chadwm desktop skel folder is /etc/skel/.config/chadwm (renamed from arco-chadwm on 2026-05-24 for the Kiro de-brand)
type: project
originSessionId: 5fb4fe9c-d68b-408c-a66d-04f09c0c2778
---
The chadwm desktop config folder on disk is `/etc/skel/.config/chadwm`, copied to `~/.config/chadwm` at first login.

**History:** This was previously `arco-chadwm` and was once locked as "never rename." That decision was deliberately reversed on 2026-05-24: the folder was renamed to `chadwm` for the new Kiro release de-brand, with all references updated in the same change set (edu-chadwm runtime scripts + ATT `desktopr.py` desktop installer + the `npicom` shell aliases).

**Why:** `arco-chadwm` carried the ArcoLinux brand, which Kiro is removing. The rename was safe because the runtime chain (`chadwm.desktop` → `/usr/bin/exec-chadwm` → `run.sh`) references the path only by name and nothing is hardcoded in the compiled chadwm C source.

**How to apply:**
- The current folder name is `/etc/skel/.config/chadwm` — reference it exactly.
- `desktopr.py` copies this path when installing the chadwm desktop (source repo: edu-chadwm at /home/erik/EDU/edu-chadwm).
- Do not reintroduce `arco-chadwm`. A stale `arco-chadwm` reference anywhere is a leftover to fix, not a path to preserve.
- Real AUR package names like `arcolinux-arc-*` are a separate case — those stay (see [[project_arcolinux_arc_themes]]).
