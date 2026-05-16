---
name: Simplify Session 2026-05-05 — main entry point cleanup
description: Bugs fixed and dead code removed in archlinux-tweak-tool.py; two larger issues flagged but deferred
type: project
originSessionId: a449de76-147b-4620-a766-2c9399d4c95c
---
Session ran /simplify on archlinux-tweak-tool.py (no git diff, reviewed open file directly).

**Bug fixed:** `check_if_process_is_running(int(pid))` at the lock-file guard — function compares process name strings, so passing an int (PID) always returned False. Added `fn.check_pid_is_running(pid: int)` to functions.py using `psutil.pid_exists()`.

**Dead code removed from archlinux-tweak-tool.py:**
- `call = None` global + `from subprocess import call as _call` import + `call = _call` assignment — never used, forbidden by project rules
- `pmf = None` global + `pmf = pacman_functions` assignment — never used in this file (functions_startup.py has its own local import)
- `self.label7` init in `__init__` — immediately overwritten by privacy_gui.py:128
- `self.fb` and `self.flowbox_wall` FlowBox allocations — never referenced anywhere
- Stale module-list comment block, redundant inline comments, bare `return` at end of `__init__`
- `on_refresh_att_clicked(self, desktop)` → `(self, _widget)` per project convention

**Two issues flagged, not yet fixed (need plan mode or user confirmation):**
1. GTK_THEME / `/etc/environment` parsing duplicated verbatim in `Main.__init__` (lines ~77–95) and `ATTApplication.on_activate` (lines ~384–394) — extract to helper
2. `_finish_background_init` runs backup functions (file I/O) on the GTK main thread — can freeze UI; needs threading refactor

**Why:** Fast, clean entry point is a project goal; threading refactor needs plan mode before touching.
**How to apply:** When next touching archlinux-tweak-tool.py, start with the GTK_THEME deduplication or the threading issue.
