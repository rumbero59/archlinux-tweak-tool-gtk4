# ============================================================
# Authors: Erik Dubois
# ============================================================
# sched-ext / scx scheduler selector — backend logic.
#
# Exposes the CachyOS/Kiro sched-ext schedulers through scx_loader's five
# friendly modes (Auto / Gaming / LowLatency / PowerSave / Server). Default
# OFF: nothing here changes the running scheduler until the user opts in, so
# the EEVDF/BORE baseline that kiro-audit validates is untouched on a fresh
# system. Gated on /sys/kernel/sched_ext so every control no-ops on kernels
# without sched-ext (linux-hardened / LTS) without being hardcoded per-kernel.
#
# VERIFY-ON-BOX (tracked while trialling, MASTER_TODO §3 P2):
#   * scxctl flag spelling (-m / --mode, mode casing) on the shipped scx_loader
#   * which TOML path the installed scx_loader actually reads
#     (/etc/scx_loader.toml as CachyOS uses, vs /etc/scx_loader/config.toml)
# Both are isolated below behind constants + debug_print so a live test can
# correct them without touching the GUI.

import os

import functions as fn
from functions import GLib

# ── Configuration ──────────────────────────────────────────────────────
SCX_SCHEDS_PACKAGE = "scx-scheds"
SCX_LOADER_PACKAGE = "scx_loader"
SCX_LOADER_SERVICE = "scx_loader.service"
SCX_LOADER_TOML = "/etc/scx_loader.toml"  # path CachyOS's own GUI writes
SCHED_EXT_SYSFS = "/sys/kernel/sched_ext"

# scx_loader's five modes — friendlier than raw scheduler names. Order is the
# order shown in the dropdown.
MODES = ["Auto", "Gaming", "LowLatency", "PowerSave", "Server"]


# ── Detection / readout ────────────────────────────────────────────────


def sched_ext_supported():
    """Return True when the running kernel exposes the sched-ext framework."""
    return os.path.isdir(SCHED_EXT_SYSFS)


def _read_sysfs(relpath):
    try:
        with open(os.path.join(SCHED_EXT_SYSFS, relpath), encoding="utf-8") as handle:
            return handle.read().strip()
    except OSError:
        return ""


def get_active_scheduler():
    """Return a human-readable name for the scheduler currently in charge."""
    if not sched_ext_supported():
        return "default (no sched-ext)"
    state = _read_sysfs("state")
    if state and state != "disabled":
        name = _read_sysfs("root/ops")
        if name:
            return name if name.startswith("scx_") else f"scx_{name}"
        return "scx (loaded)"
    return "default (EEVDF / BORE)"


def scheds_installed():
    """Return True when the scx-scheds package is installed."""
    return fn.check_package_installed(SCX_SCHEDS_PACKAGE)


def loader_installed():
    """Return True when the scx_loader package is installed."""
    return fn.check_package_installed(SCX_LOADER_PACKAGE)


def loader_active():
    """Return True when scx_loader.service is running."""
    return fn.check_service(SCX_LOADER_SERVICE)


# ── Actions ────────────────────────────────────────────────────────────


def _run_terminal(script):
    """Run a privileged shell script in a terminal so the user sees progress."""
    proc = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )
    proc.wait()


def install_scx(self, _widget, refresh=None):
    """Install scx-scheds + scx_loader (leaves the service OFF — opt-in stays explicit)."""
    if scheds_installed() and loader_installed():
        GLib.idle_add(fn.show_in_app_notification, self, "scx-scheds is already installed")
        return
    fn.log_subsection("Install scx-scheds")

    def _do_install():
        try:
            cmd = f"pacman -S --noconfirm --needed {SCX_SCHEDS_PACKAGE} {SCX_LOADER_PACKAGE}"
            fn.debug_print(f"Terminal: {cmd}")
            _run_terminal(
                f"""
set -o pipefail
{cmd}
RESULT=$?
echo ''
[ $RESULT -eq 0 ] && echo '✓ Installation successful' || echo '✗ Installation failed'
echo ''
echo 'scx_loader.service is left DISABLED — enable it from ATT by picking a mode.'
echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            )
            fn.invalidate_pkg_cache()
            if scheds_installed():
                fn.log_success("scx-scheds installed")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-scheds has been installed")
            else:
                fn.log_warn("scx-scheds installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-scheds installation failed or was cancelled")
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to install scx-scheds: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def _persist_mode(mode):
    """Write the chosen mode to scx_loader's TOML so it survives a reboot."""
    try:
        line = f'default_mode = "{mode}"\n'
        fn.debug_print(f"Write {SCX_LOADER_TOML}: {line.strip()}")
        with open(SCX_LOADER_TOML, "w", encoding="utf-8") as handle:
            handle.write("# Managed by ArchLinux Tweak Tool — scx scheduler block\n")
            handle.write(line)
    except OSError as error:
        fn.log_warn(f"Could not persist scx mode to {SCX_LOADER_TOML}: {error}")


def apply_mode(self, mode, refresh=None):
    """Enable scx_loader (the opt-in) and switch it to the chosen mode."""
    if mode not in MODES:
        return
    fn.log_subsection(f"Apply scx mode: {mode}")

    def _do_apply():
        try:
            # Enabling the service is the user's explicit opt-in; ships OFF.
            enable_cmd = ["systemctl", "enable", "--now", SCX_LOADER_SERVICE]
            fn.debug_print(f"Terminal: {' '.join(enable_cmd)}")
            fn.subprocess.run(enable_cmd, capture_output=True, text=True)

            # Switch the running scheduler's mode. `start` if nothing is loaded
            # yet, `switch` if scx_loader is already driving — try switch, fall
            # back to start. Flag spelling is VERIFY-ON-BOX (see header).
            for action in ("switch", "start"):
                scxctl = ["scxctl", action, "-m", mode]
                fn.debug_print(f"Terminal: {' '.join(scxctl)}")
                result = fn.subprocess.run(scxctl, capture_output=True, text=True)
                if result.returncode == 0:
                    break

            _persist_mode(mode)
            fn.log_success(f"scx mode set to {mode}")
            GLib.idle_add(fn.show_in_app_notification, self, f"Scheduler mode set to {mode}")
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to apply scx mode: {error}")

    fn.threading.Thread(target=_do_apply, daemon=True).start()


def disable_scx(self, _widget, refresh=None):
    """Stop scx and fall back to the kernel default (EEVDF / BORE)."""
    fn.log_subsection("Disable scx — back to default scheduler")

    def _do_disable():
        try:
            stop = ["scxctl", "stop"]
            fn.debug_print(f"Terminal: {' '.join(stop)}")
            fn.subprocess.run(stop, capture_output=True, text=True)

            disable_cmd = ["systemctl", "disable", "--now", SCX_LOADER_SERVICE]
            fn.debug_print(f"Terminal: {' '.join(disable_cmd)}")
            fn.subprocess.run(disable_cmd, capture_output=True, text=True)

            try:
                if os.path.exists(SCX_LOADER_TOML):
                    os.remove(SCX_LOADER_TOML)
                    fn.debug_print(f"Removed {SCX_LOADER_TOML}")
            except OSError:
                pass

            fn.log_success("scx disabled — kernel default restored")
            GLib.idle_add(fn.show_in_app_notification, self, "Scheduler back to default (EEVDF / BORE)")
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to disable scx: {error}")

    fn.threading.Thread(target=_do_disable, daemon=True).start()
