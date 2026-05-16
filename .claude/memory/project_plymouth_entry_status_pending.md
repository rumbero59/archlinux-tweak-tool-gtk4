---
name: project-plymouth-entry-status-pending
description: Plymouth bootloader status split — DONE
metadata: 
  node_type: memory
  type: project
  originSessionId: b78d56e9-f049-42fb-9d83-603ba9d30ce1
---

COMPLETED. `plymouth_gui.py` already has two independent status rows:

- `hbox_sdboot_cmdline_status` / `lbl_sdboot_cmdline_status` — shows cmdline OK/Warning
- `hbox_sdboot_entries_status` / `lbl_sdboot_entries_status` — shows entries OK/Warning with count

`refresh_sdboot_status()` updates each independently. `hbox_sdboot_fix` hides when both are OK.
