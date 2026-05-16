---
name: hblock should run via package
description: hblock functionality should use package manager hooks, not direct subprocess calls
type: feedback
originSessionId: c816ab3a-3261-4fb1-959d-450ff91896b0
---
**Issue:** Direct subprocess calls to `/usr/bin/hblock` don't work properly in ATT GUI context

**Why:** hblock is designed to run as a pacman hook or systemd service, not as a standalone subprocess from a GUI application. Direct calls require:
- sudo privileges in GUI context
- Proper environment setup
- Integration with package system hooks

**How to apply:** When refactoring hblock functionality, consider:
- Using `pacman -S edu-hblock-git` to install, then let pacman hooks handle the database
- Or use systemctl/systemd units if hblock has associated services
- Avoid direct subprocess calls to hblock binary from GUI - it's not the intended usage pattern
- Check if there's a proper command or package hook that should be invoked instead
