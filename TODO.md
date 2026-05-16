# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Alacritty Tweak Tool

- [x] **Colorful console logs** — add colored log helpers (section/info/success/warn/error) matching ATT's `fn.log_*` style so console output is readable at a glance
- [x] **Startup timing + `--debug` flag** — record wall-clock time at key init stages; add `--debug` CLI flag (like ATT) that prints each timing measurement to console and shows total startup time at launch
- [ ] **Move to its own project** — extract `usr/share/alacritty-tweak-tool/` into a standalone repo at `/home/erik/EDU/alacritty-tweak-tool` with its own git history

---

## Backlog / Unscheduled

- [ ] **Research leftwm theme and picom.conf** — investigate how leftwm theming works and how picom.conf integrates with it
- [ ] **GParted launcher** — add a button to launch gparted if installed (`shutil.which("gparted")`); decide which page it belongs on (Maintenance or a dedicated Disks section); button should be hidden/insensitive when gparted is not installed
- [ ] **Keep checking Bazaar works** — ongoing verification that Bazaar launches and functions correctly across distros

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
