# ATT - Ideas for future features

## Performance tab additions

- **preload** (`preload`) — adaptive readahead daemon that prefetches frequently used binaries into memory; same install/enable/disable pattern
- **IO scheduler** — dropdown to set the I/O scheduler (bfq, mq-deadline, kyber, none) per block device; useful for HDD vs NVMe

## New tabs worth adding

- **Gaming Stack** — Steam, Lutris, MangoHud, vkbasalt, vm.max_map_count tweak; could live in a dedicated Gaming tab
- **Plymouth (all distros)** — currently Omarchy-only; extend to all Arch distros: gate content on whether `plymouth` is installed, show Install button if not, warn if not in mkinitcpio HOOKS, show full theme manager if fully configured

## Already implemented this session

- Ananicy CPP + cachyos-ananicy-rules-git (Performance)
- GameMode (Performance)
- Tuned + tuned-ppd combined enable/disable (Performance)
- Swapfile size display + btrfs detection (Performance)
- AUR Helper — yay-git / paru-git with chaotic-aur detection (Pacman)

---

## Claude's Ideashop

### SDDM Live Preview — render the selected theme in a scaled GTK window

Add a **Preview** button next to the SDDM theme dropdown that launches a borderless GTK window sized to ~50% of screen resolution and renders the selected SDDM theme's QML or HTML preview asset (most themes ship a `preview.png` or `metadata.desktop` with a `Screenshot=` key). No SDDM restart required — ATT reads the asset path, scales it into a `Gtk.Picture`, and shows it in a transient dialog. Gives users a visual sanity-check before they commit the theme and reboot into the login screen.

**Why this is worth building:** The current flow is: pick theme → apply → reboot → see it for the first time. A 200ms preview eliminates the reboot-to-check cycle entirely.

---

### Wallpaper Slideshow Mode — variety-lite built into ATT

Add a **Slideshow** toggle to the wallpaper page that rotates through the selected folder on a user-defined interval (5 min, 15 min, 1 h) using a `GLib.timeout_add_seconds` loop calling `on_random_wallpaper`. No variety required, no extra package — ATT already has all the pieces. A single `GLib` timer, a stop button, and an interval dropdown is the entire implementation. Pairs naturally with the existing folder browser and thumbnail grid.

**Why this is worth building:** Users who don't want the full variety daemon just want their wallpaper to rotate. This delivers that in ~30 lines reusing code ATT already has.

---

### System Health Score — a living pulse for your Arch install

Add a persistent **Health Score** widget to the ATT sidebar (or as a dedicated tab) that computes a single 0–100 score in real time from factors ATT already knows how to read:

| Factor | Weight | Source |
| --- | --- | --- |
| Failed systemd units | 25 | `systemctl list-units --failed` |
| Orphaned packages | 20 | `pacman -Qdtq` |
| Journal critical errors (last 24h) | 20 | `journalctl -p crit --since "24h ago"` |
| Disk usage on `/` and `/home` | 20 | `shutil.disk_usage()` |
| Broken/unreachable mirrors | 15 | test first mirror in `/etc/pacman.d/mirrorlist` |

The score updates every time the user opens ATT (lazy, low-cost) and recomputes live when the Maintenance tab runs a cleanup. Each factor shows its contribution inline so the user knows exactly what is dragging the score down. Tapping a factor jumps to the relevant ATT tab — failed services → Services tab, orphans → Maintenance tab.

**Why this is worth building:** Most users never notice their system degrading because every problem lives in a separate tab. A single number gives an immediate "is my system happy?" answer and turns ATT from a collection of manual tools into something that proactively surfaces problems — without adding any new system knowledge to the codebase.

---

### Backup Timeline Viewer — make ATT's silent backups visible

Add a small **Backups** section (or side panel) that reads the `mtime` of each known `-bak` file ATT creates and shows a table: filename, backed-up date, size, and a **Restore** button. No extra tracking, no database — the filesystem already has all the data.

**Why this is worth building:** ATT silently creates backups the user never sees. When something breaks they don't know a backup exists or where it is. Surfacing the mtime + a one-click restore turns the backup system from invisible insurance into a tool the user can actually trust and use.

---

### GUI App Launcher Health Check — test display connectivity before launching

Before launching any GUI app via `sudo -u` (bazaar, octopi, pamac, etc.), run a one-liner `sudo -u <user> env XDG_RUNTIME_DIR=/run/user/<uid> xdpyinfo >/dev/null 2>&1` or Wayland equivalent. If it fails, show an in-app notification explaining the display connection problem rather than silently exiting. Avoids the "button does nothing" mystery and points the user at the real issue immediately.

**Why this is worth building:** The pkexec-stripping-env-vars problem will recur for every GUI app ATT launches. A reusable `can_launch_as_user()` guard in `functions.py` — checked once before every Popen — replaces per-app debugging with a single, consistent diagnostic message.

---

### Dev Mode Dashboard — a dedicated --dev page listing all hidden experimental features

When `--dev` is active, add a "Dev" tab (hidden in normal mode) that lists every widget currently gated behind `fn.DEV`, its file:line, and a one-line status (installed/missing). Clicking any row jumps to the relevant tab. No runtime cost in production — the tab itself is appended only under `if fn.DEV:`.

**Why this is worth building:** As `--dev` guards accumulate across tabs, it becomes hard to remember what's hidden and why. A central Dev tab turns the flag from a one-off workaround into a structured staging area — visible to the developer, invisible to users.

---

### Distro-Aware Tab Visibility Dashboard — surface hidden tabs without --dev

Add a lightweight startup log line (visible only with `--debug`) that lists every tab currently hidden by a distro guard, e.g. `[CachyOS] SDDM tab hidden (fn.distr == cachyos) — use --dev to show`. No new UI, no new files — just one `fn.debug_print` after each `if fn.distr != X or fn.DEV:` guard in `gui.py`. As the guard list grows across distros, this gives instant visibility into what's hidden on the current system without reading source code.

**Why this is worth building:** As ATT runs on more distros, more tabs get distro-gated. Without a central log of what's hidden and why, developers waste time wondering "why is that tab missing on this machine?" A debug-mode summary answers the question in one launch.

---

### Theme Compatibility Smart Selector — warn and auto-disable incompatible themes per desktop

Extend the Plasma warning pattern across all tabs: for each installer checkbox (theme, icon, cursor), detect the current desktop and disable/gray-out incompatible packages with a tooltip explaining why. Examples: GTK themes auto-disabled on Plasma (already warned), KDE icons auto-disabled on XFCE/dwm. Build a lightweight `compatibility_map` dict keyed by desktop and package name, checked at GUI build time.

**Why this is worth building:** Users no longer accidentally install packages that won't work. The warning already signals "this won't work on Plasma" — extending it to prevent the selection entirely (with friendly gray-out + tooltip) prevents the support question entirely, reduces session waste, and scales to other desktops and incompatibilities ATT will discover.
