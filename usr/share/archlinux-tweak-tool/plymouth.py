import glob
import os
import subprocess


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


def list_available_packages():
    try:
        all_pkgs = set(subprocess.run(
            ["pacman", "-Ssq", "^plymouth-theme"],
            capture_output=True, text=True
        ).stdout.strip().splitlines())
        installed = set(subprocess.run(
            ["pacman", "-Qq"],
            capture_output=True, text=True
        ).stdout.strip().splitlines())
        return sorted(all_pkgs - installed)
    except Exception:
        return []


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
                if "splash" in line and "quiet" in line:
                    ok.append(path)
                else:
                    missing.append(path)
                break
    return missing, ok


def check_grub_splash():
    """Return True if GRUB_CMDLINE_LINUX_DEFAULT contains both quiet and splash."""
    try:
        for line in open("/etc/default/grub").readlines():
            s = line.strip()
            if s.startswith("GRUB_CMDLINE_LINUX_DEFAULT"):
                return "splash" in s and "quiet" in s
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
