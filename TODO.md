# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Backlog / Unscheduled

- [ ] **Research leftwm theme and picom.conf** — investigate how leftwm theming works and how picom.conf integrates with it
- [ ] **GParted launcher** — add a button to launch gparted if installed (`shutil.which("gparted")`); decide which page it belongs on (Maintenance or a dedicated Disks section); button should be hidden/insensitive when gparted is not installed
- [ ] **Keep checking Bazaar works** — ongoing verification that Bazaar launches and functions correctly across distros
- [ ] **Skel page** — new page to copy files/folders from `/etc/skel/` to the user's home (and vice versa); buttons to copy individual entries or sync entire skel; useful for re-applying default configs to existing users
- [ ] **kiro-diag page in ATT** — new diagnostic page similar to the User page; displays ISO version (`/etc/dev-rel`), BIOS/UEFI mode, mounted filesystems, active display manager, X11/Wayland sessions, installed kernels, running kernel, and NVIDIA driver/package status; all read-only info rendered as GTK labels; source: `/home/erik/EDU/edu-system-files/usr/local/bin/kiro-diag`
- [ ] **List user systemd services** — add a section (Services page or new tab) that lists the current user's systemd units (`systemctl --user list-units`); show name, description, and active/enabled state; read-only info panel so users can see what is running in their user session without opening a terminal
- [ ] **Verify Support page** — launch ATT and confirm the new Support page renders (orange header, 5 funding rows) and each Open button opens the correct URL in the user's browser via `sudo -u … xdg-open`

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
