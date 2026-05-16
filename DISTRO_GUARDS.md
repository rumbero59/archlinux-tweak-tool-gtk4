# DISTRO_GUARDS.md

Single source of truth for all distro-conditional logic in ATT.
Update this file whenever a guard is added, removed, or changed.

---

## Distro Detection & Canonical Name Resolution

**File:** `functions.py` (bottom of module, runs at import time)

These are not guards — they are identity corrections. `fn.distr` is normalized here once so that every downstream guard can key off a stable canonical name without duplicating detection logic.

| Detected as | Canonical name | Condition                                                                                  |
|-------------|----------------|--------------------------------------------------------------------------------------------|
| `manjaro`   | `biglinux`     | `/etc/os-release` contains "biglinux"                                                      |
| `arch`      | `omarchy`      | `/etc/plymouth/plymouthd.conf` contains "omarchy" OR `/etc/att/att-omarchy-marker` exists  |

**Do not change this block** — all guards below depend on these names being stable.

---

## Tab Visibility Guards

**File:** `gui.py`

| Tab | Hidden on | Condition |
|-----|-----------|-----------|
| Fastfetch | `garuda` | `fn.distr != "garuda"` |
| Performance | `artix` | `fn.distr != "artix"` |
| Services | `artix` | `fn.distr != "artix"` |
| Plymouth | `artix` | `fn.distr != "artix"` |
| Locale | `artix` | `fn.distr != "artix"` |
| SDDM | `prismlinux` | `fn.distr not in _SDDM_HIDDEN_DISTROS` (set at top of `gui.py`) |
| SDDM | any distro | also hidden if `plasma-login` or `plasmalogin` service is enabled (not distro-keyed) |

---

## Per-Module Guards

### `desktopr.py`

| Distro | Effect |
|--------|--------|
| `archcraft` | Calls `fn.clear_skel_directory()` when applying a desktop environment |

### `shell_gui.py`

| Distro | Effect |
|--------|--------|
| `archcraft` | Fish tab hidden from shell stack |
| `archcraft` | "Apply fish" button hidden from Fish config section |

### `services_gui.py`

| Distro | Effect |
|--------|--------|
| `garuda`, `manjaro` | Audio sub-tab hidden from the Services stack |

### `kernel_distros.py`

| Distro | Effect |
|--------|--------|
| `arch` | Requires `pacman-hook-kernel-install` (nemesis-repo) when systemd-boot is active |

### `plymouth_gui.py`

| Distro | Effect |
|--------|--------|
| `omarchy` | Default reset theme = `omarchy` |
| `cachyos` | Default reset theme = `cachyos-bootanimation` |
| `prismlinux` | Default reset theme = `prismlinux-theme` |
| `omarchy` | Writes `/etc/att/att-omarchy-marker` after theme reset |
| *(others)* | Reset button is hidden (no known default) |

### `user_gui.py`

| Distro | Effect |
|--------|--------|
| `arch` | Visudo section shown in User tab |

---

## Quick Reference — Distro Guard Inventory

| Distro | Tabs affected | Modules affected |
|--------|---------------|-----------------|
| `arch` | — | `kernel_distros.py`, `user_gui.py` |
| `archcraft` | Shells (Fish hidden) | `desktopr.py`, `shell_gui.py` |
| `artix` | Performance, Services, Plymouth, Locale hidden | `gui.py` |
| `biglinux` | — (re-map only) | `functions.py` |
| `cachyos` | — | `plymouth_gui.py` |
| `garuda` | Fastfetch hidden; Services/Audio hidden | `gui.py`, `services_gui.py` |
| `manjaro` | Services/Audio hidden | `services_gui.py` |
| `omarchy` | — (re-map only) | `functions.py`, `plymouth_gui.py` |
| `prismlinux` | SDDM hidden | `gui.py`, `plymouth_gui.py` |
