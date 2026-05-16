---
name: Console Output Standard Template
description: Standard format for all console messages and user feedback throughout ATT
type: feedback
originSessionId: c816ab3a-3261-4fb1-959d-450ff91896b0
---
# Console Output Standard Template

## Established Pattern

This is the approved standard for ALL user-facing console messages in ArchLinux Tweak Tool.

### Without `--debug` (Normal User Experience)
```
════════════════════════════════════════════════════════════════════════════
Installing yay-git...
════════════════════════════════════════════════════════════════════════════

════════════════════════════════════════════════════════════════════════════
yay-git installed successfully
════════════════════════════════════════════════════════════════════════════
```

### With `--debug` (Troubleshooting/Developer Mode)
```
════════════════════════════════════════════════════════════════════════════
Installing yay-git...
════════════════════════════════════════════════════════════════════════════

[DEBUG] Binary path: /usr/bin/yay
[DEBUG] Waiting for process to complete...
[DEBUG] Reading temp file: /tmp/tmp1pputt24.log
[DEBUG] Temp file contents: 622 bytes

════════════════════════════════════════════════════════════════════════════
yay-git installed successfully
════════════════════════════════════════════════════════════════════════════
```

## Key Characteristics

- **Action start**: `fn.log_subsection("Installing yay-git...")` - shows action with colored separators
- **Debug info**: Only appears with `--debug` flag via `fn.debug_print()`
- **Result**: `fn.log_success("yay-git installed successfully")` - confirms completion
- **Clean**: No spam, no unnecessary output
- **Professional**: Colored, organized, easy to read
- **Consistent**: Same format for all operations (install/remove/configure/etc.)

## Application Scope

Apply this template to ALL user-facing operations:
- ✓ Package installations/removals (SOFTWARE, AI TOOLS)
- ✓ System configurations (SDDM, themes, etc.)
- ✓ Feature toggles
- ✓ Any action with status feedback
- ✓ Error/warning messages

## Implementation in Code

```python
# Start operation
fn.log_subsection(f"Installing {package}...")

# Optional: debug details (only shown with --debug)
fn.debug_print(f"Binary path: {path}")
fn.debug_print(f"Processing...")

# End result
fn.log_success(f"{package} installed successfully")
```

## Alternative Messages

**For errors/warnings:**
```python
fn.log_warn("Installation may have failed or encountered issues")
fn.log_error("Critical error message here")
```

**For other operations:**
```python
fn.log_section("Major operation header")  # GREEN separators
fn.log_subsection("Minor operation")      # CYAN separators
fn.info("Simple info (no separators)")
fn.warn("Simple warning (no separators)")
fn.error("Simple error (no separators)")
```

## Why:** Clean UX for normal users, detailed debugging when needed. No clutter.
