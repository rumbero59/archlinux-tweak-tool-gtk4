---
name: project-att-runs-as-root
description: ATT always runs as root via pkexec — no permission handling needed for system commands
metadata: 
  node_type: memory
  type: project
  originSessionId: 3dd62016-039a-43f0-87a0-78e5d1e66729
---

ATT always runs as root (launched via pkexec or sudo). All subprocess calls to system tools (localectl, timedatectl, pacman, systemctl, etc.) have full root permissions by default.

**Why:** The app manages system-level configuration — package installation, service management, locale/keyboard/timezone — all of which require root.

**How to apply:** Never add sudo prefixes inside ATT subprocess calls, and never add permission-error handling for "insufficient privileges" scenarios — they can't happen at runtime.
