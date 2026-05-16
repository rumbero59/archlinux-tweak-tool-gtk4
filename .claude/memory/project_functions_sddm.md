---
name: functions_sddm.py Design Intent
description: setup_sddm_config must only run on user action from the SDDM page, never at startup
type: project
originSessionId: 26646806-84f4-4ce4-8348-8e659e1f2d6c
---
`functions_sddm.py` contains `setup_sddm_config()` which checks/creates SDDM config files.

It must stay as a separate file — do NOT merge into functions.py.

**Why:** Running it at startup is too invasive — it modifies system files (SDDM config) before the user has decided anything about SDDM. Violates the Non-Invasive objective.

**How to apply:** Only call `setup_sddm_config()` when the user takes an explicit action on the SDDM page (e.g. saving settings). Import `functions_sddm` in `sddm.py` or `sddm_gui.py`, not in `archlinux-tweak-tool.py`. Never wire it into the startup flow.
