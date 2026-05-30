# ============================================================
# Authors: Erik Dubois
# ============================================================
# sched-ext / scx scheduler selector — backend logic.
#
# Drives the CachyOS sched-ext stack the same way CachyOS's own Kernel Manager
# does: the `scx_loader` daemon (DBus org.scx.Loader, unit scx_loader.service)
# controlled by the `scxctl` CLI, with persistence in /etc/scx_loader.toml.
# Both binaries ship in the official `extra/scx-tools` package, which depends on
# `scx-scheds` (the scheduler binaries). Default OFF: nothing changes the
# running scheduler until the user picks one and Applies, so the EEVDF/BORE
# baseline kiro-audit validates is untouched on a fresh system. Gated on
# /sys/kernel/sched_ext so every control no-ops on kernels without sched-ext.
#
# scxctl model (verified against the upstream scxctl README):
#   * `scxctl start -s <sched> [-m <mode>]` — scheduler is REQUIRED, so the GUI
#     must offer a scheduler, not modes alone.
#   * `scxctl switch [-s <sched>] [-m <mode>]` — adjust a running scheduler.
#   * `scxctl stop` — back to the kernel default.
#   Scheduler names are passed WITHOUT the scx_ prefix (lavd, bpfland); modes
#   are lowercase (auto/gaming/lowlatency/powersave/server). The TOML keeps the
#   full name (scx_lavd) and capitalised mode (Gaming).

import os

import functions as fn
from functions import GLib

# ── Configuration ──────────────────────────────────────────────────────
SCX_TOOLS_PACKAGE = "scx-tools"  # ships scx_loader + scxctl, deps on scx-scheds
SCX_LOADER_SERVICE = "scx_loader.service"
SCX_LOADER_TOML = "/etc/scx_loader.toml"  # path CachyOS's Kernel Manager writes
SCHED_EXT_SYSFS = "/sys/kernel/sched_ext"

# scx_loader's five modes — friendlier flag-sets per scheduler. UI casing;
# lowercased before handing to scxctl, kept as-is in the TOML.
MODES = ["Auto", "Gaming", "LowLatency", "PowerSave", "Server"]

# Curated schedulers from scx-scheds, with the role each is tuned for. Full
# scx_ name (for the TOML); the scx_ prefix is stripped for scxctl.
SCHEDULERS = [
    ("scx_lavd", "Gaming / low-latency desktop"),
    ("scx_bpfland", "Interactive desktop"),
    ("scx_rusty", "General / throughput"),
    ("scx_flash", "Audio / multimedia"),
    ("scx_p2dq", "General, scalable"),
    ("scx_tickless", "Servers / power saving"),
]


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


def _scxctl_get():
    """Return scxctl's report of the running scheduler, or '' if unavailable."""
    try:
        result = fn.subprocess.run(["scxctl", "get"], capture_output=True, text=True)
    except (FileNotFoundError, OSError):
        return ""
    return (result.stdout or "").strip()


def get_active_scheduler():
    """Return a human-readable name for the scheduler currently in charge."""
    if not sched_ext_supported():
        return "default (no sched-ext)"
    state = _read_sysfs("state")
    if not state or state == "disabled":
        return "default (EEVDF / BORE)"
    # A scheduler is attached. scxctl knows its name + mode; sysfs only knows
    # "enabled". Prefer scxctl, fall back to the sysfs name file when present.
    report = _scxctl_get()
    if report:
        return report
    name = _read_sysfs("root/ops")
    if name:
        return name if name.startswith("scx_") else f"scx_{name}"
    return "scx (loaded)"


def tools_installed():
    """Return True when scx-tools (scx_loader + scxctl) is installed."""
    return fn.check_package_installed(SCX_TOOLS_PACKAGE)


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
    """Install scx-tools (scx_loader + scxctl + scx-scheds) — service stays OFF."""
    if tools_installed():
        GLib.idle_add(fn.show_in_app_notification, self, "scx-tools is already installed")
        return
    fn.log_subsection("Install scx-tools")

    def _do_install():
        try:
            cmd = f"pacman -S --noconfirm --needed {SCX_TOOLS_PACKAGE}"
            fn.debug_print(f"Terminal: {cmd}")
            _run_terminal(
                f"""
set -o pipefail
{cmd}
RESULT=$?
echo ''
[ $RESULT -eq 0 ] && echo '✓ Installation successful' || echo '✗ Installation failed'
echo ''
echo 'scx_loader.service is left DISABLED — enable it from ATT by picking a scheduler + mode.'
echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            )
            fn.invalidate_pkg_cache()
            if tools_installed():
                fn.log_success("scx-tools installed")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-tools has been installed")
            else:
                fn.log_warn("scx-tools installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-tools installation failed or was cancelled")
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to install scx-tools: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_scx(self, _widget, refresh=None):
    """Tear scx down and remove scx-tools (leaves scx-scheds, a harmless dep)."""
    if not tools_installed():
        GLib.idle_add(fn.show_in_app_notification, self, "scx-tools is not installed")
        return
    fn.log_subsection("Remove scx-tools")

    def _do_remove():
        try:
            cmd = f"pacman -R --noconfirm {SCX_TOOLS_PACKAGE}"
            fn.debug_print(f"Terminal: scxctl stop; systemctl disable --now {SCX_LOADER_SERVICE}; {cmd}")
            _run_terminal(
                f"""
set +e
scxctl stop 2>/dev/null
systemctl disable --now {SCX_LOADER_SERVICE} 2>/dev/null
rm -f {SCX_LOADER_TOML}
{cmd}
RESULT=$?
echo ''
[ $RESULT -eq 0 ] && echo '✓ scx-tools removed' || echo '✗ Removal failed'
echo 'scx-scheds (the schedulers) is left installed — remove it manually if you want it gone too.'
echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            )
            fn.invalidate_pkg_cache()
            if not tools_installed():
                fn.log_success("scx-tools removed")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-tools has been removed")
            else:
                fn.log_warn("scx-tools removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "scx-tools removal failed or was cancelled")
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to remove scx-tools: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def _persist(sched, mode):
    """Write the chosen scheduler + mode to scx_loader's TOML so it survives a reboot."""
    try:
        fn.debug_print(f"Write {SCX_LOADER_TOML}: default_sched={sched} default_mode={mode}")
        with open(SCX_LOADER_TOML, "w", encoding="utf-8") as handle:
            handle.write("# Managed by ArchLinux Tweak Tool — scx scheduler block\n")
            handle.write(f'default_sched = "{sched}"\n')
            handle.write(f'default_mode = "{mode}"\n')
    except OSError as error:
        fn.log_warn(f"Could not persist scx config to {SCX_LOADER_TOML}: {error}")


def apply_scheduler(self, sched, mode, refresh=None):
    """Enable scx_loader (the opt-in) and load the chosen scheduler in the chosen mode."""
    if sched not in dict(SCHEDULERS) or mode not in MODES:
        return
    short = sched[len("scx_"):] if sched.startswith("scx_") else sched
    cli_mode = mode.lower()
    fn.log_subsection(f"Apply scx scheduler: {sched} ({mode})")

    def _do_apply():
        try:
            _persist(sched, mode)

            enable_cmd = ["systemctl", "enable", "--now", SCX_LOADER_SERVICE]
            fn.debug_print(f"Terminal: {' '.join(enable_cmd)}")
            fn.subprocess.run(enable_cmd, capture_output=True, text=True)

            # `switch` adjusts a running scheduler; `start` boots one when none
            # is loaded yet. Try switch first, fall back to start.
            switched = False
            for action in ("switch", "start"):
                scxctl = ["scxctl", action, "-s", short, "-m", cli_mode]
                fn.debug_print(f"Terminal: {' '.join(scxctl)}")
                result = fn.subprocess.run(scxctl, capture_output=True, text=True)
                if result.returncode == 0:
                    switched = True
                    break
                if result.stderr:
                    fn.debug_print(f"scxctl {action} stderr: {result.stderr.strip()}")

            if switched:
                fn.log_success(f"scx scheduler set to {sched} ({mode})")
                GLib.idle_add(fn.show_in_app_notification, self, f"Scheduler set to {sched} ({mode})")
            else:
                fn.log_warn("scxctl could not load the scheduler")
                GLib.idle_add(fn.show_in_app_notification, self, "Could not load scheduler — see the log")
            if refresh:
                GLib.idle_add(refresh)
        except FileNotFoundError:
            fn.log_error("scxctl not found — install scx-tools first")
            GLib.idle_add(fn.show_in_app_notification, self, "scxctl not found — install scx-tools first")
        except Exception as error:
            fn.log_error(f"Failed to apply scx scheduler: {error}")

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
        except FileNotFoundError:
            # scxctl gone but service still around — just stop the service.
            fn.subprocess.run(["systemctl", "disable", "--now", SCX_LOADER_SERVICE], capture_output=True, text=True)
            if refresh:
                GLib.idle_add(refresh)
        except Exception as error:
            fn.log_error(f"Failed to disable scx: {error}")

    fn.threading.Thread(target=_do_disable, daemon=True).start()
