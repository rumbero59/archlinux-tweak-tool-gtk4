# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Backlog / Unscheduled

_P1 = urgent / bug / security / release; P2 = backlog. **One P1 bug open (2026-05-27)** — listed first; all other items are P2._

- [ ] **P1 bug — Desktop install: "Making backup" yellow text seems to do nothing** — _added 2026-05-27._ On the Desktop page, after choosing a desktop and clicking Install, a yellow warning label reading "Making backup" appears but seems to do nothing — no visible backup results. Investigate whether the backup step actually executes or the label is shown without its action firing. Likely candidates: [desktopr_gui.py](usr/share/archlinux-tweak-tool/desktopr_gui.py), [desktopr.py](usr/share/archlinux-tweak-tool/desktopr.py), and the GTK-config backup in [functions_backup.py](usr/share/archlinux-tweak-tool/functions_backup.py). Confirm what the backup should capture and where it writes; if it runs, surface the output path (transparency objective 14); if it's informational only, reword so it doesn't imply an action. Add a verification hook (ATT DEV section) when fixed, per the testcase rule.
- [ ] **`fetch-configs.sh` — pull MIRROR configs fresh at sync time** — implement the fetch step from the config-source audit (2026-05-25). Reads [data-sources.tsv](data-sources.tsv) (9 MIRROR files), wgets each from GitHub raw `main` into `data/`, wired into `up.sh` before commit so upstream drift is captured. Standard EDU bash template. Source-of-truth then lives in the source repos (edu-shells / edu-dot-files / kiro-iso / edu-variety-config), not ATT's copies. See [CONFIG_SOURCES.md](CONFIG_SOURCES.md). Note: sddm + nanorc sources live in kiro-iso (different repo layout than the edu-* skel paths).
- [ ] **Research leftwm theme and picom.conf** — investigate how leftwm theming works and how picom.conf integrates with it
- [ ] **GParted launcher** — add a button to launch gparted if installed (`shutil.which("gparted")`); decide which page it belongs on (Maintenance or a dedicated Disks section); button should be hidden/insensitive when gparted is not installed
- [ ] **Keep checking Bazaar works** — ongoing verification that Bazaar launches and functions correctly across distros
- [ ] **Skel page** — new page to copy files/folders from `/etc/skel/` to the user's home (and vice versa); buttons to copy individual entries or sync entire skel; useful for re-applying default configs to existing users
- [ ] **List user systemd services (on the Dev page)** — add a Dev-page section listing the current user's systemd units (`systemctl --user list-units`); show name, description, and active/enabled state; read-only. _Folded onto the Dev page 2026-05-25; the separate-page idea was dropped — the Dev page already absorbed the old "kiro-diag page in ATT" diagnostics item._
- [ ] **Enable `reflector.timer`** — reflector is installed but its timer is disabled; add a toggle/button (likely Maintenance or Pacman page) to enable `reflector.timer` so mirrors stay fresh/fast, reducing partial-update and slow-mirror issues

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
