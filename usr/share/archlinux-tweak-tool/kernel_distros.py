# ============================================================
# Authors: Erik Dubois
# ============================================================
# Distro-specific requirements for the kernel manager tab.
# Add a new entry here when a distro needs packages that are
# not available in standard Arch repos.
# ============================================================

import subprocess
import functions as fn


# Each distro maps to a list of required packages.
# Missing packages trigger a console warning + in-app notice + install dialog.
def _is_systemd_boot():
    try:
        return subprocess.run(["bootctl", "is-installed"], capture_output=True).returncode == 0
    except Exception:
        return False


DISTRO_REQUIREMENTS = {
    "arch": [
        {
            "pkg": "pacman-hook-kernel-install",
            "reason": "registers kernel-install hook for systemd-boot ESP layout",
            "repo": "nemesis-repo",
            "condition": _is_systemd_boot,
        }
    ],
    "garuda": [
        {
            "pkg": "garuda-dracut-support",
            "reason": "Garuda's dracut configuration and pacman hook for automatic initramfs regeneration",
            "repo": "garuda",
        }
    ],
    # Other distros added here as needed.
    # "manjaro": [...],
    # "artix": [...],
}


def get_missing_requirements():
    requirements = DISTRO_REQUIREMENTS.get(fn.distr, [])
    missing = []
    for req in requirements:
        condition = req.get("condition")
        if condition is not None and not condition():
            continue
        try:
            result = subprocess.run(["pacman", "-Q", req["pkg"]], capture_output=True)
            if result.returncode != 0:
                missing.append(req)
        except Exception:
            pass
    return missing
