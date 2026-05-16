---
name: Never block GTK main thread with subprocess.call for terminal commands
description: All alacritty terminal launches must use Popen in a daemon thread via _run_terminal; never subprocess.call which freezes ATT
type: feedback
originSessionId: de7c78ac-8b02-4fd8-93ac-79bc8496be87
---
Never use `fn.subprocess.call()` or `subprocess.call()` to launch alacritty terminal windows from GUI callbacks. `call()` blocks the GTK main thread, freezing the entire ATT window while the terminal is open.

**Why:** The user discovered this when maintenance callbacks froze ATT during system update, cache clean, mirror operations, etc.

**How to apply:** Use the `_run_terminal(self, cmd, done_msg, start_msg=None)` helper in maintenance.py (or the equivalent daemon-thread pattern in other modules). `Popen().wait()` runs in a background thread; `GLib.idle_add` fires the notification back on the GTK thread when the terminal closes. Exception: `subprocess.call()` is acceptable for non-terminal background operations (e.g. wget downloads) where subsequent code depends on the result.
