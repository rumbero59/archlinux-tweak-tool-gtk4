# ATT Dev Page — Glossary

> **Purpose:** every row on ATT's Dev page in plain language, so you can read it and know what is being checked, why it matters, and what to do when something says FAIL.
>
> **Audience:** Kiro users and anyone running ATT with `--dev` who wants to understand what they're looking at, without having to learn systemd internals or grep the source.
>
> If a row is missing here, please open an issue — every Dev row should have an entry.

---

## How to read each entry

| Field            | What it tells you                                                  |
|------------------|--------------------------------------------------------------------|
| **What it checks** | The exact file, service, sysfs path, or command being inspected. |
| **Why it matters** | What goes right (or wrong) on your machine because of this.      |
| **PASS means**     | The conditions that produce the green check.                     |
| **FAIL / WARN means + fix** | What the red/yellow state implies and how to address it. |

---

## Sections on the Dev page

1. [Session diagnostics](#session-diagnostics)
2. [Per-tab status](#per-tab-status)
3. [Cross-cutting safeguards](#cross-cutting-safeguards)
4. [System integrity (kiro-audit mirror)](#system-integrity-kiro-audit-mirror)
5. [Userspace tuning](#userspace-tuning)

---

## Session diagnostics

Meta info about the running session — confirms ATT detected your system correctly. None of these are PASS/FAIL — they're shown to help us see what ATT sees.

### Distro Detection

#### `fn.distr`
- **What it checks:** the short ID ATT uses internally (e.g. `arch`, `omarchy`, `cachyos`, `prismlinux`, `artix`).
- **Why it matters:** every distro guard, conditional UI element, and package check keys off this string. If it's wrong, ATT shows the wrong tabs.
- **PASS means:** there is no PASS/FAIL here — it's an info row.
- **FAIL means:** if the value isn't your distro, open an issue with `cat /etc/os-release` output.

#### `get_distro_label()`
- **What it checks:** the human-readable label (e.g. `Kiro`, `Arch`, `CachyOS`, `Omarchy`). On Kiro this reads `Kiro` even though `fn.distr` is `arch` (Kiro is an Arch-based rebrand).
- **Why it matters:** lets ATT show a friendly name in the UI while still using `fn.distr` for guard logic.
- **PASS means:** the label matches expectations. The Kiro pairing (`fn.distr = arch` + label `Kiro`) is explicitly marked OK.
- **WARN (orange ⚠ mismatch) means:** label and `fn.distr` disagree in an unexpected way — investigate.

### Environment

#### `XDG_CURRENT_DESKTOP`
- **What it checks:** the desktop environment as advertised by the session.
- **Why it matters:** many wallpaper/themer integrations need to know the DE to call the right helper (xfconf-query for XFCE, gsettings for GNOME, etc.).
- **PASS / FAIL:** info row.

#### `fn.sudo_username`
- **What it checks:** the real (non-root) user that launched ATT.
- **Why it matters:** ATT runs as root but writes user-config to that user's home; this row confirms the right home is targeted.
- **PASS / FAIL:** info row.

#### `fn.home`
- **What it checks:** that user's home directory (e.g. `/home/erik`).
- **Why it matters:** all ATT-managed user configs land under `${fn.home}/.config/archlinux-tweak-tool/`.
- **PASS / FAIL:** info row.

### Session

#### `XDG_SESSION_TYPE`
- **What it checks:** `x11` or `wayland`. If the env var isn't set (common when starting a WM via `startx`/`.xinitrc`), ATT infers it from `WAYLAND_DISPLAY` / `DISPLAY` and shows `(inferred)`.
- **Why it matters:** wallpaper setters and some helpers behave differently on X11 vs Wayland.
- **PASS / FAIL:** info row; `(not set)` means no session display variables present (e.g. tty-only).

#### `active shell`
- **What it checks:** the login shell of `fn.sudo_username` (`bash` / `zsh` / `fish`).
- **Why it matters:** the Shells page surfaces shell-specific actions based on this.
- **PASS / FAIL:** info row.

### System

#### `bootloader`
- **What it checks:** which bootloader is in use — `systemd-boot`, `grub`, `limine`, `refind`, or `unknown`.
- **Why it matters:** the Plymouth page and several install paths behave differently per bootloader (`systemd-boot` needs `/etc/kernel/cmdline`; GRUB needs `grub-mkconfig`; etc.).
- **PASS / FAIL:** info row.

#### `running kernel`
- **What it checks:** output of `uname -r` (e.g. `7.0.10-zen1-1-zen`).
- **Why it matters:** the Kernels group below compares this against the boot images present in `/boot/`.
- **PASS / FAIL:** info row.

#### `init system`
- **What it checks:** `systemd` or `OpenRC`. Detected by the presence of `/run/openrc` or `/sbin/openrc`.
- **Why it matters:** all of ATT's service-management code assumes systemd. The few OpenRC-friendly distros (Artix) are guarded against.
- **PASS / FAIL:** info row.

#### `initramfs`
- **What it checks:** `mkinitcpio` (Arch default) or `dracut` (Garuda, some Cachy configs).
- **Why it matters:** the Plymouth integration uses different commands per generator (`mkinitcpio -P` vs `dracut --regenerate-all --force`).
- **PASS / FAIL:** info row.

#### `systemd PID 1`
- **What it checks:** `/run/systemd/private` exists.
- **Why it matters:** confirms systemd is actually running as PID 1 (not running inside a chroot/container where the marker wouldn't exist).
- **PASS / FAIL:** info row.

---

## Per-tab status

One sub-section per active ATT tab. Confirms the packages/services/binaries each tab needs are actually installed. Most rows are "is this present?" checks — green = yes, red/empty = no. None of these are failures by themselves: ATT just won't offer features it has nothing to act on.

### AI Tools

Detects local AI tooling via binary paths (`/usr/bin/ollama`, `/usr/bin/open-webui`, `/usr/bin/aider`, `/usr/bin/claude`) rather than package names — these install from varied AUR sources.

- **PASS means:** the binary is on PATH.
- **FAIL / empty means:** the tool isn't installed. Install it via the AI Tools tab if you want it.
- **`ollama.service active`:** the ollama daemon is running. If you have ollama installed but the service is inactive, models won't be reachable until you `sudo systemctl start ollama`.

### Autostart

#### `~/.config/autostart/*.desktop`
- **What it checks:** how many `.desktop` autostart entries exist for your user.
- **Why it matters:** quick sanity number — if you expected 5 and see 0, something cleared your autostart folder.
- **PASS / FAIL:** info row.

### Desktop

Detects 15 desktop environments and tiling window managers via their session binary (Plasma, GNOME, XFCE, Cinnamon, MATE, Budgie, Deepin, LXQt, awesome, bspwm, chadwm, i3, leftwm, ohmychadwm, qtile).

- **Why binaries, not packages:** several DE names (xfce4, gnome, mate, deepin, lxqt) are pacman *groups* — `pacman -Qi xfce4` always fails. Binary presence is the authoritative test.
- **PASS means:** the binary is in `/usr/bin/`. Multiple DEs PASS is normal if you've installed several.
- **FAIL / empty means:** that DE/WM isn't installed; install via the Desktop page if you want it.

### Fastfetch

- **`fastfetch` / `lolcat`:** the packages — present if installed.
- **`user config exists`:** `~/.config/fastfetch/config.jsonc` is there.
  - **FAIL means:** fastfetch will run with built-in defaults. Apply a preset from the Fastfetch page to populate your config.

### Icons

#### `sardi-* packs`, `surfn-* packs`, `neo-candy-* packs`
- **What it checks:** how many packages with that prefix are installed (Erik's icon-pack families).
- **Why it matters:** quick visibility into your icon library coverage; the Icons page lists and toggles these.
- **PASS means:** at least one pack of that family is present (count shown).
- **FAIL means:** zero packs — install one from the Icons page if you want it.

### Kernels

Dynamically enumerates `/boot/vmlinuz-*` — the actually-bootable kernels, regardless of package name (Liquorix ships as `linux-lqx`, CachyOS as `linux-cachyos`, etc.). Per kernel found:

- **`{pkgname}`:** the boot image path. The currently-running kernel is marked `<running>` in green; others are PASS green.
- **`{pkgname}-headers`:** matching headers package — needed by DKMS for that kernel. FAIL means DKMS modules (NVIDIA, VirtualBox, etc.) won't build for this kernel.
- **`(none found)` means:** no `vmlinuz-*` files in `/boot/` — broken system; you almost certainly can't boot. Investigate immediately.

### Locale

- **`LANG`:** your active locale (e.g. `en_US.UTF-8`).
- **`keyboard (X11 layout)`:** keymap reported by `localectl`.
- **`vc keymap`:** virtual-console keymap (tty).
- **`timezone`:** zone reported by `timedatectl`.
- **PASS / FAIL:** all info rows. `(not set)` means the system didn't report a value.

### Maintenance

- **`reflector` / `rate-mirrors`:** mirror-ranking tools used by the Maintenance page. FAIL means the page falls back to a manual mirror picker.
- **`pacman ParallelDownloads`:** the parallel-downloads value from `/etc/pacman.conf`. `(default 1)` means it's the legacy single-threaded behavior — the Pacman page can raise it.

### Network

- **`avahi` / `avahi-daemon.service`:** mDNS / Zeroconf for `.local` hostnames. Active means LAN device discovery works.
- **`samba` / `smb.service`:** SMB file sharing daemon. Active means others on the LAN can browse shares you host.
- **`firewalld` / `firewalld.service` / `firewall-config`:** the firewall. Kiro ships firewalld enabled+active by default (replaces ufw, which is intentionally out-of-scope).
- **`firewalld allows mdns` / `firewalld allows samba`:** these services explicitly permitted in the default zone. FAIL means avahi/samba won't reach the LAN even if running.

### Packages (AUR helpers)

#### `yay`, `paru`, `trizen`, `pikaur` on PATH
- **What it checks:** which AUR helper(s) you have installed.
- **Why it matters:** ATT's AUR install/remove flows prefer the first available helper. Having at least one is recommended.
- **PASS means:** that helper is on PATH.
- **FAIL means:** install one from the Packages page (paru is the modern default).

### Pacman

- **`chaotic-AUR active`:** chaotic-aur repo enabled in `/etc/pacman.conf`. Shipped with Kiro.
- **`nemesis_repo active`:** Erik's custom pacman repo. Required for several `edu-*` and `kiro-*` packages.
- **`[multilib] enabled`:** 32-bit repo. **Intentionally OFF by default on Kiro** (not a gaming distro — Steam/Wine 32-bit libs are out of scope). One-click enable from the Pacman page if you want them.
- **`[testing] enabled`:** Arch [testing] repo. Off by default — only for early adopters who accept breakage.

### Plymouth

- **`plymouth installed`:** the Plymouth boot splash package. **Kiro intentionally ships without Plymouth** — FAIL/empty here is correct for a stock Kiro install.
- **`active theme`:** if Plymouth IS installed, the current theme name. `(none)` means no theme has been applied yet.
- **`HOOKS contains plymouth` (mkinitcpio)** / **`att-plymouth.conf exists` (dracut):** the initramfs hook that wires Plymouth into boot. WARN ("missing") means Plymouth is installed but won't fire at boot — the Plymouth page has a one-click fix.
- **`/etc/kernel/cmdline splash` (systemd-boot only):** the kernel command line contains `quiet splash`. Without these, Plymouth has nothing to suppress and won't render.

### Privacy

- **`hblock on PATH`:** the ad/tracker `/etc/hosts` block tool. Optional.
- **`/etc/hosts has hblock marker`:** confirms hblock has run and populated your hosts file (470k+ entries).
- **`firefox-ublock-origin`:** the ad-blocker extension package. FAIL means Firefox uses bare defaults.

### Performance

This is the densest tab — lots of optional perf tooling.

- **`tuned` / `tuned.service` / `active tuned profile`:** the system tuning daemon, its service, and the active profile name (`balanced`, `throughput-performance`, etc.). Kiro ships tuned active.
- **`tuned-ppd` / `tuned-ppd.service`:** the `power-profiles-daemon`-compatible front-end on top of tuned. Kiro ships this active so desktop power widgets work.
- **`PPD active profile (D-Bus)`:** the profile reported via D-Bus (`balanced`, `power-saver`, `performance`). **WARN (`⚠ mismatch with tuned`)** means the desktop power widget changed the profile but tuned hasn't picked it up — usually transient; restart tuned-ppd if it persists.
- **`irqbalance` / `irqbalance.service`:** IRQ-distribution daemon. Optional; helps on multi-core boxes.
- **`ananicy-cpp` / `ananicy-cpp.service`:** auto-nice daemon (re-prioritises noisy/idle processes). Shipped active on Kiro.
- **`preload` / `preload.service`:** legacy file-preloader. Optional; rarely useful on modern SSDs.
- **`gamemode` / `cpupower`:** optional perf tools — install if you want them, no opinion otherwise.
- **`fstrim.timer enabled`:** weekly TRIM for SSDs. **Should be ENABLED on Kiro** — if disabled, your SSD doesn't get freed-block discards on a schedule.

### SDDM

- **`active display manager`:** which DM is currently enabled (`sddm`, `gdm`, `lightdm`, etc.) or `none` for tty-only.
- **`sddm installed` / `sddm enabled`:** SDDM package presence and service state.
- **`plasma-login enabled`:** the CachyOS-style hyphenated SDDM-replacement service. WARN (orange `yes`) means you're on CachyOS or a derivative — Kiro doesn't use this.

### Services

- **`cups` / `cups.service`:** printing. Kiro enables `cups.socket` (socket activation) on installed systems via Calamares — the `cups.service` row reads inactive-until-needed, which is correct.
- **`bluez` / `bluetooth.service`:** Bluetooth stack.
- **`bluetooth-autoconnect` / `bluetooth-autoconnect.service`:** optional helper for "remember and auto-reconnect to last device" — toggled from the Services tab's Bluetooth section.

### Shells

Each row checks one package: `bash`, `bash-completion`, `zsh`, `zsh-completions`, `zsh-syntax-highlighting`, `oh-my-zsh-git`, `fish`, `alacritty`, `alacritty-tweak-tool-git`.

- **PASS means:** package installed.
- **FAIL means:** that shell/extension isn't installed; the Shells page can install it.

### Software

Detects 12 GUI package managers / app stores via binary paths (Pamac, Octopi, Bazaar, GNOME Software, Plasma Discover, Bauh, Flatpak, Snap, pacseek, pacui, pachub, app-manager) — names vary across distros, binary is authoritative.

- **PASS means:** binary present.
- **FAIL means:** not installed; install from the Software page if you want it.

### Themer

Tracks 4 packages: `edu-awesome-git`, `edu-i3-git`, `edu-leftwm-git`, `edu-qtile-git` — Erik's tiling-WM config families. PASS = installed, FAIL = not.

### Themes

#### `edu-* GTK themes`
- **What it checks:** count of packages matching `edu-arc-*`, `edu-neo-candy-*`, `edu-papirus-*`, `edu-vimix-*`.
- **Why it matters:** quick visibility into your GTK theme library.
- **PASS means:** at least one is installed (count shown).
- **FAIL means:** none — install from the Themes page if you want them.

### User

- **`{sudo_username} in wheel`:** confirms your user is in the `wheel` group, which is what `sudoers` keys off. FAIL means `sudo` won't work for that user.
- **`/etc/sudoers.d/ entries`:** how many drop-in sudoers files exist. Info row — non-zero is normal (Kiro ships several).

### Wallpaper

#### `variety`, `variety process running`
- **What it checks:** the `variety` wallpaper-rotator package, and whether the daemon is alive.
- **Why it matters:** the Wallpaper page can install/manage variety; the "running" row tells you it's actually rotating wallpapers right now.
- **PASS means:** installed and running.
- **FAIL means:** not installed (the running-row is only shown if installed).

---

## Cross-cutting safeguards

Each row here describes one **guard** — a condition that hides or shows UI based on the distro / system state, so ATT doesn't offer broken actions on unsupported configs. The authoritative source is [DISTRO_GUARDS.md](DISTRO_GUARDS.md); this glossary is the user-facing translation.

The right-hand column shows **whether the guard is currently active on your machine** — orange means "this guard is firing right now and changing what you see."

### `Plymouth page hidden` — artix guard
- **What it checks:** are you on Artix Linux?
- **Why it matters:** Artix uses OpenRC instead of systemd, and Kiro's Plymouth helpers all assume systemd. Showing the page would offer broken actions.
- **Active means:** the Plymouth page is hidden from the sidebar on Artix.

### `SDDM page hidden` — prismlinux guard
- **What it checks:** are you on PrismLinux?
- **Why it matters:** PrismLinux ships its own SDDM customisation that conflicts with ATT's.
- **Active means:** the SDDM page is hidden on PrismLinux.

### `SDDM page hidden` — plasma-login / plasmalogin service
- **What it checks:** is the CachyOS `plasma-login` (or older `plasmalogin`) service enabled?
- **Why it matters:** CachyOS replaces SDDM with its own login shim; ATT's SDDM page would write configs that get ignored.
- **Active means:** the SDDM page is hidden because a CachyOS-style login service is active.

### `Kernel: pacman-hook-kernel-install required` — arch + systemd-boot
- **What it checks:** are you on Arch (or Arch-based) **and** using systemd-boot as bootloader?
- **Why it matters:** without the `pacman-hook-kernel-install` hook package, pacman won't copy new kernel images to the ESP after upgrades — your `/boot/loader/entries/` will reference the old kernel and fail. Critical.
- **Active means:** the guard is engaged (Arch + systemd-boot is your setup).
- **Status row reads:** `active — hook installed` (green) or `⚠ hook MISSING — install pacman-hook-kernel-install` (orange).

### `User: visudo section shown` — arch guard
- **What it checks:** are you on Arch?
- **Why it matters:** the visudo helper section assumes the Arch-style `/etc/sudoers.d/` layout.
- **Active means:** the User page shows the visudo section.

### `Plymouth: omarchy marker on apply` — omarchy guard
- **What it checks:** are you on Omarchy?
- **Why it matters:** Omarchy tracks "ATT has applied a custom Plymouth theme" in `att_settings.json` so its own Plymouth defaults don't fight ATT's choice.
- **Active means:** when you apply a Plymouth theme on Omarchy, the marker is written; on other distros the marker step is skipped.

---

## System integrity (kiro-audit mirror)

A high-signal subset of `kiro-audit`'s checks, rendered in the GUI so you don't have to drop to a terminal. The authoritative checks live in `usr/local/bin/kiro-audit` (in `edu-system-files`); this section is the user-readable summary.

### Microcode

#### `intel-ucode` / `amd-ucode`
- **What it checks:** for each ucode package you have installed, the matching `/boot/{vendor}-ucode.img` file is actually present.
- **Why it matters:** archiso can strip the `.img` file even though pacman still lists the package as installed — leaving the kernel without the early-microcode load. Specific real bug, hence the dedicated check.
- **PASS means:** the package is installed *and* the image file exists in `/boot/`.
- **FAIL means + fix:** the image is missing. Run `sudo pacman -S {vendor}-ucode` to reinstall and restore the file.
- **`(none installed)` WARN:** neither `intel-ucode` nor `amd-ucode` is installed — you're booting without early microcode loading. Install the one that matches your CPU (`intel-ucode` for Intel, `amd-ucode` for AMD).

### Audio stack (PipeWire)

#### `pipewire` / `pipewire-pulse` / `wireplumber`
- **What it checks:** the three packages that make up the modern audio stack.
- **Why it matters:** PipeWire is the audio server; pipewire-pulse provides PulseAudio compatibility; wireplumber is the session/policy manager. All three should be installed.
- **PASS means:** package installed.
- **FAIL means + fix:** `sudo pacman -S pipewire pipewire-pulse wireplumber`.

#### `pulseaudio not installed`
- **What it checks:** the old PulseAudio daemon is **not** present.
- **Why it matters:** PulseAudio and PipeWire-pulse cannot both own the audio socket — having both installed produces broken sound.
- **PASS means:** pulseaudio is absent.
- **FAIL means + fix:** `sudo pacman -R pulseaudio` (and any sub-packages it pulls).

### ZRAM

#### `zram-generator`
- **What it checks:** the `zram-generator` package is installed.
- **Why it matters:** this is the systemd-native way to provision a compressed-RAM swap device at boot. Kiro relies on it.
- **PASS means:** installed.
- **FAIL means + fix:** `sudo pacman -S zram-generator`.

#### `/dev/zram0 present`
- **What it checks:** the device node exists.
- **PASS means:** the zram generator ran and created the device.
- **FAIL means + fix:** check `/etc/systemd/zram-generator.conf` and reboot, or run `sudo systemctl start systemd-zram-setup@zram0`.

#### `active as swap`
- **What it checks:** `/dev/zram0` shows up in `swapon`.
- **PASS means:** it's in use as swap.
- **FAIL means + fix:** swap activation failed; `journalctl -u systemd-zram-setup@zram0` will say why.

#### `compression`
- **What it checks:** the compression algorithm reported by `zramctl`.
- **PASS means:** `zstd` (Kiro's choice — best ratio/speed balance).
- **WARN means:** something other than zstd (`lz4`, `lzo`) — works fine but suboptimal compression. Edit `/etc/systemd/zram-generator.conf` and reboot.

### Log rotation

#### `logrotate.timer enabled`
- **What it checks:** `systemctl is-enabled logrotate.timer` succeeds.
- **Why it matters:** file-based logs (`pacman.log`, Xorg, app logs) grow without bound otherwise. journald rotates separately via `SystemMaxUse` — this timer covers everything else.
- **PASS means:** timer is enabled (persistent across reboots).
- **FAIL means + fix:** `sudo systemctl enable logrotate.timer`. A fresh install can show *active* but *disabled* — `is-enabled` is the authoritative answer.

### Calamares cleanup

#### `calamares removed` / `mkinitcpio-archiso removed` / `kiro-calamares-config-next removed`
- **What it checks:** each of these install-time-only packages is **gone** from the installed system.
- **Why it matters:** the Calamares installer is meant to remove itself and its helpers after a successful install. If any of them is still present, the install partially failed or self-cleanup was skipped.
- **PASS means:** package is gone.
- **FAIL means + fix:** `sudo pacman -R {package}`. If it cascades into unrelated packages, stop and ask — that's a sign something else is off.

#### `installer leftovers`
- **What it checks:** none of the live-only Calamares/archiso artifacts (specific files the install should have wiped) are still present.
- **PASS means:** no leftovers (`none`).
- **FAIL means + fix:** specific paths are listed in red. Delete them manually after confirming they're not in use; `kiro-audit --fix` may handle some.

### Package integrity (pacman -Qk)

#### `packages with missing files` / `all packages intact`
- **What it checks:** `pacman -Qk` lists packages whose files are missing from disk. A short ignore list filters known-noisy packages (`ohmychadwm-git`, `bind`, `cups`, `nfs-utils`).
- **Why it matters:** if a package thinks it owns files that are gone, future upgrades may overwrite custom changes or skip needed installs.
- **PASS means:** all packages intact (0 missing files).
- **FAIL means + fix:** for each listed package, `sudo pacman -S {package}` to restore the missing files.

### Failed systemd units

#### `failed units`
- **What it checks:** the count from `systemctl --failed`.
- **Why it matters:** a unit fails for a reason — service won't start, mount won't apply, timer can't fire. Often points at a misconfiguration the user never sees.
- **PASS means:** `0`.
- **FAIL means + fix:** each failed unit is listed; for each, run `systemctl status {unit}` and `journalctl -u {unit} -b` to see what went wrong.

---

## Userspace tuning

Five small system-level tweaks shipped by `edu-system-files` that change behavior without depending on a specific kernel. Adopted from a Garuda comparison study on 2026-05-28 — full rationale in `kiro-iso/KIRO-VS-GARUDA.md`.

### OOM daemon (systemd-oomd)

#### `systemd-oomd enabled`
- **What it checks:** `systemctl is-enabled systemd-oomd` returns success.
- **Why it matters:** the kernel's built-in OOM killer only fires after memory is completely exhausted — by which point the desktop has already spent seconds swapping itself into unresponsiveness. systemd-oomd watches PSI memory pressure and intervenes earlier, killing the worst offender (typically a runaway browser tab or IDE) before everything else suffers.
- **PASS means:** the service is set to start at every boot.
- **FAIL means + fix:** the service is masked or disabled. Run `sudo systemctl enable systemd-oomd`. The ATT audit's `--fix` mode can do this for you.

#### `systemd-oomd active`
- **What it checks:** `systemctl is-active systemd-oomd` returns success.
- **Why it matters:** even if enabled, the service has to actually be running to protect you in the current session.
- **PASS means:** the daemon is alive and watching memory pressure right now.
- **FAIL means + fix:** the daemon crashed or was stopped. Run `sudo systemctl start systemd-oomd` and check `journalctl -u systemd-oomd -b` for the cause.

### Intel ME blacklist

#### `blacklist-intel-me.conf`
- **What it checks:** `/etc/modprobe.d/blacklist-intel-me.conf` exists and contains `blacklist mei` + `blacklist mei_me`.
- **Why it matters:** the Intel Management Engine is an always-on co-processor with network access and a long CVE history (e.g. SA-00086). Blacklisting the kernel-side drivers closes the userspace attack surface and one always-loaded driver. (It does NOT disable ME itself — only BIOS or `me_cleaner` can.)
- **PASS means:** the blacklist file is in place. AMD machines don't have mei to begin with — this still PASSes (the file is harmless on AMD).
- **FAIL means + fix:** the file is missing — reinstall the `edu-system-files-git` package: `sudo pacman -S edu-system-files-git`.

#### `mei/mei_me not loaded`
- **What it checks:** neither `mei` nor `mei_me` shows up in `lsmod`.
- **Why it matters:** the blacklist file only takes effect on next boot (or when the initramfs is rebuilt). If the modules are still loaded, the blacklist isn't yet active.
- **PASS means:** the modules are not loaded — either because they're blacklisted and you've rebooted, or because you have an AMD machine.
- **WARN means + fix:** the file is there but the modules are still loaded. Rebuild the initramfs (`sudo mkinitcpio -P`) and reboot — or just reboot if you haven't since installing the package.

### Bluetooth USB reset

#### `bluetooth-usb.conf (btusb reset=1)`
- **What it checks:** `/etc/modprobe.d/bluetooth-usb.conf` exists and sets `options btusb reset=1`.
- **Why it matters:** forces a USB-level reset on every probe of a Bluetooth USB controller. Fixes the common "Bluetooth works after a cold boot but never wakes up after suspend/resume" issue on Intel AX200/AX201/AX210 and Realtek RTL8822 combo cards.
- **PASS means:** the option file is in place; btusb will reset cleanly on each load.
- **FAIL means + fix:** file missing — reinstall `edu-system-files-git`.

### Kernel zswap

#### `disable-zswap.conf tmpfile`
- **What it checks:** `/etc/tmpfiles.d/disable-zswap.conf` exists.
- **Why it matters:** Kiro uses `zram-generator` to provide a compressed-RAM swap device. If the kernel's built-in `zswap` is also enabled, every page gets compressed twice — once by zswap as it caches, then again by zstd as it hits zram. Wasted CPU, no extra capacity.
- **PASS means:** the tmpfile is shipped and will turn zswap off at every boot.
- **FAIL means + fix:** file missing — reinstall `edu-system-files-git`.

#### `runtime state (N or 0)`
- **What it checks:** reads `/sys/module/zswap/parameters/enabled` — should read `N` or `0`.
- **Why it matters:** the tmpfile only fires at boot. If you just installed the package, the runtime state may still be `Y` until next boot.
- **PASS means:** zswap is off right now.
- **FAIL (`Y` or `1`) means + fix:** apply the tmpfile immediately with `sudo systemd-tmpfiles --create /etc/tmpfiles.d/disable-zswap.conf`. Survives reboots automatically afterwards.
- **WARN (`?`) means:** `/sys/module/zswap/parameters/enabled` was unreadable. Your kernel may not expose zswap (very unusual — every mainline kernel since 3.11 / 2013 has it).

### NetworkManager loopback

#### `unmanaged-lo.conf`
- **What it checks:** `/etc/NetworkManager/conf.d/unmanaged-lo.conf` exists with `unmanaged-devices=interface-name:lo`.
- **Why it matters:** recent NetworkManager versions try to manage the loopback (`lo`) interface and log a benign warning about it on every boot. The loopback needs no management — it's brought up by systemd and never changes. This file silences the noise; no behavior change otherwise.
- **PASS means:** the drop-in is in place; NM stays away from `lo`.
- **FAIL means + fix:** file missing — reinstall `edu-system-files-git`.

---

## Maintenance

The authoritative state for each row lives in `usr/share/archlinux-tweak-tool/dev_gui.py`. When a new `_row(...)` call is added there, an entry must be added in this file in the same change — otherwise the row appears in the UI with no user-readable meaning.

The file is installed by the package to `/usr/share/doc/archlinux-tweak-tool/DEV_PAGE_GLOSSARY.md`. The Dev page's "What do these rows mean?" link opens this local copy in a detected GUI text editor (mousepad / gedit / kate / geany / ...) — no browser dependency, no internet round-trip, and ATT runs as root without tripping browser self-protection.

If you spot a row in the UI that isn't documented here, please open an issue.
