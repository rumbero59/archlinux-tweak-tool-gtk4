# DISTRO_GUARDS.md

Single source of truth for all distro-conditional logic in ATT.
Update this file whenever a guard is added, removed, or changed.

**Purpose of guards:** Prevent ATT from breaking or conflicting with how a specific distro manages its own system. Guards are not feature flags and not branding — they exist because that distro owns that area and ATT must stay out of the way.

**Rules:**

- Guards are only removed when explicitly requested during active testing on that distro — never proactively.
- The detection/re-mapping block in `functions.py` is permanently frozen — never touch it.

---

## Distro Detection & Canonical Name Resolution

**File:** `functions.py` (bottom of module, runs at import time)

These are not guards — they are identity corrections. `fn.distr` is normalized here once so that every downstream guard can key off a stable canonical name without duplicating detection logic.

| Detected as | Canonical name | Condition |
| ----------- | -------------- | --------- |
| `manjaro` | `biglinux` | `/etc/os-release` contains "biglinux" |
| `arch` | `omarchy` | `/etc/plymouth/plymouthd.conf` contains "omarchy" OR `/etc/att/att-omarchy-marker` exists |

**Do not change this block** — all guards below depend on these names being stable.

---

## Tab Visibility Guards

**File:** `gui.py`

| Tab | Hidden on | Condition |
| --- | --------- | --------- |
| Plymouth | `artix` | artix has no systemd init |
| SDDM | `prismlinux` | `fn.distr not in _SDDM_HIDDEN_DISTROS` (set at top of `gui.py`) |
| SDDM | any distro | also hidden if `plasma-login` or `plasmalogin` service is enabled (not distro-keyed) |

---

## Per-Module Guards

### `kernel_distros.py`

| Distro | Effect |
| ------ | ------ |
| `arch` | Requires `pacman-hook-kernel-install` (nemesis-repo) when systemd-boot is active |

### `plymouth_gui.py`

| Distro | Effect |
| ------ | ------ |
| `omarchy` | Default reset theme = `omarchy` |
| `cachyos` | Default reset theme = `cachyos-bootanimation` |
| `prismlinux` | Default reset theme = `prismlinux-theme` |
| `omarchy` | Writes `/etc/att/att-omarchy-marker` after theme reset |
| *(others)* | Reset button is hidden when no default theme is mapped |

### `user_gui.py`

| Distro | Effect |
| ------ | ------ |
| `arch` | Visudo section shown in User tab |

---

## Quick Reference — Distro Guard Inventory

| Distro | Guards | Tabs affected | Modules affected |
| ------ | ------ | ------------- | ---------------- |
| `arch` | yes | — | `kernel_distros.py`, `user_gui.py` |
| `archcraft` | none | — | pending hardware test |
| `artix` | yes | Plymouth hidden | `gui.py` |
| `biglinux` | re-map only | — | `functions.py` |
| `cachyos` | yes | — | `plymouth_gui.py` |
| `garuda` | none | — | pending hardware test |
| `kiro` | none | — | primary target |
| `manjaro` | none | — | pending hardware test |
| `nyarch` | none | — | pending hardware test |
| `omarchy` | re-map only | — | `functions.py`, `plymouth_gui.py` |
| `prismlinux` | yes | SDDM hidden | `gui.py`, `plymouth_gui.py` |
