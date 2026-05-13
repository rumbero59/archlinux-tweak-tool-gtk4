# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Kernel Page

- [ ] **Garuda: dracut support** — Garuda uses dracut instead of mkinitcpio; kernel tab must detect which initramfs tool is active and show the correct rebuild command; guard with binary presence check (`shutil.which("dracut")`)

---

## Plymouth Page

- [ ] **Garuda: dracut integration** — Plymouth on Garuda requires `dracut` hooks, not `mkinitcpio` hooks; the "add to HOOKS" section and rebuild button must branch on detected initramfs tool; dracut variant runs `dracut --force` instead of `mkinitcpio -P`
- [ ] **Split bootloader status into two rows** — `plymouth_gui.py`: replace single `lbl_sdboot_status` with two rows: (1) cmdline row "OK: /etc/kernel/cmdline contains quiet splash" (2) entries row "OK: all entries contain quiet splash"; update `refresh_sdboot_status()` to set each independently; GRUB/limine/rEFInd keep single row

---

## Logging Page

- [ ] **Journalctl-style log viewer** — `logging_gui.py` / `log_callbacks.py` exist but the feature needs fleshing out; goal is an in-app viewer similar to `journalctl` — filterable by unit, priority, time range; output rendered in a scrollable text view; consider `journalctl -f` streaming mode via a background thread + `GLib.idle_add`

---

## Main Entry Point (`archlinux-tweak-tool.py`)

- [ ] **Deduplicate GTK_THEME parsing** — `/etc/environment` parsing block is duplicated verbatim in `Main.__init__` (~lines 77–95) and `ATTApplication.on_activate` (~lines 384–394); extract to a single helper in `functions.py`
- [ ] **Thread the background init file I/O** — `_finish_background_init` runs backup file operations on the GTK main thread and can freeze the UI; move to a daemon thread with `GLib.idle_add` for any UI updates after

---

## Software Page

- [ ] **Bazaar launch under pkexec** — partially fixed (2026-05-08): `get_terminal_env()` now passes Wayland vars, works on some machines; still needs further diagnosis on machines where it still fails

---

## New Scripts

- [ ] **get-chadwm-on-att** — script to install/configure chadwm via ATT
- [ ] **get-ohmychadwm-on-att** — script to install/configure ohmychadwm via ATT (pair with get-chadwm-on-att)

---

## Scripts Audit

- [ ] **Audit data/bin/ script usage** — grep all Python source files for calls into `data/bin/`; identify any scripts in that directory that are not called from anywhere in the codebase; decide whether to keep, remove, or wire them up

---

## ~/.config/archlinux-tweak-tool/ Cleanup

- [ ] **Termite settings.ini leftover** — `~/.config/archlinux-tweak-tool/settings.ini` appears to contain termite config written by an old arco-era ATT version; the word "termite" does not appear anywhere in the current codebase; audit what ATT currently writes to that file vs what is there on disk, and decide whether to remove the stale content or add a startup cleanup

---

## Button Messaging Audit

- [ ] **Test all buttons — notification bar + console log on pure Arch** — go through every tab and click every button; verify (1) the in-app notification bar shows a meaningful message, (2) the console log (`log_*`) reflects the action; on pure Arch (no chaotic-AUR / nemesis repo), any button that requires a repo the user has not enabled must communicate this clearly — e.g. "Enable chaotic-AUR first" — rather than silently failing or showing a cryptic error

---

## Backlog / Unscheduled

- [ ] **Font looks strange** — user flagged it; only CSS file is `icons.css`; sidebar labels have `font-size: 14px; font-weight: 500`; ask which area looks off (sidebar, titles, log, whole app) before touching
- [ ] **XFCE wallpaper D-Bus** — `xfconf-query` runs as real user via `sudo -u` + D-Bus env (S11 marked solved in code) but not confirmed working on a real XFCE session; needs live test
- [x] **Dead `lolcat_toggle()` / `util_toggle()`** — removed; `utilities.py` deleted; `get_config_file()` moved to `functions.py`
- [ ] **Bazaar tab** — currently behind `--dev` flag; needs design decision before making public

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
