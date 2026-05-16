---
name: functions_sddm.py and functions_makedir.py Stay Separate
description: Do not merge functions_sddm.py or functions_makedir.py into functions.py
type: project
originSessionId: 51fded40-8f3b-41b1-bbd6-338701f8b4cb
---
`functions_sddm.py` and `functions_makedir.py` must remain as separate files — do NOT merge them into `functions.py`.

**Why:** User decision; these files are intentionally isolated for design/scoping reasons.

**How to apply:** Skip any task that proposes merging these files. If the task list references merging them (S7, S8), mark as skipped.
