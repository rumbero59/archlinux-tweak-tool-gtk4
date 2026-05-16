---
name: Pacman Bulk Removal Pattern
description: For removing groups of related packages, use one long pacman -Rdd command instead of complex dependency management
type: feedback
originSessionId: 19dc08b8-144e-4cda-a8dc-2e7cf4d1391a
---
**Rule:** When removing multiple related packages (e.g., desktop environment + dependencies), put them all in a single `pacman -Rdd` command rather than trying to orchestrate removal order across multiple commands or with complex variable expansion.

**Why:** Attempting to remove packages in dependency order across multiple commands or with separate variable expansions creates brittle logic that fails silently. The `-Rdd` flag tells pacman to force-remove and ignore inter-package dependencies, which works perfectly when removing an entire cohesive set (e.g., plasma + all its KDE support packages).

**How to apply:**
- Build a single removal list with all packages in one place
- Use `pacman -Rdd <pkg1> <pkg2> <pkg3> ... --noconfirm` 
- Never try to manage dependency ordering across multiple pacman invocations or with complex bash variable substitution
- This approach is especially effective for desktop environments that have tight internal dependencies but are meant to be removed as a unit

**Example (from plasma removal):**
```bash
pkexec pacman -Rdd \
  signon-kwallet-extension kaccounts-integration \
  kdeclarative kdesu kded kde-inotify-survey \
  dolphin kcron khelpcenter kio-admin kio-extras kjournald ksystemlog partitionmanager \
  --noconfirm
```

This works reliably because `-Rdd` handles all the internal conflicts and dependencies in one atomic operation.
