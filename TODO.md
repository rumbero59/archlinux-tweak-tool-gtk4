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

## Backlog / Unscheduled

- [ ] **Research leftwm theme and picom.conf** — investigate how leftwm theming works and how picom.conf integrates with it
- [ ] **GParted launcher** — add a button to launch gparted if installed (`shutil.which("gparted")`); decide which page it belongs on (Maintenance or a dedicated Disks section); button should be hidden/insensitive when gparted is not installed
- [ ] **Keep checking Bazaar works** — ongoing verification that Bazaar launches and functions correctly across distros

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
