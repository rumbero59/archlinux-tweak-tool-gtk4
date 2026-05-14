# ============================================================
# Authors: Erik Dubois
# ============================================================

import os
import re
import glob
import functions as fn
import subprocess

KERNELS = [
    {
        "pkg": "linux",
        "headers": "linux-headers",
        "label": "Linux",
        "description": "Vanilla Arch kernel",
        "group": "Standard Arch",
        "url": "https://github.com/archlinux/linux",
    },
    {
        "pkg": "linux-lts",
        "headers": "linux-lts-headers",
        "label": "Linux LTS",
        "description": "Long-term support kernel",
        "group": "Standard Arch",
        "url": "https://www.kernel.org/",
    },
    {
        "pkg": "linux-zen",
        "headers": "linux-zen-headers",
        "label": "Linux Zen",
        "description": "Tuned for desktop responsiveness",
        "group": "Standard Arch",
        "url": "https://github.com/zen-kernel/zen-kernel",
    },
    {
        "pkg": "linux-hardened",
        "headers": "linux-hardened-headers",
        "label": "Linux Hardened",
        "description": "Security-focused kernel",
        "group": "Standard Arch",
        "url": "https://github.com/anthraxx/linux-hardened",
    },
    {
        "pkg": "linux-rt",
        "headers": "linux-rt-headers",
        "label": "Linux RT",
        "description": "Real-time kernel",
        "group": "Standard Arch",
        "url": "https://wiki.linuxfoundation.org/realtime/start",
    },
    {
        "pkg": "linux-rt-lts",
        "headers": "linux-rt-lts-headers",
        "label": "Linux RT LTS",
        "description": "Real-time kernel (LTS base)",
        "group": "Standard Arch",
        "url": "https://wiki.linuxfoundation.org/realtime/start",
    },
    {
        "pkg": "linux-cachyos",
        "headers": "linux-cachyos-headers",
        "label": "Linux CachyOS",
        "description": "CachyOS default kernel",
        "requires_chaotic": True,
        "group": "CachyOS",
        "url": "https://github.com/CachyOS/linux-cachyos",
    },
    {
        "pkg": "linux-cachyos-bore",
        "headers": "linux-cachyos-bore-headers",
        "label": "Linux CachyOS BORE",
        "description": "CachyOS with BORE scheduler",
        "requires_chaotic": True,
        "group": "CachyOS",
        "url": "https://github.com/CachyOS/linux-cachyos",
    },
    {
        "pkg": "linux-cachyos-lts",
        "headers": "linux-cachyos-lts-headers",
        "label": "Linux CachyOS LTS",
        "description": "CachyOS long-term support kernel",
        "requires_chaotic": True,
        "group": "CachyOS",
        "url": "https://github.com/CachyOS/linux-cachyos",
    },
    {
        "pkg": "linux-cachyos-rc",
        "headers": "linux-cachyos-rc-headers",
        "label": "Linux CachyOS RC",
        "description": "CachyOS release candidate kernel",
        "requires_chaotic": True,
        "group": "CachyOS",
        "url": "https://github.com/CachyOS/linux-cachyos",
    },
    {
        "pkg": "linux-cjktty",
        "headers": "linux-cjktty-headers",
        "label": "Linux CJKTTY",
        "description": "CachyOS kernel with CJK TTY font support",
        "requires_chaotic": True,
        "group": "CachyOS",
        "url": "https://github.com/CachyOS/linux-cachyos",
    },
    {
        "pkg": "linux-xanmod-lts",
        "headers": "linux-xanmod-lts-headers",
        "label": "Linux Xanmod LTS",
        "description": "Xanmod long-term support kernel",
        "requires_chaotic": True,
        "group": "Xanmod",
        "url": "https://xanmod.org/",
    },
    {
        "pkg": "linux-xanmod-rt",
        "headers": "linux-xanmod-rt-headers",
        "label": "Linux Xanmod RT",
        "description": "Xanmod real-time kernel",
        "requires_chaotic": True,
        "group": "Xanmod",
        "url": "https://xanmod.org/",
    },
    {
        "pkg": "linux-xanmod-x64v2",
        "headers": "linux-xanmod-x64v2-headers",
        "label": "Linux Xanmod x64v2",
        "description": "Xanmod optimized for x86-64-v2 (post-2009 CPUs)",
        "requires_chaotic": True,
        "group": "Xanmod",
        "url": "https://xanmod.org/",
        "cpu_compat": {"flags": ["sse4_2", "popcnt", "ssse3"]},
    },
    {
        "pkg": "linux-xanmod-x64v3",
        "headers": "linux-xanmod-x64v3-headers",
        "label": "Linux Xanmod x64v3",
        "description": "Xanmod optimized for x86-64-v3 (Haswell+)",
        "requires_chaotic": True,
        "group": "Xanmod",
        "url": "https://xanmod.org/",
        "cpu_compat": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    },
    {
        "pkg": "linux-xanmod-edge-x64v3",
        "headers": "linux-xanmod-edge-x64v3-headers",
        "label": "Linux Xanmod Edge x64v3",
        "description": "Xanmod bleeding-edge, x86-64-v3",
        "requires_chaotic": True,
        "group": "Xanmod",
        "url": "https://xanmod.org/",
        "cpu_compat": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    },
    {
        "pkg": "linux-lqx",
        "headers": "linux-lqx-headers",
        "label": "Linux Liquorix",
        "description": "Desktop/multimedia optimized kernel",
        "requires_chaotic": True,
        "group": "Liquorix",
        "url": "https://liquorix.net/",
    },
    {
        "pkg": "linux-mainline",
        "headers": "linux-mainline-headers",
        "label": "Linux Mainline",
        "description": "Latest upstream mainline kernel",
        "requires_chaotic": True,
        "group": "Mainline",
        "url": "https://www.kernel.org/",
    },
    {
        "pkg": "linux-mainline-x64v3",
        "headers": "linux-mainline-x64v3-headers",
        "label": "Linux Mainline x64v3",
        "description": "Mainline optimized for x86-64-v3",
        "requires_chaotic": True,
        "group": "Mainline",
        "url": "https://www.kernel.org/",
        "cpu_compat": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    },
    {
        "pkg": "linux-lts515",
        "headers": "linux-lts515-headers",
        "label": "Linux LTS 5.15",
        "description": "Long-term support kernel 5.15",
        "requires_chaotic": True,
        "group": "Specific LTS versions",
        "url": "https://www.kernel.org/",
    },
    {
        "pkg": "linux-lts61",
        "headers": "linux-lts61-headers",
        "label": "Linux LTS 6.1",
        "description": "Long-term support kernel 6.1",
        "requires_chaotic": True,
        "group": "Specific LTS versions",
        "url": "https://www.kernel.org/",
    },
    {
        "pkg": "linux-lts612",
        "headers": "linux-lts612-headers",
        "label": "Linux LTS 6.12",
        "description": "Long-term support kernel 6.12",
        "requires_chaotic": True,
        "group": "Specific LTS versions",
        "url": "https://www.kernel.org/",
    },
    {
        "pkg": "linux-lts66",
        "headers": "linux-lts66-headers",
        "label": "Linux LTS 6.6",
        "description": "Long-term support kernel 6.6",
        "requires_chaotic": True,
        "group": "Specific LTS versions",
        "url": "https://www.kernel.org/",
    },
    # ── x86-64 microarch level builds ────────────────────────────
    {
        "pkg": "linux-x64v2",
        "headers": "linux-x64v2-headers",
        "label": "Linux x64v2",
        "description": "Arch kernel optimized for x86-64-v2",
        "requires_chaotic": True,
        "group": "x86-64 microarch level builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"flags": ["sse4_2", "popcnt", "ssse3"]},
    },
    {
        "pkg": "linux-x64v3",
        "headers": "linux-x64v3-headers",
        "label": "Linux x64v3",
        "description": "Arch kernel optimized for x86-64-v3 (Haswell+)",
        "requires_chaotic": True,
        "group": "x86-64 microarch level builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    },
    {
        "pkg": "linux-x64v4",
        "headers": "linux-x64v4-headers",
        "label": "Linux x64v4",
        "description": "Arch kernel optimized for x86-64-v4 (AVX-512)",
        "requires_chaotic": True,
        "group": "x86-64 microarch level builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"flags": ["avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"]},
    },
    # ── AMD Zen builds ───────────────────────────────────────────
    {
        "pkg": "linux-znver2",
        "headers": "linux-znver2-headers",
        "label": "Linux Znver2",
        "description": "Optimized for AMD Zen 2 CPUs",
        "requires_chaotic": True,
        "group": "AMD Zen builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"vendor": "AMD", "min_zen": 2},
    },
    {
        "pkg": "linux-znver3",
        "headers": "linux-znver3-headers",
        "label": "Linux Znver3",
        "description": "Optimized for AMD Zen 3 CPUs",
        "requires_chaotic": True,
        "group": "AMD Zen builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"vendor": "AMD", "min_zen": 3},
    },
    {
        "pkg": "linux-znver4",
        "headers": "linux-znver4-headers",
        "label": "Linux Znver4",
        "description": "Optimized for AMD Zen 4 CPUs",
        "requires_chaotic": True,
        "group": "AMD Zen builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"vendor": "AMD", "min_zen": 4},
    },
    {
        "pkg": "linux-znver5",
        "headers": "linux-znver5-headers",
        "label": "Linux Znver5",
        "description": "Optimized for AMD Zen 5 CPUs",
        "requires_chaotic": True,
        "group": "AMD Zen builds",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"vendor": "AMD", "min_zen": 5},
    },
    # ── Specialty ────────────────────────────────────────────────
    {
        "pkg": "linux-nitrous",
        "headers": "linux-nitrous-headers",
        "label": "Linux Nitrous",
        "description": "Performance-tuned kernel",
        "requires_chaotic": True,
        "group": "Specialty",
        "url": "https://github.com/archlinux/linux",
    },
    {
        "pkg": "linux-tachyon",
        "headers": "linux-tachyon-headers",
        "label": "Linux Tachyon",
        "description": "High-performance kernel",
        "requires_chaotic": True,
        "group": "Specialty",
        "url": "https://github.com/archlinux/linux",
    },
    {
        "pkg": "linux-vfio",
        "headers": "linux-vfio-headers",
        "label": "Linux VFIO",
        "description": "Kernel with VFIO/GPU passthrough patches",
        "requires_chaotic": True,
        "group": "Specialty",
        "url": "https://github.com/archlinux/linux",
    },
    {
        "pkg": "linux-vfio-lts",
        "headers": "linux-vfio-lts-headers",
        "label": "Linux VFIO LTS",
        "description": "LTS kernel with VFIO/GPU passthrough patches",
        "requires_chaotic": True,
        "group": "Specialty",
        "url": "https://github.com/archlinux/linux",
    },
    {
        "pkg": "linux-vfio-x64v3",
        "headers": "linux-vfio-x64v3-headers",
        "label": "Linux VFIO x64v3",
        "description": "VFIO kernel optimized for x86-64-v3",
        "requires_chaotic": True,
        "group": "Specialty",
        "url": "https://github.com/archlinux/linux",
        "cpu_compat": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    },
]


CACHYOS_CACHE_PATH = "/usr/share/archlinux-tweak-tool/data/cachyos_kernels.txt"

_CACHYOS_REPO_COMPAT = {
    "cachyos-v3": {"flags": ["avx", "avx2", "bmi1", "bmi2"]},
    "cachyos-v4": {"flags": ["avx512f", "avx512bw", "avx512cd", "avx512dq", "avx512vl"]},
}


def _build_cachyos_dicts(pkg_repo_pairs, already_shown_pkgs):
    kernels = []
    for pkg, repo in pkg_repo_pairs:
        if pkg in already_shown_pkgs:
            continue
        suffix = pkg.removeprefix("linux-cachyos-").replace("-", " ").title()
        if "cachyos" in pkg:
            label = f"Linux CachyOS {suffix}" if suffix != pkg else "Linux CachyOS"
        else:
            label = pkg.replace("-", " ").title()
        entry = {
            "pkg": pkg,
            "headers": f"{pkg}-headers",
            "label": label,
            "description": "CachyOS kernel",
            "group": "CachyOS (native repo)",
            "url": "https://github.com/CachyOS/linux-cachyos",
        }
        compat = _CACHYOS_REPO_COMPAT.get(repo)
        if compat:
            entry["cpu_compat"] = compat
        kernels.append(entry)
    return kernels


def load_cachyos_kernel_cache(already_shown_pkgs):
    """Return kernel dicts from cache file, or None if no cache exists."""
    try:
        with open(CACHYOS_CACHE_PATH) as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return None
    except Exception:
        return None
    pairs = []
    for line in lines:
        if ":" in line:
            pkg, repo = line.split(":", 1)
        else:
            pkg, repo = line, "cachyos"
        pairs.append((pkg, repo))
    return _build_cachyos_dicts(pairs, already_shown_pkgs)


def get_cachyos_available_kernels(already_shown_pkgs):
    """Query pacman -Sl for cachyos linux-* kernels, save to cache, return filtered dicts."""
    try:
        result = subprocess.run(
            ["pacman", "-Sl"], capture_output=True, text=True, check=False, timeout=10
        )
        seen = set()
        all_pairs = []
        for line in result.stdout.splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            repo, pkg = parts[0], parts[1]
            if not repo.startswith("cachyos"):
                continue
            if not pkg.startswith("linux-"):
                continue
            if "-headers" in pkg or "firmware" in pkg or "hotspot" in pkg:
                continue
            if pkg in seen:
                continue
            seen.add(pkg)
            all_pairs.append((pkg, repo))
        try:
            with open(CACHYOS_CACHE_PATH, "w") as f:
                f.write("\n".join(f"{pkg}:{repo}" for pkg, repo in all_pairs) + "\n")
        except Exception:
            pass
        return _build_cachyos_dicts(all_pairs, already_shown_pkgs)
    except Exception:
        return []


def get_cpu_info():
    """Return dict with vendor, flags (set), family, model from /proc/cpuinfo."""
    info = {"vendor": "", "flags": set(), "family": 0, "model": 0}
    try:
        with open("/proc/cpuinfo", "r") as f:
            for line in f:
                if line.startswith("vendor_id"):
                    info["vendor"] = line.split(":")[1].strip()
                elif line.startswith("cpu family"):
                    info["family"] = int(line.split(":")[1].strip())
                elif line.startswith("model\t"):
                    info["model"] = int(line.split(":")[1].strip())
                elif line.startswith("flags"):
                    info["flags"] = set(line.split(":")[1].strip().split())
                if info["vendor"] and info["flags"] and info["family"] and info["model"]:
                    break
    except Exception:
        pass
    return info


def _amd_zen_generation(family, model):
    """Return AMD Zen generation number (1-5) or 0 if not Zen."""
    if family == 23:   # 0x17 — Zen / Zen+ / Zen 2
        return 2 if model >= 0x31 else 1
    if family == 24:   # 0x18 — some Zen 2 mobile
        return 2
    if family == 25:   # 0x19 — Zen 3 / Zen 4
        return 4 if model >= 0x60 else 3
    if family >= 26:   # 0x1A — Zen 5+
        return 5
    return 0


def is_kernel_compatible(k, cpu_info):
    """Return True if the kernel can run on the given CPU."""
    compat = k.get("cpu_compat")
    if not compat:
        return True

    # Flag check (x86-64 microarch levels)
    required_flags = compat.get("flags", [])
    if required_flags and not set(required_flags).issubset(cpu_info["flags"]):
        return False

    # Vendor check
    vendor = compat.get("vendor", "")
    if vendor and vendor not in cpu_info["vendor"]:
        return False

    # AMD Zen generation check
    min_zen = compat.get("min_zen", 0)
    if min_zen:
        gen = _amd_zen_generation(cpu_info["family"], cpu_info["model"])
        if gen < min_zen:
            return False

    return True


def get_running_kernel():
    """Return the running kernel package name, e.g. 'linux' or 'linux-lts'."""
    try:
        uname = subprocess.check_output(["uname", "-r"], text=True).strip()
        result = subprocess.check_output(
            ["pacman", "-Qo", f"/usr/lib/modules/{uname}/pkgbase"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        # Output format: "/path/to/file is owned by package-name version"
        # Extract package name (second to last element)
        parts = result.split()
        if len(parts) >= 2:
            return parts[-2]
        return None
    except Exception:
        return None


def get_installed_kernels():
    """Return dict of {pkg_name: version} for all installed packages (one pacman call)."""
    try:
        output = subprocess.check_output(["pacman", "-Q"], text=True, stderr=subprocess.DEVNULL)
        result = {}
        for line in output.splitlines():
            parts = line.split()
            if len(parts) == 2:
                result[parts[0]] = parts[1]
        return result
    except Exception:
        return {}


def is_systemd_boot():
    """Return True if systemd-boot is the active bootloader."""
    try:
        result = subprocess.run(
            ["bootctl", "is-installed"],
            capture_output=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def _resolve_kernel_for_entry(version, linux_path):
    """Return (pkg_name, is_orphan) for a boot entry.

    Strategy:
      1. If `version:` is set, read /usr/lib/modules/<version>/pkgbase — that file
         is owned by the kernel package and its contents are the package name.
         Missing file means the kernel was uninstalled but the .conf remains.
      2. Else if `linux:` basename starts with "vmlinuz-", strip the prefix.
      3. Else no kernel can be resolved (e.g. firmware/automatic entries).
    """
    if version:
        pkgbase_path = f"/usr/lib/modules/{version}/pkgbase"
        try:
            with open(pkgbase_path, "r", encoding="utf-8") as f:
                return f.read().strip(), False
        except FileNotFoundError:
            return None, True
        except Exception:
            return None, False

    if linux_path:
        basename = linux_path.rsplit("/", 1)[-1]
        if basename.startswith("vmlinuz-"):
            return basename[len("vmlinuz-"):], False

    return None, False


def get_boot_entries():
    """Return list of (id, title, kernel_pkg) tuples from bootctl list.

    Orphan entries (whose kernel package is no longer installed) are filtered
    out so they never reach the dropdown.
    """
    try:
        output = subprocess.check_output(
            ["bootctl", "list", "--no-pager"],
            text=True, stderr=subprocess.DEVNULL
        )
        entries = []
        current = {}
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped:
                if current.get("id") and current.get("title"):
                    kernel_pkg, is_orphan = _resolve_kernel_for_entry(
                        current.get("version"), current.get("linux")
                    )
                    if not is_orphan:
                        entries.append((current["id"], current["title"], kernel_pkg))
                current = {}
                continue
            if stripped.startswith("id:"):
                current["id"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("title:"):
                raw_title = stripped.split(":", 1)[1].strip()
                if "reported/absent" in raw_title:
                    current = {}
                    continue
                current["title"] = re.sub(r'\s*\((default|selected|current)\)', '', raw_title).strip()
            elif stripped.startswith("version:"):
                current["version"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("linux:"):
                current["linux"] = stripped.split(":", 1)[1].strip()
        # Flush trailing entry if file did not end with a blank line
        if current.get("id") and current.get("title"):
            kernel_pkg, is_orphan = _resolve_kernel_for_entry(
                current.get("version"), current.get("linux")
            )
            if not is_orphan:
                entries.append((current["id"], current["title"], kernel_pkg))

        # Drop machine-ID-stamped duplicates: among entries sharing the same
        # kernel_pkg, keep the one whose title has no 32-char hex blob.
        _mid_re = re.compile(r'\([0-9a-f]{32}\)', re.IGNORECASE)
        best = {}
        for i, (_, title, kernel_pkg) in enumerate(entries):
            if not kernel_pkg:
                continue
            has_hash = bool(_mid_re.search(title))
            if kernel_pkg not in best or (best[kernel_pkg][1] and not has_hash):
                best[kernel_pkg] = (i, has_hash)
        keep = {idx for idx, _ in best.values()} | {i for i, (_, _, kp) in enumerate(entries) if not kp}
        return [e for i, e in enumerate(entries) if i in keep]
    except Exception:
        return []


def get_default_boot_entry():
    """Return the current default boot entry ID."""
    try:
        output = subprocess.check_output(
            ["bootctl", "status", "--no-pager"],
            text=True, stderr=subprocess.DEVNULL
        )
        for line in output.splitlines():
            if "Default Entry:" in line or "default entry:" in line.lower():
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def set_default_boot_entry(entry_id):
    """Set the default boot entry using bootctl set-default. Returns True on success."""
    try:
        result = subprocess.run(
            ["bootctl", "set-default", entry_id],
            shell=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            fn.log_error(f"bootctl set-default failed: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        fn.log_error(f"set_default_boot_entry error: {e}")
        return False


LIMINE_CONF_PATHS = [
    "/boot/limine/limine.conf",
    "/boot/limine.conf",
    "/limine/limine.conf",
    "/limine.conf",
]


def get_limine_conf_path():
    """Return first found limine.conf path, or None."""
    for path in LIMINE_CONF_PATHS:
        if os.path.exists(path):
            return path
    return None


def is_limine():
    """Return True if a limine.conf is found on the system."""
    return get_limine_conf_path() is not None


def get_limine_boot_entries():
    """Return list of (index_str, title) parsed from limine.conf.

    All entry lines at any depth are counted for correct default_entry indexing.
    Only level-2 (//) leaf entries are returned — containers and level-1 entries
    (group headers, EFI fallback) are excluded from the dropdown.
    """
    path = get_limine_conf_path()
    if not path:
        return []
    raw = []
    index = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped.startswith("/"):
                    continue
                level = len(stripped) - len(stripped.lstrip("/"))
                title = stripped[level:].strip().replace("\\/", "/").lstrip("+").strip()
                if not title:
                    continue
                index += 1
                raw.append((index, level, title))
    except Exception:
        pass
    entries = []
    for i, (idx, level, title) in enumerate(raw):
        if level != 2:
            continue
        is_container = i + 1 < len(raw) and raw[i + 1][1] > level
        if not is_container:
            entries.append((str(idx), title))
    return entries


def get_default_limine_entry():
    """Return current default_entry value from limine.conf, or None."""
    path = get_limine_conf_path()
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().lower().startswith("default_entry:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def set_default_limine_entry(index):
    """Write default_entry: <index> into limine.conf. Returns True on success."""
    path = get_limine_conf_path()
    if not path:
        fn.log_error("set_default_limine_entry: limine.conf not found")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_lines = []
        found = False
        for line in lines:
            if line.strip().lower().startswith("default_entry:"):
                new_lines.append(f"default_entry: {index}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            insert_pos = 0
            for i, line in enumerate(new_lines):
                if line.strip().lower().startswith("timeout:"):
                    insert_pos = i + 1
                    break
            new_lines.insert(insert_pos, f"default_entry: {index}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        fn.log_error(f"set_default_limine_entry error: {e}")
        return False


REFIND_CONF_PATHS = [
    "/boot/EFI/refind/refind.conf",
    "/boot/efi/EFI/refind/refind.conf",
    "/efi/EFI/refind/refind.conf",
    "/boot/refind/refind.conf",
]


def get_refind_conf_path():
    """Return first found refind.conf path, or None."""
    for path in REFIND_CONF_PATHS:
        if os.path.exists(path):
            return path
    return None


def is_refind():
    """Return True if a refind.conf is found on the system."""
    return get_refind_conf_path() is not None


_REFIND_DEFAULT_SEL_RE = re.compile(
    r'^\s*default_selection\s+(?:"([^"]*)"|(\S+))\s*(?:#.*)?$'
)

_REFIND_FOLD_RE = re.compile(r'^\s*#?\s*fold_linux_kernels\s+\S+\s*(?:#.*)?$')


def _ensure_fold_linux_kernels_false(lines):
    """Ensure refind.conf has an active `fold_linux_kernels false` line.

    rEFInd folds multiple vmlinuz-* into one menu tile by default. When folded,
    default_selection matches only the folded parent tag, so sub-kernels cannot
    be pre-selected — ATT's dropdown silently does nothing. Forcing it to false
    makes each kernel its own top-level entry so substring match works.
    """
    target = "fold_linux_kernels false\n"
    for i, line in enumerate(lines):
        if _REFIND_FOLD_RE.match(line):
            if line.strip() == "fold_linux_kernels false":
                return lines, "unchanged"
            lines[i] = target
            return lines, "replaced"
    lines.append(target)
    return lines, "appended"


def _parse_refind_default_selection(line):
    """If `line` is an unconditional default_selection directive, return its value.

    Time-conditional lines like `default_selection Maintenance 23:30 2:00` have
    trailing tokens after the value and are skipped (return None), so they are
    never overwritten by set_default_refind_entry().
    """
    m = _REFIND_DEFAULT_SEL_RE.match(line)
    if not m:
        return None
    return m.group(1) if m.group(1) is not None else m.group(2)


def get_refind_boot_entries():
    """Return list of (value, label) for installed kernels rEFInd will auto-detect.

    Scans /boot for vmlinuz-* files (the standard rEFInd auto-detect target on
    CachyOS) and pairs each with its installed package version when available.
    `value` is the vmlinuz filename so rEFInd's substring match picks the
    auto-detected entry regardless of menu order.
    """
    entries = []
    installed = get_installed_kernels()
    for path in sorted(glob.glob("/boot/vmlinuz-*")):
        basename = path.rsplit("/", 1)[-1]
        pkg = basename[len("vmlinuz-"):]
        version = installed.get(pkg, "")
        label = f"{pkg} {version}".strip()
        entries.append((basename, label))
    return entries


def get_default_refind_entry():
    """Return the last unconditional default_selection value, or None."""
    path = get_refind_conf_path()
    if not path:
        return None
    value = None
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                parsed = _parse_refind_default_selection(line)
                if parsed is not None:
                    value = parsed
    except Exception:
        pass
    return value


def set_default_refind_entry(value):
    """Replace the last unconditional default_selection, or append a new one.

    Time-conditional default_selection lines are preserved. Returns True on success.
    """
    path = get_refind_conf_path()
    if not path:
        fn.log_error("set_default_refind_entry: refind.conf not found")
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        last_idx = -1
        for i, line in enumerate(lines):
            if _parse_refind_default_selection(line) is not None:
                last_idx = i
        if last_idx >= 0:
            lines[last_idx] = f'default_selection "{value}"\n'
        else:
            insert_pos = len(lines)
            for i, line in enumerate(lines):
                if line.lstrip().startswith("timeout "):
                    insert_pos = i + 1
                    break
            lines.insert(insert_pos, f'default_selection "{value}"\n')

        lines, fold_status = _ensure_fold_linux_kernels_false(lines)
        if fold_status == "replaced":
            fn.log_info(
                "refind.conf: replaced existing fold_linux_kernels line with "
                "`fold_linux_kernels false` so per-kernel default_selection takes effect"
            )
        elif fold_status == "appended":
            fn.log_info(
                "refind.conf: appended `fold_linux_kernels false` "
                "(required for per-kernel default_selection on multi-kernel systems)"
            )

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        fn.log_success(f'refind.conf updated: default_selection "{value}"')
        return True
    except Exception as e:
        fn.log_error(f"set_default_refind_entry error: {e}")
        return False


def is_grub():
    """Return True if GRUB is the active bootloader."""
    return os.path.exists("/boot/grub/grub.cfg")


def is_grub_default_saved():
    """Return True if GRUB_DEFAULT=saved is set in /etc/default/grub."""
    try:
        with open("/etc/default/grub", "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("GRUB_DEFAULT="):
                    val = stripped.split("=", 1)[1].strip().strip('"\'')
                    return val == "saved"
    except Exception:
        pass
    return False


def set_grub_default_saved():
    """Set GRUB_DEFAULT=saved in /etc/default/grub. Returns True on success."""
    path = "/etc/default/grub"
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if re.search(r'^GRUB_DEFAULT=', content, re.MULTILINE):
            content = re.sub(r'^GRUB_DEFAULT=.*$', 'GRUB_DEFAULT=saved', content, flags=re.MULTILINE)
        else:
            content += "\nGRUB_DEFAULT=saved\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        fn.log_success("GRUB_DEFAULT=saved written to /etc/default/grub")
        return True
    except Exception as e:
        fn.log_error(f"set_grub_default_saved error: {e}")
        return False


def get_grub_boot_entries():
    """Return list of (index_str, title) for menuentries in grub.cfg.

    Top-level entries use a plain integer index.  Entries inside a submenu use
    GRUB's '<submenu_idx>><sub_entry_idx>' notation so grub-set-default accepts
    them.  Fallback initramfs entries are excluded.
    """
    path = "/boot/grub/grub.cfg"
    entries = []
    top_level_index = 0
    depth = 0
    in_submenu = False
    submenu_index = 0
    sub_entry_index = 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                opens = stripped.count("{")
                closes = stripped.count("}")
                if depth == 0 and (stripped.startswith("menuentry ") or stripped.startswith("submenu ")):
                    m = re.match(r"""^(?:menuentry|submenu)\s+['"](.+?)['"]""", stripped)
                    if m:
                        title = m.group(1)
                        if stripped.startswith("menuentry "):
                            entries.append((str(top_level_index), title))
                        else:
                            in_submenu = True
                            submenu_index = top_level_index
                            sub_entry_index = 0
                        top_level_index += 1
                elif depth == 1 and in_submenu and stripped.startswith("menuentry "):
                    m = re.match(r"""^menuentry\s+['"](.+?)['"]""", stripped)
                    if m:
                        title = m.group(1)
                        if "fallback" not in title.lower():
                            entries.append((f"{submenu_index}>{sub_entry_index}", title))
                        sub_entry_index += 1
                depth += opens - closes
                if depth == 0:
                    in_submenu = False
    except Exception:
        pass
    return entries


def get_default_grub_entry():
    """Return saved_entry value from /boot/grub/grubenv, or None."""
    try:
        with open("/boot/grub/grubenv", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("saved_entry="):
                    return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None


def set_default_grub_entry(index):
    """Set the GRUB default entry via grub-set-default. Returns True on success."""
    try:
        result = subprocess.run(
            ["grub-set-default", index],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            fn.log_error(f"grub-set-default failed: {result.stderr.strip()}")
            return False
        return True
    except Exception as e:
        fn.log_error(f"set_default_grub_entry error: {e}")
        return False


def install_kernel(self, pkg, headers):
    """Install kernel and headers with detailed logging."""
    fn.log_subsection(f"Installing kernel: {pkg}")
    fn.debug_print(f"Headers: {headers}")
    script = f"""#!/bin/bash
tput setaf 6
echo "================================================================"
echo "  Installing kernel: {pkg}"
echo "  Headers: {headers}"
echo "================================================================"
tput sgr0

pacman -S "{pkg}" "{headers}" --noconfirm --needed
RESULT=$?

echo
if [ $RESULT -eq 0 ]; then
    tput setaf 2
    echo "================================================================"
    echo "  ✓ Successfully installed {pkg}"
    echo "================================================================"
    tput sgr0
else
    tput setaf 1
    echo "================================================================"
    echo "  ✗ Failed to install {pkg}"
    echo "================================================================"
    tput sgr0
fi

echo
echo "###############################################################################"
echo "###                DONE - YOU CAN CLOSE THIS WINDOW                        ####"
echo "###############################################################################"
read -p 'Press Enter to close...'
"""
    fn.debug_print(f"Terminal cmd: {script}")
    process = subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
    fn.show_in_app_notification(self, f"Installing {pkg}...")
    return process


def remove_kernel(self, pkg, headers):
    """Remove kernel and headers with detailed logging."""
    fn.log_subsection(f"Removing kernel: {pkg}")
    fn.debug_print(f"Headers: {headers}")
    script = f"""#!/bin/bash
tput setaf 6
echo "================================================================"
echo "  Removing kernel: {pkg}"
echo "  Headers: {headers}"
echo "================================================================"
tput sgr0

pacman -R "{headers}" "{pkg}" --noconfirm 2>/dev/null || pacman -R "{pkg}" --noconfirm
RESULT=$?

echo
if [ $RESULT -eq 0 ]; then
    tput setaf 2
    echo "================================================================"
    echo "  ✓ Successfully removed {pkg}"
    echo "================================================================"
    tput sgr0
else
    tput setaf 1
    echo "================================================================"
    echo "  ✗ Failed to remove {pkg}"
    echo "================================================================"
    tput sgr0
fi

echo
echo "###############################################################################"
echo "###                DONE - YOU CAN CLOSE THIS WINDOW                        ####"
echo "###############################################################################"
read -p 'Press Enter to close...'
"""
    fn.debug_print(f"Terminal cmd: {script}")
    process = subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    fn.show_in_app_notification(self, f"Removing {pkg}...")
    return process


def run_grub_update(self):
    """Launch a separate alacritty to run grub-install + grub-mkconfig. Returns Popen or None if not a GRUB system."""
    if not (os.path.isfile("/usr/bin/grub-mkconfig") and os.path.isfile("/boot/grub/grub.cfg")):
        return None
    fn.log_subsection("Updating GRUB...")
    fn.debug_print("run_grub_update: launching grub-install + grub-mkconfig in terminal")
    fn.show_in_app_notification(self, "Updating GRUB...")
    script = """#!/bin/bash
tput setaf 6
echo "================================================================"
echo "  Updating GRUB..."
echo "================================================================"
tput sgr0

if [ -d /sys/firmware/efi ]; then
    if mountpoint -q /boot/efi 2>/dev/null; then
        EFI_DIR=/boot/efi
    elif mountpoint -q /efi 2>/dev/null; then
        EFI_DIR=/efi
    else
        EFI_DIR=/boot
    fi
    echo "UEFI system — EFI directory: $EFI_DIR"
    grub-install --target=x86_64-efi --efi-directory=$EFI_DIR --bootloader-id=GRUB
    INSTALL_RESULT=$?
    if [ $INSTALL_RESULT -eq 0 ]; then
        tput setaf 2
        echo "  ✓ grub-install completed"
        tput sgr0
    else
        tput setaf 1
        echo "  ✗ grub-install failed"
        tput sgr0
    fi
else
    echo "BIOS system — skipping grub-install (disk target unknown), running grub-mkconfig only"
fi

echo
grub-mkconfig -o /boot/grub/grub.cfg
RESULT=$?

echo
if [ $RESULT -eq 0 ]; then
    tput setaf 2
    echo "================================================================"
    echo "  ✓ GRUB configuration updated"
    echo "================================================================"
    tput sgr0
else
    tput setaf 1
    echo "================================================================"
    echo "  ✗ GRUB configuration update failed"
    echo "================================================================"
    tput sgr0
fi

echo
echo "###############################################################################"
echo "###                DONE - YOU CAN CLOSE THIS WINDOW                        ####"
echo "###############################################################################"
read -p 'Press Enter to close...'"""
    fn.debug_print(f"Terminal cmd: {script}")
    return subprocess.Popen(["alacritty", "-e", "bash", "-c", script])
