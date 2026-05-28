# ATT — To-Do List

Tasks that are known but not yet scheduled into a milestone.
Add new items here; move to CLAUDE.md milestones when scheduled.

---

## Backlog / Unscheduled

_P1 = urgent / bug / security / release; P2 = backlog. **One P1 bug open (2026-05-27)** — listed first; all other items are P2._

- [x] **P1 bug — Desktop install: "Making backup" yellow text seems to do nothing** — _added 2026-05-27; done 2026-05-27._ Resolved the Desktop-page "Making backup" label that appeared without visible results.
- [ ] **`fetch-configs.sh` — pull MIRROR configs fresh at sync time** — implement the fetch step from the config-source audit (2026-05-25). Reads [data-sources.tsv](data-sources.tsv) (9 MIRROR files), wgets each from GitHub raw `main` into `data/`, wired into `up.sh` before commit so upstream drift is captured. Standard EDU bash template. Source-of-truth then lives in the source repos (edu-shells / edu-dot-files / kiro-iso / edu-variety-config), not ATT's copies. See [CONFIG_SOURCES.md](CONFIG_SOURCES.md). Note: sddm + nanorc sources live in kiro-iso (different repo layout than the edu-* skel paths).
- [ ] **GParted launcher** — add a button to launch gparted if installed (`shutil.which("gparted")`); decide which page it belongs on (Maintenance or a dedicated Disks section); button should be hidden/insensitive when gparted is not installed
- [ ] **Keep checking Bazaar works** — ongoing verification that Bazaar launches and functions correctly across distros
- [ ] **Skel page** — new page to copy files/folders from `/etc/skel/` to the user's home (and vice versa); buttons to copy individual entries or sync entire skel; useful for re-applying default configs to existing users
- [ ] **List user systemd services (on the Dev page)** — add a Dev-page section listing the current user's systemd units (`systemctl --user list-units`); show name, description, and active/enabled state; read-only. _Folded onto the Dev page 2026-05-25; the separate-page idea was dropped — the Dev page already absorbed the old "kiro-diag page in ATT" diagnostics item._
- [x] **Enable `reflector.timer`** — _done 2026-05-27._ Toggle/button added to enable `reflector.timer` so mirrors stay fresh/fast, reducing partial-update and slow-mirror issues.

---

*Keep this list short — if an item is scheduled into a milestone, move it there and delete it from here.*
