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

## Fastfetch Page

- [ ] **Enable toggle reverts when fastfetch not installed** — if the user clicks the enable switch but `fastfetch` is not installed, the switch must snap back to off and show a notification "fastfetch is not installed — install it first"; currently the toggle stays on even though nothing was enabled

---

## Performance Page

- [ ] **tuned / tuned-ppd buttons stay greyed out after install on Arch** — installing `tuned` or `tuned-ppd` via ATT on a plain Arch system leaves the enable/configure buttons permanently greyed out; the UI does not refresh installed state after the terminal closes; apply the `wait_and_refresh` pattern so button sensitivity is re-evaluated once the alacritty terminal exits
- [ ] **irqbalance enable/disable buttons unresponsive after install** — after installing `irqbalance` via ATT the enable and disable buttons cannot be clicked; same root cause as tuned — UI does not refresh sensitivity after the terminal closes; apply `wait_and_refresh` so buttons become active once install completes
- [ ] **gamemode: show "Installed" label + unblock enable buttons after install** — after installing `gamemode` via ATT, (1) an "Installed" label must appear next to the package row and (2) the enable/disable buttons must become clickable; both stay in their pre-install state because the UI does not refresh after the terminal closes; apply `wait_and_refresh` so label and button sensitivity are re-evaluated once `check_package_installed("gamemode")` returns true
- [ ] **ananicy false install notification + console log** — both the notification bar and the console log (`log_*`) show an installation message even when ananicy was not installed; the log calls fire unconditionally before checking install state; guard both the notification and all `log_success`/`log_info` calls so they only fire after confirming the package is actually present post-install

---

## SDDM Page

- [ ] **URGENT: remove install/enable option for plasma-login-manager** — the SDDM tab must not offer to install or enable `plasma-login-manager`; this package replaces SDDM on KDE Plasma systems and would break the SDDM tab's own guard (`check_service_enabled("plasma-login")`); remove the UI row and any backing code entirely

---

## hblock Page

- [ ] **hblock enable fails on pure Arch** — on a plain Arch system, hblock installs successfully but the enable button does nothing (or silently fails); investigate why enable is blocked on pure Arch (missing hook, missing systemd unit, repo dependency?) and either fix the enable path or show a clear message explaining what the user must do first

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
