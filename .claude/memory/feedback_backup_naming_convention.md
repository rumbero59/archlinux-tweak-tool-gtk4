---
name: ATT Backup Naming Convention
description: Official ATT backup suffix is -bak (hyphen), not .bak (dot); home-folder backups must call fn.permissions() after creation
type: feedback
originSessionId: 26a70424-e320-47fd-ae6f-8cd675961183
---
ATT backup files and directories use the `-bak` suffix (hyphen), not `.bak` (dot extension). Example: `variety.conf-bak`, `scripts-bak/`.

**Why:** User confirmed this as the official convention. The startup banner in archlinux-tweak-tool.py also documents "(-bak extension)".

**How to apply:** When creating any backup in ATT — never use `.bak`; always use `-bak`. Additionally, any backup created inside the user's home directory (e.g. `~/.config/variety/`) must call `fn.permissions(backup_path)` immediately after creation so ownership is set back to the real user (not root). System-file backups (e.g. `/etc/pacman.conf-bak`) do not need `fn.permissions()`.
