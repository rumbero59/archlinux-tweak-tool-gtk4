# ATT - Ideas for future features

## Claude's Ideashop

### Pre-Install Compatibility Report — show a transaction preview before any desktop install

Before opening the alacritty terminal, run `pacman -Sp --print-format "%n" [pkg list]` (dry-run, no download) to retrieve the full resolved package list and cross-check it against installed desktops. Packages that already belong to an installed DE's list are highlighted as "shared — will not be removed if you later remove [other DE]". Packages unique to the target DE are listed as "new". Show the summary in a small `Gtk.TextView` inside a scrolled confirmation dialog: the user sees exactly how big the install is and which DEs will share packages before clicking Install. Zero extra subprocess cost — `pacman -Sp` is fast, read-only, and does no package resolution on disk.

**Why this is worth building:** Plasma installs 400+ packages. Users who don't know this click Install expecting a 10-package operation and are surprised by 20 minutes of downloads. A pre-install report sets expectations, catches repo availability issues before the terminal opens, and extends naturally to the "one-way" warning (if the report detects Plasma, it can reinforce the irreversibility message).

---

### Notification History Popover — make ephemeral startup/background notifications retrievable

Add a small bell button at the bottom of the sidebar that opens a `Gtk.Popover` listing the last 10 in-app notifications with timestamps. As ATT now fires meaningful background notifications (e.g. "Config backups complete"), users lose them because they auto-dismiss in seconds. Implementation: a `collections.deque(maxlen=10)` in `functions.py` populated on every `show_in_app_notification` call with `(timestamp, message)`; the popover reads from it on open. Zero extra subprocess calls, zero persistent state — the log lives only for the session.

**Why this is worth building:** The "Config backups complete" notification is the first of what will become several background-event signals. Once there are 5+ of these, users will occasionally miss them and have no way to check what happened at startup. A session-scoped log gives them that without the overhead of writing to a file.

### Service-Status Dot in Sidebar Tab Labels — live signal next to tabs gated on systemd services

For any tab whose visibility is gated on a service (SDDM is now gated on `plasma-login`), add a small colored indicator (unicode circle or "(active)"/"(inactive)" suffix) to the `stack.add_titled()` label. ATT already calls `check_service_enabled()` at startup to decide whether to show the tab — feeding that same result into the label string is trivial. Users get immediate status context ("SDDM [enabled]") without having to open the tab and look at a label. No new detection code required.

### Post-Removal Directory Audit Helper — warn when a removed package leaves files behind

After any `pacman -R` completes, scan the package's known install paths for leftover files/directories and show an in-app notification listing them. ATT already knows which paths each package owns (e.g. `/usr/share/sddm/themes/edu-simplicity` for the simplicity package). A quick `os.path.exists` check after the terminal closes surfaces orphan directories before they cause confusion in dropdowns or file pickers. Requires no new system calls — just a path list per managed package.

### Initramfs Health Check on Kernel Page — detect missing initramfs for installed kernels

After the kernel list renders, scan `/boot` (and `/boot/efi/<machine-id>/`) for each installed kernel and check whether its initramfs file exists. Show a warning badge next to any kernel row that has no matching initramfs — something like `⚠ no initramfs found`. On dracut systems this catches the case where `dracut-hook` wasn't installed when the kernel was added. A single `glob.glob` per kernel, no subprocess. The "Regenerate All Initramfs" button is the natural fix action already shown on the same page.

### SDDM Live Preview Thumbnail on Theme Select — show a screenshot when the theme dropdown changes

When the user picks a theme in the SDDM theme dropdown, check `/usr/share/sddm/themes/<name>/preview.png` (SDDM's standard preview file) and display it in a small `Gtk.Picture` below the dropdown. Most packaged SDDM themes ship this file. If the file is absent, hide the picture widget. The dropdown already fires `notify::selected` — just connect a second handler there. Zero new dependencies, and users can visually confirm they're choosing the right theme before clicking Apply.

### DE-aware Quick-Launch Bar — context-sensitive sidebar buttons per desktop environment

### Distro-Mismatch Warning Banner — alert when `fn.distr` and `get_distro_label()` disagree

### Session-Scoped Package Cache Warmer — pre-populate `_pkg_cache` at startup in one batch call

ATT now caches `check_package_installed()` results per call. The next step is to warm the entire cache in one `pacman -Q` call during `_finish_startup_init()` — parse the output once into a set, then pre-fill `_pkg_cache` for every package name ATT knows it will check. This turns N sequential subprocesses into a single fast bulk query at startup, with zero changes needed in any calling code. The cache key format is already compatible: `_pkg_cache[pkg] = pkg in installed_set`.

Now that ATT has both detection methods, a one-line comparison at startup could show a non-blocking in-app notification when `fn.distr != get_distro_label().lower()` (e.g. `fn.distr="arch"` but `get_distro_label()="Kiro"`). This surfaces misconfigured `/etc/os-release` files on custom spins and helps users on derivative distros understand why certain guards fire or don't fire. Zero extra detection code — just a comparison of two values already computed.

Add a collapsible quick-launch strip at the bottom of the sidebar that shows only the tools relevant to the running DE. On Plasma it shows `plasma-systemsettings` and `kwin --replace`; on GNOME it shows `gnome-tweaks` and `dconf-editor`; on plain WMs it shows nothing. The strip reads `fn.desktop` once at startup and builds only the applicable buttons. Result: power users get one-click access to complementary DE tools without cluttering the sidebar for WM users who don't need them.

**Why this is worth building:** ATT already knows the DE at startup — surfacing the right companion tools in context takes zero new detection code and removes the "where do I set Plasma-specific things ATT can't touch?" friction point.

### Run-as-User Helper in functions.py — consolidate the sudo -E -u env HOME= pattern into one call

Add `fn.run_as_user(cmd)` that wraps `subprocess.Popen("sudo -E -u {fn.sudo_username} env HOME={fn.home} {cmd} &", shell=True, ...)`. Every Software/Shell page launch site currently repeats this 4-part pattern by hand; one helper means a future `HOME` or env-var fix propagates everywhere automatically. The helper can also accept an optional `env_extras` dict for tools that need additional vars (e.g. `WAYLAND_DISPLAY`). Zero new dependencies — just a 6-line wrapper in `functions.py` that every GUI module already imports.

**Why this is worth building:** Today's `alacritty-tweak-tool` HOME bug required patching two separate launch sites. As more user-space GUI tools are added to ATT (e.g. other tweak tools, config editors), each will repeat the same error-prone boilerplate. One canonical helper makes correctness the default.

### Repo-Readiness Banner — one-time banner telling the user which repos ATT needs and which are missing

At startup, compare the repos ATT uses (chaotic-AUR, nemesis) against the user's active `pacman.conf` mirrors. If any are absent, show a dismissible top-of-window banner: "Some features require chaotic-AUR — [Enable it]". Clicking the link jumps to the Pacman tab's repo section. This surfaces the "pure Arch" problem reported across multiple tabs today — instead of each button failing individually with its own message, the user gets one clear overview at startup that sets expectations before they click anything. Zero extra detection code: `fn.check_chaotic_aur_active()` and `fn.check_nemesis_repo_active()` already exist.

### Install-Path Parity Checker — flag when install and remove use different package names

ATT has several places where the install path and remove path independently decide which package name to use (e.g. fastfetch-git vs fastfetch). A lightweight startup check could compare the two decisions and warn in the console if they diverge — catching bugs like today's before they reach users. Implementation: for each managed package pair, call both the "which package to install?" and "which package to remove?" selectors at startup in `--debug` mode and log a warning if they don't agree. Zero UI changes; pure developer diagnostic.

---

### Script Compliance Dashboard in Dev Page — live ATT Script Standard audit for all data/bin scripts

Extend the Dev page's existing Safeguards section with a second grid showing each `data/bin/` script and whether it passes the ATT Script Standard checklist: `set -euo pipefail` ✓/✗, tput colors ✓/✗, helper functions ✓/✗, error trap ✓/✗. Each row is a script name; columns are the four checks; cells are green/red labels computed at page-map time by scanning the first 40 lines of each file with a regex. No subprocess calls — pure Python file reads. Developers can verify compliance at a glance without running a separate audit script.

**Why this is worth building:** The 14-script error-trap fix this session was discovered by an external scan, not by anything in ATT itself. A live compliance view in the Dev page would have surfaced it earlier and makes future regressions immediately visible.

### Config-File Change Preview — show a before/after diff before ATT writes any system config

Before overwriting a system config file (e.g. `/etc/bluetooth/main.conf`, `/etc/hosts`, `/etc/pacman.conf`), compute the diff and show it in a small `Gtk.TextView` inside a confirmation dialog. The user sees exactly which lines change before clicking Confirm. Implementation: write the proposed content to a temp file, run `diff -u original tmp`, display the output. Applies to any ATT operation that calls `open(..., "w")` on a system path. Ties directly into Objective 14 (Transparency) and prevents "what did ATT just do to my config?" confusion.

**Why this is worth building:** Today's `AutoEnable` toggle silently rewrites `/etc/bluetooth/main.conf`. Users who manage their configs manually have no way to verify ATT only changed the one line it claimed to. A diff dialog makes the operation auditable without requiring the user to open a terminal.

### Plymouth mkinitcpio Guard — warn when plymouth hook is missing from initramfs config

Before showing the theme manager, check whether `plymouth` appears in the `HOOKS` line of `/etc/mkinitcpio.conf`. If it's absent, the theme applies but never renders at boot — a silent failure that puzzles users. Show a one-line amber warning row at the top of the Plymouth page: "plymouth hook not found in /etc/mkinitcpio.conf — themes will not render at boot." No action required from ATT; the warning is informational only. Zero extra subprocess calls — `fn.get_file_content("/etc/mkinitcpio.conf")` and a string check.

**Why this is worth building:** Users on fresh installs or minimal setups often have plymouth installed but not wired into mkinitcpio. They apply a theme, reboot, see no change, and assume ATT is broken. The warning surfaces the real cause in the tool where they'd look first.

---

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

### Boot Parameter Audit Tab — one-click review of every bootloader's current kernel cmdline

Add a lightweight "Boot Audit" section (or row) somewhere in the Plymouth or a new System page that reads the actual active kernel cmdline from `/proc/cmdline` and diffs it against what ATT has configured. If ATT added `quiet splash` to the entries but the running kernel doesn't show them, the user gets an immediate warning that the change didn't take effect (probably because the wrong entries were edited, or initramfs wasn't rebuilt). Shows the live cmdline, ATT's expected cmdline, and a diff highlight in three lines — no subprocess, no terminal, just a `open("/proc/cmdline").read()`.

**Why this is worth building:** Users apply a Plymouth theme, reboot, see no splash, and blame ATT. The real cause is almost always a missing `quiet splash` on the running entry, or a wrong ESP path. A `/proc/cmdline` diff surfaces the gap instantly in the tool itself, before the user files a bug.

---

### Config Dir Self-Audit on Startup — surface stale files ATT no longer owns

During `ensure_app_dirs()` (or a new `audit_app_dirs()`), scan `~/.config/archlinux-tweak-tool/` and compare every file there against a known list of files ATT currently writes. Any file not in the list (e.g. a `settings.ini` with termite config from an old arco-era version) is logged as a warning and optionally removed after user confirmation. No new subprocess calls — pure `os.scandir` + set difference. Prevents ghost config from old ATT versions confusing users or overriding current settings.

**Why this is worth building:** ATT has been through several major rewrites. Each one left files in `~/.config/archlinux-tweak-tool/` that the new version never touches. A one-time self-audit at startup surfaces the problem immediately rather than leaving the user puzzled when they find an unexpected file in their config folder.

---

### Theme Compatibility Smart Selector — warn and auto-disable incompatible themes per desktop

Extend the Plasma warning pattern across all tabs: for each installer checkbox (theme, icon, cursor), detect the current desktop and disable/gray-out incompatible packages with a tooltip explaining why. Examples: GTK themes auto-disabled on Plasma (already warned), KDE icons auto-disabled on XFCE/dwm. Build a lightweight `compatibility_map` dict keyed by desktop and package name, checked at GUI build time.

**Why this is worth building:** Users no longer accidentally install packages that won't work. The warning already signals "this won't work on Plasma" — extending it to prevent the selection entirely (with friendly gray-out + tooltip) prevents the support question entirely, reduces session waste, and scales to other desktops and incompatibilities ATT will discover.

---

### AUR Package Age Badge in Available-Theme Rows — show relative age next to each package name

Now that ATT can fetch `LastModified` from the AUR RPC, surface that data inline: add a small grey label "(3 months ago)" or "(2 years ago)" next to each package name in the available-themes dropdown. The data is already fetched when sort-by-date is active — it just needs to be formatted and shown. A relative-age helper (`time.time() - ts` → "N days/months/years ago") is four lines of code and gives users immediate context without having to sort and infer. Could also flash a warning color for packages not updated in 2+ years.

---

### Checkbox Preset Diff View — show what each preset changes before applying it

When the user hovers (or long-presses) an All/Normal/Small/None preset button, compute the diff between the current checkbox states and what the preset would set, and show a transient popover listing only the checkboxes that would change. "Normal would disable: local ip, locale, color blocks." Zero network calls, zero file reads — purely comparing `_PRESET_*` dict against current `get_active()` states in memory. The preset dicts introduced in this session make this trivial: one `{k for k, v in preset.items() if v != getattr(self, k).get_active()}` set comprehension.

**Why this is worth building:** Users click Normal and wonder why a checkbox they enabled is now gone. Showing what's about to change — before the click lands — replaces surprise with control, and the implementation cost is nearly zero now that preset data is in dicts.

---

### get-* Script Generator — auto-generate install scripts from desktopr.py package lists

Add a small dev utility (e.g. `tools/gen-desktop-script.py`) that reads the package arrays from `desktopr.py` and generates a `get-<desktop>-on-att` script for each one. Every time a package is added or removed in `desktopr.py`, one command regenerates all scripts so they stay in sync with no manual editing. The generator would inject the correct conflict-removal block per desktop (lbonn variants for ohmychadwm/chadwm, nothing for XFCE/Plasma) from a small config dict.

**Why this is worth building:** The ohmychadwm script was created by hand from the desktopr.py list — that's a maintenance liability. If someone adds a package to the GUI installer and forgets to update the standalone script, the two silently diverge. A generator collapses them into one source of truth with zero manual sync needed.

---

### SSH Key Manager Tab — create, inspect, rotate, and deploy SSH keys from a GUI

Add a dedicated SSH tab that covers the full key lifecycle: generate a new key pair (ed25519 by default, RSA optional) with a name and optional passphrase, list existing keys under `~/.ssh/` with type/fingerprint/comment shown inline, copy the public key to clipboard or append to `~/.ssh/authorized_keys`, change or remove a passphrase on an existing key, and delete a key pair with a confirmation dialog. Wrap `ssh-keygen` calls in daemon threads so the UI stays live during generation. A small `authorized_keys` viewer (toggle visibility) rounds out the tab.

**Why this is worth building:** SSH key hygiene is one of the most common friction points for Linux newcomers — they forget where keys live, don't know how to inspect them, and copy keys manually and incorrectly. Putting the whole workflow in one place, with clear labels for key type and fingerprint, removes a category of support questions and teaches best practices through use.

---

### Docstring Coverage Badge in Dev Mode — runtime count of undocumented public functions

When `--dev` is active, add a one-line console output during startup that counts public functions without docstrings across all loaded modules: `[DEV] Docstring coverage: 312/315 public functions (99%)`. Walk each module's `__dict__` for callables that don't start with `_` and check `.__doc__`. Zero user-visible UI, zero performance cost in production — the check runs only under `if fn.DEV:` in `_finish_startup_init()`. After a review pass this would print 100% and thereafter acts as a regression guard: if a new public function lands without a docstring, the number drops and the developer notices immediately.

**Why this is worth building:** The full review pass just completed gets the codebase to 100% docstring coverage for public functions. This one-liner locks that in without any CI infrastructure — the developer sees the count every time they run with `--dev` and the feedback loop is instant.

---

### Package Snapshot Timeline — make ATT's silent desktop_history visible and actionable

The Packages page already writes `pacman -Q` snapshots to `~/.config/archlinux-tweak-tool/desktop_history/` on every Desktop page action. Add a **History** button that opens a popover listing each snapshot by date/time, and a diff view between any two snapshots using `difflib.unified_diff`. Added packages appear green, removed packages red. A **Restore** button re-installs the diff using a single `pacman -S <added...>` call in a terminal. Zero new file writes, zero new detection — the data is already there, just invisible.

**Why this is worth building:** Users install a DE, tweak packages, then forget what changed between sessions. The snapshot timeline turns a silent audit trail into a tool for understanding and recovering system state — without any external backup software or new ATT infrastructure.
