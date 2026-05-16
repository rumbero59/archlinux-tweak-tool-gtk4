---
name: system-tab-auto-approve
description: Changes to system.py and system_gui.py are pre-approved — no confirmation needed
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 57f218af-5168-4979-83c2-4b7e1dd86241
---

For the System tab (system.py and system_gui.py), the user has pre-approved all changes. Implement directly without stating intent and waiting.

**Why:** User said "always approve for this tab" during system page coloring work (2026-05-14).

**How to apply:** When editing system.py or system_gui.py, skip the "state intent and wait for yes" step and make the change immediately. Still run flake8, commit, and push as usual.
