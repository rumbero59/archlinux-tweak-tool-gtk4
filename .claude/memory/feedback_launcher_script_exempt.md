---
name: launcher-script-att-standard-exempt
description: usr/bin/archlinux-tweak-tool and setup.sh are permanently frozen — never edit them
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b8c22086-6439-4a2c-a014-60af0b54d3e7
---

Two files are permanently off-limits for unsolicited changes:

- `usr/bin/archlinux-tweak-tool` — system launcher script
- `setup.sh` — project setup script

**Why:** User's explicit instruction. Both must remain exactly as-is. Do not apply ATT Script Standard, refactor, rename variables, or make any edit unless the user explicitly names the file and the change in the same message.

**How to apply:** If a task touches more than 2 files and these are nearby, skip them. If a linter or pattern sweep would naturally include them, stop at the file boundary. Only act on a direct, file-specific instruction from the user.
