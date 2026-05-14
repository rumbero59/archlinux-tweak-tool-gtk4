import glob
import json
import os
import subprocess


KERNEL_CMDLINE = "/etc/kernel/cmdline"
_AVAILABLE_CACHE = "/etc/att/cache_plymouth_available.json"

_LOADER_CONF_PATHS = [
    "/boot/loader/loader.conf",
    "/boot/efi/loader/loader.conf",
    "/boot/EFI/loader/loader.conf",
    "/efi/loader/loader.conf",
    "/EFI/loader/loader.conf",
]

_ENTRY_DIRS = [
    "/boot/loader/entries",
    "/boot/efi/loader/entries",
    "/boot/EFI/loader/entries",
    "/efi/loader/entries",
    "/EFI/loader/entries",
]


def list_themes():
    themes_dir = "/usr/share/plymouth/themes"
    try:
        return sorted(
            d for d in os.listdir(themes_dir)
            if os.path.isdir(os.path.join(themes_dir, d))
        )
    except OSError:
        return []


def get_current_theme():
    try:
        result = subprocess.run(
            ["plymouth-set-default-theme"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _sync_db_mtime():
    try:
        mtimes = [os.path.getmtime(f) for f in glob.glob("/var/lib/pacman/sync/*.db")]
        return max(mtimes) if mtimes else 0.0
    except OSError:
        return 0.0


def list_available_packages():
    try:
        cache = json.loads(open(_AVAILABLE_CACHE).read())
        if cache.get("db_mtime") == _sync_db_mtime():
            return cache["packages"]
    except (OSError, KeyError, ValueError):
        pass

    try:
        all_pkgs = set(subprocess.run(
            ["pacman", "-Ssq", "^plymouth-theme"],
            capture_output=True, text=True
        ).stdout.strip().splitlines())
        installed = set(subprocess.run(
            ["pacman", "-Qq"],
            capture_output=True, text=True
        ).stdout.strip().splitlines())
        result = sorted(all_pkgs - installed)
    except Exception:
        return []

    try:
        with open(_AVAILABLE_CACHE, "w") as f:
            json.dump({"packages": result, "db_mtime": _sync_db_mtime()}, f)
    except OSError:
        pass

    return result


def detect_bootloader():
    if any(os.path.exists(p) for p in _LOADER_CONF_PATHS):
        return "systemd-boot"
    if os.path.exists("/etc/default/grub"):
        return "grub"
    try:
        result = subprocess.run(["pacman", "-Qq", "limine"], capture_output=True, text=True)
        if result.returncode == 0:
            return "limine"
    except Exception:
        pass
    try:
        result = subprocess.run(["pacman", "-Qq", "refind"], capture_output=True, text=True)
        if result.returncode == 0:
            return "refind"
    except Exception:
        pass
    return "unknown"


def find_systemd_boot_entries():
    entries = []
    for d in _ENTRY_DIRS:
        entries.extend(glob.glob(os.path.join(d, "*.conf")))
    return sorted(set(entries))


def check_kernel_cmdline_exists():
    return os.path.exists(KERNEL_CMDLINE)


def check_kernel_cmdline_splash():
    """Return True if /etc/kernel/cmdline contains both quiet and splash as tokens."""
    try:
        tokens = open(KERNEL_CMDLINE).read().split()
        return "quiet" in tokens and "splash" in tokens
    except OSError:
        return False


def check_systemd_boot_splash():
    """Return (entries_missing, entries_ok) — lists of entry file paths."""
    missing = []
    ok = []
    for path in find_systemd_boot_entries():
        try:
            lines = open(path).readlines()
        except OSError:
            continue
        for line in lines:
            if line.strip().startswith("options"):
                tokens = line.split()
                if "splash" in tokens and "quiet" in tokens:
                    ok.append(path)
                else:
                    missing.append(path)
                break
    return missing, ok


def check_grub_splash():
    """Return True if GRUB_CMDLINE_LINUX_DEFAULT contains both quiet and splash as tokens.

    Accepts single- or double-quoted values; token-matches (so `nosplash` does not
    count as splash).
    """
    try:
        for line in open("/etc/default/grub").readlines():
            s = line.strip()
            if s.startswith("GRUB_CMDLINE_LINUX_DEFAULT"):
                _, _, rest = s.partition("=")
                rest = rest.strip()
                if rest and rest[0] in ("'", '"'):
                    rest = rest[1:]
                if rest and rest[-1] in ("'", '"'):
                    rest = rest[:-1]
                tokens = rest.split()
                return "quiet" in tokens and "splash" in tokens
    except OSError:
        pass
    return False


def check_hooks_order():
    """Return True if mkinitcpio HOOKS has plymouth before encrypt/sd-encrypt/lvm2."""
    try:
        for line in open("/etc/mkinitcpio.conf").readlines():
            s = line.strip()
            if s.startswith("HOOKS="):
                hooks = s.replace("HOOKS=", "").strip("()").split()
                if "plymouth" not in hooks:
                    return True  # not using plymouth hooks, no ordering concern
                plymouth_idx = hooks.index("plymouth")
                for danger in ("encrypt", "sd-encrypt", "lvm2"):
                    if danger in hooks and hooks.index(danger) < plymouth_idx:
                        return False
                return True
    except OSError:
        pass
    return True


def is_virtual_machine():
    try:
        result = subprocess.run(
            ["systemd-detect-virt"],
            capture_output=True, text=True
        )
        return result.stdout.strip() != "none"
    except Exception:
        return False


def detect_gpu():
    _module_map = {
        "i915": "intel",
        "amdgpu": "amd",
        "radeon": "amd",
        "nouveau": "nvidia",
        "nvidia": "nvidia",
    }
    try:
        lines = subprocess.run(["lsmod"], capture_output=True, text=True).stdout.splitlines()
        loaded = {line.split()[0] for line in lines if line.split()}
        for module, vendor in _module_map.items():
            if module in loaded:
                return vendor
    except Exception:
        pass
    return None


def get_gpu_name():
    try:
        out = subprocess.run(["lspci"], capture_output=True, text=True).stdout
        for line in out.splitlines():
            lower = line.lower()
            if "vga" in lower or "display controller" in lower or "3d controller" in lower:
                return line.split(":", 2)[-1].strip() if ":" in line else line
    except Exception:
        pass
    return None


def get_kms_module(gpu):
    return {"amd": "amdgpu", "intel": "i915"}.get(gpu)


def check_early_kms(module):
    try:
        for line in open("/etc/mkinitcpio.conf").readlines():
            s = line.strip()
            if s.startswith("MODULES="):
                inner = s[s.index("(") + 1:s.rindex(")")]
                return module in inner.split()
    except (OSError, ValueError):
        pass
    return False


def is_dracut():
    """Return True if dracut is the active initramfs generator."""
    return os.path.exists("/usr/bin/dracut")


def check_dracut_plymouth_enabled():
    """True if the plymouth dracut module is active.

    Active means either:
      - any /etc/dracut.conf.d/*.conf adds plymouth via add_dracutmodules+= , or
      - /etc/dracut.conf itself adds it, or
      - the 90plymouth module ships on disk (dracut auto-picks it up by default
        once the plymouth package is installed, unless explicitly omitted)
    """
    conf_files = ["/etc/dracut.conf"] + sorted(glob.glob("/etc/dracut.conf.d/*.conf"))
    omitted = False
    added = False
    for path in conf_files:
        try:
            for line in open(path).readlines():
                s = line.strip()
                if s.startswith("#") or "=" not in s:
                    continue
                if "add_dracutmodules" in s and "plymouth" in s:
                    added = True
                if "omit_dracutmodules" in s and "plymouth" in s:
                    omitted = True
        except OSError:
            continue
    if omitted:
        return False
    if added:
        return True
    return os.path.isdir("/usr/lib/dracut/modules.d/90plymouth")
