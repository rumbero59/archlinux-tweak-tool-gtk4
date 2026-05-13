# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Kernel Page

- [ ] **Garuda: dracut support** — Garuda uses dracut instead of mkinitcpio; kernel tab must detect which initramfs tool is active and show the correct rebuild command; guard with binary presence check (`shutil.which("dracut")`)

---

## Plymouth Page

- [ ] **Garuda: dracut integration** — Plymouth on Garuda requires `dracut` hooks, not `mkinitcpio` hooks; the "add to HOOKS" section and rebuild button must branch on detected initramfs tool; dracut variant runs `dracut --force` instead of `mkinitcpio -P`

---

## Button Messaging Audit

- [ ] **Test all buttons — notification bar + console log on pure Arch** — go through every tab and click every button; verify (1) the in-app notification bar shows a meaningful message, (2) the console log (`log_*`) reflects the action; on pure Arch (no chaotic-AUR / nemesis repo), any button that requires a repo the user has not enabled must communicate this clearly — e.g. "Enable chaotic-AUR first" — rather than silently failing or showing a cryptic error

---

## Backlog / Unscheduled

- [ ] **XFCE wallpaper D-Bus** — `xfconf-query` runs as real user via `sudo -u` + D-Bus env (S11 marked solved in code) but not confirmed working on a real XFCE session; needs live test
- [ ] **Bazaar tab** — currently behind `--dev` flag; needs design decision before making public
- [ ] **Bazaar on pure Arch** — verify Bazaar launches and functions correctly on a plain Arch Linux system (no chaotic-AUR, no nemesis repo); identify any repo-gated dependencies that silently fail

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
