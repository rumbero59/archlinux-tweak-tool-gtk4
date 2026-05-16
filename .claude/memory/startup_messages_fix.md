---
name: Startup Message Suppression - Initialization Flag Timing
description: Fixed double initialization of switches causing logging messages during startup
type: feedback
originSessionId: c816ab3a-3261-4fb1-959d-450ff91896b0
---
## Problem
Repository toggle and autologin messages were appearing during startup despite having initializing flag checks in callback functions.

## Root Cause
Switches were being initialized TWICE:
1. **Synchronously in archlinux-tweak-tool.py** (lines 296-307) - called immediately after GLib.idle_add()
2. **Asynchronously in functions_startup.init_switch_states()** - scheduled with GLib.idle_add() but runs later

The first set of `set_active()` calls triggered signal handlers BEFORE the `initializing` flag was ever set, so the handlers couldn't suppress their logging.

## Solution
**Why:** GTK signal handlers for switch changes must be guarded by an `initializing` flag that's set BEFORE any switch state changes occur.

**How to apply:** When initializing UI switches:
1. Set `self.initializing = True` at the start of switch initialization
2. Make all `set_active()` calls while the flag is True
3. Ensure ALL signal handlers check: `if hasattr(self, 'initializing') and self.initializing: return`
4. Clear the flag at the END of all initialization: `self.initializing = False`

## Specific Fix Applied
Added `self.initializing = True` in archlinux-tweak-tool.py (line 281) **before** the check_repo() and set_active() calls, so the first batch of switch initialization happens with the flag set.

## Functions Protected
- pacman.py: all on_*_toggle functions (nemesis, chaotic, pacman1-7)
- pacman_functions.py: toggle_test_repos(), append_repo()
- sddm.py: on_autologin_sddm_activated()

Result: Startup now displays only "[INFO] Total startup time:" without repo/autologin config messages.
