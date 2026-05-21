# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import os
import pwd
import re

import functions as fn
from functions import GLib
from gi.repository import Gtk


# ── Tuned configuration ────────────────────────────────────────────────
TUNED_PACKAGE = "tuned"
TUNED_PPD_PACKAGE = "tuned-ppd"
TLP_PACKAGE = "tlp"
tuned_ppd_config = "/etc/tuned/ppd.conf"

# ── Other features configuration ───────────────────────────────────────
zram_config = "/etc/systemd/zram-generator.conf"
zram_disk_size = "/sys/block/zram0/disksize"
fstrim_timer = "fstrim.timer"
fstrim_service = "fstrim.service"


# ── Helper functions (service status) ──────────────────────────────────


def get_service_status(service):
    """Return a status label that includes enabled oneshot services."""
    if fn.check_service(service):
        return "<b>enabled</b>"

    try:
        output = fn.subprocess.run(
            ["systemctl", "is-enabled", service + ".service"],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        status = output.stdout.decode().strip()
        if status == "enabled":
            return "<b>enabled</b>"
        if status:
            return status
    except Exception as error:
        fn.debug_print(error)

    return "disabled"


def get_tuned_status_markup():
    """Build the tuned block status label text."""
    tuned_status = get_service_status("tuned")
    tuned_ppd_status = get_service_status("tuned-ppd")
    return "Tuned service : " + tuned_status + "   Tuned-PPD service : " + tuned_ppd_status


def refresh_tuned_status_label(self):
    """Refresh the visible tuned status labels."""
    if hasattr(self, "tuned_status_label"):
        GLib.idle_add(
            self.tuned_status_label.set_markup,
            "tuned service : " + get_service_status("tuned"),
        )
    if hasattr(self, "tuned_ppd_status_label"):
        GLib.idle_add(
            self.tuned_ppd_status_label.set_markup,
            "tuned-ppd service : " + get_service_status("tuned-ppd"),
        )


def refresh_performance_status_label(self):
    """Refresh the visible performance service status label."""
    refresh_tuned_status_label(self)


# ── Tuned block (tuned + tuned-ppd) ───────────────────────────────────


def install_tuned_tools(self, _widget):
    """Install tuned for dynamic power management."""
    if fn.check_package_installed("tuned"):
        fn.log_info("tuned is already installed")
        GLib.idle_add(fn.show_in_app_notification, self, "tuned is already installed")
        return
    fn.log_subsection("Install Tuned")

    def _do_install():
        try:
            for file_path in ["/etc/modprobe.d/tuned.conf"]:
                if fn.path.exists(file_path):
                    try:
                        fn.debug_print(f"Removing conflicting file: {file_path}")
                        fn.unlink(file_path)
                    except Exception as e:
                        fn.log_warn(f"Could not remove {file_path}: {e}")

            if fn.check_package_installed("power-profiles-daemon"):
                fn.debug_print("Removing power-profiles-daemon (conflicts with tuned-ppd)")
                fn.disable_service("power-profiles-daemon")
                proc = fn.launch_pacman_remove_in_terminal("power-profiles-daemon")
                if proc:
                    proc.wait()
                GLib.idle_add(fn.show_in_app_notification, self, "power-profiles-daemon removed")

            fn.log_info("Enabling services: tuned.service, tuned-ppd.service")
            fn.debug_print(f"Terminal: pacman -S --noconfirm --needed {TUNED_PACKAGE} {TUNED_PPD_PACKAGE}")
            fn.debug_print(f"Terminal: systemctl enable --now {TUNED_PACKAGE}")
            fn.debug_print(f"Terminal: systemctl enable --now {TUNED_PPD_PACKAGE}")
            install_script = f"""
set -o pipefail
pacman -S --noconfirm --needed {TUNED_PACKAGE} {TUNED_PPD_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo ''
    systemctl disable --now tlp 2>/dev/null && echo 'TLP disabled (conflicts with Tuned)' || true
    echo 'Enabling tuned...'
    systemctl enable --now {TUNED_PACKAGE} && echo '✓ tuned enabled' || echo '✗ Failed'
    echo 'Enabling tuned-ppd...'
    systemctl enable --now {TUNED_PPD_PACKAGE} && echo '✓ tuned-ppd enabled' || echo '✗ Failed'
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for tuned install terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — checking tuned installation")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed(TUNED_PACKAGE):
                fn.log_success("Tuned installed and enabled successfully")
                GLib.idle_add(fn.show_in_app_notification, self, "Tuned has been installed")
            else:
                fn.log_warn("Tuned installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "Tuned installation failed or was cancelled")
            GLib.idle_add(refresh_tuned_package_label, self)
            GLib.idle_add(refresh_tuned_buttons, self)
            GLib.idle_add(refresh_tuned_profile_choices, self)
            GLib.idle_add(refresh_tuned_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to install tuned: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_tuned_tools(self, _widget):
    """Remove tuned and tuned-ppd."""
    if not fn.check_package_installed(TUNED_PACKAGE):
        fn.log_info("tuned is not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "tuned is not installed")
        return
    fn.log_subsection("Remove Tuned")

    def _do_remove():
        try:
            fn.debug_print(f"Terminal: systemctl disable --now {TUNED_PACKAGE}")
            fn.debug_print(f"Terminal: systemctl disable --now {TUNED_PPD_PACKAGE}")
            fn.debug_print(f"Terminal: pacman -R --noconfirm {TUNED_PACKAGE} {TUNED_PPD_PACKAGE}")
            remove_script = f"""
echo 'Disabling tuned...'
systemctl disable --now {TUNED_PACKAGE} && echo '✓ tuned disabled' || echo '✗ Failed'
echo 'Disabling tuned-ppd...'
systemctl disable --now {TUNED_PPD_PACKAGE} && echo '✓ tuned-ppd disabled' || echo '✗ Failed'

echo ''
echo 'Removing packages...'
pacman -R --noconfirm {TUNED_PACKAGE} {TUNED_PPD_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {remove_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for tuned remove terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — checking tuned removal")
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed(TUNED_PACKAGE):
                fn.log_success("tuned and tuned-ppd removed")
                GLib.idle_add(fn.show_in_app_notification, self, "Tuned has been removed")
            else:
                fn.log_warn("tuned removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "Tuned removal failed or was cancelled")
            GLib.idle_add(refresh_tuned_package_label, self)
            GLib.idle_add(refresh_tuned_buttons, self)
            GLib.idle_add(refresh_tuned_profile_status, self)
            GLib.idle_add(refresh_tuned_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to remove tuned: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def refresh_tuned_package_label(self):
    """Refresh the tuned install/remove label after package state changes."""
    if not hasattr(self, "tuned_package_label"):
        return
    if fn.check_package_installed("tuned"):
        GLib.idle_add(self.tuned_package_label.set_markup, "tuned is <b>installed</b>")
    else:
        GLib.idle_add(self.tuned_package_label.set_text, "Install tuned for dynamic system tuning")


def refresh_tuned_buttons(self):
    """Refresh tuned button sensitivity after installing or removing."""
    tuned_buttons = [
        "enable_tuned",
        "disable_tuned",
        "restart_tuned",
        "restart_tuned_ppd",
        "tuned_profile_choices",
        "btn_apply_tuned_profile",
    ]
    # Check for the main tuned package - if installed, buttons should be enabled
    installed = fn.check_package_installed("tuned")
    for button_name in tuned_buttons:
        if hasattr(self, button_name):
            GLib.idle_add(getattr(self, button_name).set_sensitive, installed)


def enable_tuned_services(self, _widget):
    """Enable both tuned and tuned-ppd services via a terminal."""
    fn.log_subsection("Enable Tuned Services")
    try:
        script = (
            "systemctl disable --now tlp 2>/dev/null && echo 'TLP disabled (conflicts with Tuned)' || true\n"
            "echo 'Enabling tuned...'\n"
            "systemctl enable --now tuned && echo '✓ tuned enabled' || echo '✗ Failed'\n"
            "echo 'Enabling tuned-ppd...'\n"
            "systemctl enable --now tuned-ppd && echo '✓ tuned-ppd enabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling Tuned and Tuned-PPD...")

        def _wait_enable_tuned():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Tuned and Tuned-PPD enabled successfully")
            GLib.idle_add(fn.show_in_app_notification, self, "Tuned and Tuned-PPD have been enabled and started")
            GLib.idle_add(refresh_tuned_status_label, self)

        fn.threading.Thread(target=_wait_enable_tuned, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable tuned services: {error}")


def disable_tuned_services(self, _widget):
    """Disable both tuned and tuned-ppd services via a terminal."""
    fn.log_subsection("Disable Tuned Services")
    try:
        script = (
            "echo 'Disabling tuned...'\n"
            "systemctl disable --now tuned && echo '✓ tuned disabled' || echo '✗ Failed'\n"
            "echo 'Disabling tuned-ppd...'\n"
            "systemctl disable --now tuned-ppd && echo '✓ tuned-ppd disabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling Tuned and Tuned-PPD...")

        def _wait_disable_tuned():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Tuned and Tuned-PPD disabled successfully")
            GLib.idle_add(fn.show_in_app_notification, self, "Tuned and Tuned-PPD have been disabled and stopped")
            GLib.idle_add(refresh_tuned_status_label, self)

        fn.threading.Thread(target=_wait_disable_tuned, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable tuned services: {error}")


def restart_tuned_service(self, _widget):
    """Restart the tuned service via a terminal."""
    fn.log_subsection("Restart Tuned Service")
    try:
        script = (
            "echo 'Restarting tuned...'\n"
            "systemctl restart tuned && echo '✓ tuned restarted' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Restarting Tuned...")

        def _wait_restart_tuned():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Tuned service restarted")
            GLib.idle_add(fn.show_in_app_notification, self, "Tuned has been restarted")
            GLib.idle_add(refresh_performance_status_label, self)

        fn.threading.Thread(target=_wait_restart_tuned, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to restart tuned: {error}")


def restart_tuned_ppd_service(self, _widget):
    """Restart the tuned-ppd service via a terminal."""
    fn.log_subsection("Restart Tuned-PPD Service")
    try:
        script = (
            "echo 'Restarting tuned-ppd...'\n"
            "systemctl restart tuned-ppd && echo '✓ tuned-ppd restarted' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Restarting Tuned-PPD...")

        def _wait_restart_tuned_ppd():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Tuned-PPD service restarted")
            GLib.idle_add(fn.show_in_app_notification, self, "Tuned-PPD has been restarted")
            GLib.idle_add(refresh_performance_status_label, self)

        fn.threading.Thread(target=_wait_restart_tuned_ppd, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to restart tuned-ppd: {error}")


# ── Tuned profiles management ──────────────────────────────────────────


def get_available_tuned_profiles():
    """Return list of available tuned profiles."""
    if not fn.check_package_installed("tuned"):
        return []

    try:
        result = fn.subprocess.run(
            ["tuned-adm", "list"],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        if result.returncode == 0:
            output = result.stdout.decode().strip()
            # Parse output: "Available profiles:" followed by profile names
            lines = output.split("\n")
            profiles = []
            found_available = False
            for line in lines:
                if "Available profiles:" in line:
                    found_available = True
                    continue
                if found_available and line.strip():
                    # Format: "- profile-name    - description"
                    # Extract profile name (the word after the leading dash, before description dash)
                    line = line.strip()
                    if line.startswith("- "):
                        line = line[2:].strip()
                        # Split on whitespace and take first token (profile name)
                        profile_name = line.split()[0] if line.split() else ""
                        if profile_name:
                            profiles.append(profile_name)
            return profiles
    except Exception as error:
        fn.debug_print(f"Error getting tuned profiles: {error}")
    return []


def get_active_tuned_profile():
    """Return the currently active tuned profile."""
    if not fn.check_package_installed("tuned"):
        return None

    try:
        result = fn.subprocess.run(
            ["tuned-adm", "active"],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        if result.returncode == 0:
            output = result.stdout.decode().strip()
            # Output format: "Current active profile: <profile_name>"
            if "Current active profile:" in output:
                profile = output.split("Current active profile:")[-1].strip()
                return profile
    except Exception as error:
        fn.debug_print(f"Error getting active tuned profile: {error}")
    return None


def get_tuned_profile_status_markup():
    """Build the tuned profile status label text."""
    active_profile = get_active_tuned_profile()
    tuned_enabled = get_service_status("tuned")

    if active_profile:
        status_text = f"Active profile: <b>{active_profile}</b> ({tuned_enabled})"
    else:
        status_text = "No active profile"

    return status_text


def refresh_tuned_profile_status(self):
    """Refresh the visible tuned profile status label."""
    if hasattr(self, "tuned_profile_status_label"):
        GLib.idle_add(
            self.tuned_profile_status_label.set_markup,
            get_tuned_profile_status_markup(),
        )


def refresh_tuned_profile_choices(self):
    """Refresh the tuned profile dropdown with available profiles."""
    if not hasattr(self, "tuned_profile_choices"):
        return

    try:
        tuned_profile_choices = get_available_tuned_profiles()
        if tuned_profile_choices:
            active_profile = get_active_tuned_profile()

            def update_dropdown():
                string_list = Gtk.StringList.new(tuned_profile_choices)
                self.tuned_profile_choices.set_model(string_list)
                if active_profile and active_profile in tuned_profile_choices:
                    self.tuned_profile_choices.set_selected(tuned_profile_choices.index(active_profile))

            GLib.idle_add(update_dropdown)
    except Exception as e:
        fn.debug_print(f"Error refreshing tuned profile choices: {e}")


def apply_tuned_profile(self, _widget):
    """Apply the selected tuned profile."""
    choice = fn.get_combo_text(self.tuned_profile_choices)

    if not choice:
        fn.debug_print("No profile selected")
        GLib.idle_add(fn.show_in_app_notification, self, "No profile selected")
        return

    set_tuned_profile(self, choice)


def set_tuned_profile(self, profile_name):
    """Set and enable a tuned profile."""
    fn.log_subsection("Apply Tuned Profile")
    try:
        if not fn.check_package_installed("tuned"):
            fn.debug_print("Installing tuned package")
            fn.install_package(self, "tuned")

        if fn.shutil.which("tuned-adm") is None:
            fn.log_error("tuned-adm is not installed")
            GLib.idle_add(fn.show_in_app_notification, self, "tuned-adm is not installed")
            return

        fn.debug_print("Starting tuned service")
        fn.enable_service("tuned")
        fn.restart_service("tuned")

        fn.debug_print(f"Applying profile: {profile_name}")
        result = fn.subprocess.run(
            ["tuned-adm", "profile", profile_name],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        if result.returncode != 0:
            fn.log_error(f"Could not set tuned profile to {profile_name}")
            GLib.idle_add(fn.show_in_app_notification, self, f"Could not set tuned profile to {profile_name}")
            return

        refresh_performance_status_label(self)
        refresh_tuned_profile_status(self)
        fn.log_success(f"Tuned profile set to {profile_name}")
        GLib.idle_add(fn.show_in_app_notification, self, f"Tuned profile set to {profile_name}")
    except Exception as error:
        fn.log_error(f"Failed to set tuned profile: {error}")
        GLib.idle_add(fn.show_in_app_notification, self, "Could not set tuned profile")


def get_zram_size_label():
    """Return the current zram size in GB, or its configured expression."""
    try:
        if fn.path.isfile(zram_disk_size):
            with open(zram_disk_size, "r", encoding="utf-8") as f:
                size_bytes = int(f.read().strip())
            return format(size_bytes / 1024 / 1024 / 1024, ".2f") + " GB"

        if fn.path.isfile(zram_config):
            with open(zram_config, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip().startswith("zram-size"):
                        return line.split("=", 1)[1].strip()
    except Exception as error:
        fn.debug_print(error)

    return ""


def get_zram_status_markup():
    """Build the zram status label text."""
    zram_status = "<b>enabled</b>" if fn.check_service("systemd-zram-setup@zram0") else "disabled"
    zram_size = get_zram_size_label()
    if zram_size:
        zram_status = zram_status + " (" + zram_size + ")"
    return "Enable zram compressed RAM swap - installs zram-generator\nZRAM service : " + zram_status


def refresh_zram_status_label(self):
    """Refresh the visible zram status label."""
    if hasattr(self, "zram_status_label"):
        GLib.idle_add(self.zram_status_label.set_markup, get_zram_status_markup())


def get_unit_state(unit, command):
    """Return a systemd unit state for services, timers, and other unit types."""
    try:
        output = fn.subprocess.run(
            ["systemctl", command, unit],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        status = output.stdout.decode().strip()
        if status:
            return status
    except Exception as error:
        fn.debug_print(error)

    return "unknown"


def get_fstrim_status_markup():
    """Build the fstrim timer status label text."""
    enabled_status = get_unit_state(fstrim_timer, "is-enabled")

    if enabled_status == "enabled":
        enabled_status = "<b>enabled</b>"

    return "Enable weekly TRIM for SSD/NVMe drives with fstrim.timer\nfstrim.timer : " + enabled_status


def refresh_fstrim_status_label(self):
    """Refresh the visible fstrim timer status label."""
    if hasattr(self, "fstrim_status_label"):
        GLib.idle_add(self.fstrim_status_label.set_markup, get_fstrim_status_markup())


def get_irqbalance_status_markup():
    """Build the irqbalance service status label text."""
    irqbalance_status = get_service_status("irqbalance")
    return "Balance hardware interrupts across CPUs\nirqbalance service : " + irqbalance_status


def refresh_irqbalance_status_label(self):
    """Refresh the visible irqbalance status label."""
    if hasattr(self, "irqbalance_status_label"):
        GLib.idle_add(
            self.irqbalance_status_label.set_markup,
            get_irqbalance_status_markup(),
        )


def refresh_irqbalance_package_label(self):
    """Refresh the visible irqbalance package status label."""
    if not hasattr(self, "irqbalance_package_label"):
        return

    if fn.check_package_installed("irqbalance"):
        GLib.idle_add(
            self.irqbalance_package_label.set_markup,
            "irqbalance package is <b>installed</b>",
        )
    else:
        GLib.idle_add(self.irqbalance_package_label.set_text, "Install irqbalance")


def refresh_irqbalance_service_buttons(self):
    """Refresh irqbalance button sensitivity after installing or removing it."""
    installed = fn.check_package_installed("irqbalance")
    for button_name in [
        "enable_irqbalance",
        "disable_irqbalance",
    ]:
        if hasattr(self, button_name):
            GLib.idle_add(getattr(self, button_name).set_sensitive, installed)


def enable_zram(self, _widget):
    """Enable zram with the selected compressed swap size."""
    fn.log_subsection("Enable zram")
    try:
        size = fn.get_combo_text(self.zram_size)
        fn.debug_print(f"Enabling zram with size: {size}")
        script = f"""
trap 'echo; read -p "Press Enter to close..."' EXIT

ZRAM_CONF=/etc/systemd/zram-generator.conf
SIZE="{size}"

echo "Enabling zram with size: $SIZE"
echo

if ! pacman -Qi zram-generator &>/dev/null; then
    echo "Installing zram-generator..."
    pacman -S zram-generator --noconfirm --needed
fi

echo "Writing $ZRAM_CONF..."
cat > "$ZRAM_CONF" << EOF
[zram0]
zram-size = $SIZE
compression-algorithm = zstd
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Starting zram device..."
systemctl start systemd-zram-setup@zram0.service

echo
echo "=== zram enabled successfully ==="
swapon --show
echo
cat "$ZRAM_CONF"
echo
echo "=== Operation Finished ==="
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling zram...")

        def _wait_zram_enable():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success(f"zram enabled ({size})")
            GLib.idle_add(fn.show_in_app_notification, self, f"zram enabled ({size})")
            GLib.idle_add(refresh_zram_status_label, self)

        fn.threading.Thread(target=_wait_zram_enable, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable zram: {error}")


def disable_zram(self, _widget):
    """Disable zram."""
    fn.log_subsection("Disable zram")
    try:
        fn.debug_print("Disabling zram")
        script = """
trap 'echo; read -p "Press Enter to close..."' EXIT

ZRAM_CONF=/etc/systemd/zram-generator.conf

echo "Disabling zram..."
echo

echo "Stopping zram device..."
systemctl stop systemd-zram-setup@zram0.service 2>/dev/null || true

if [ -b /dev/zram0 ]; then
    echo "Swapping off /dev/zram0..."
    swapoff /dev/zram0 2>/dev/null || true
fi

if [ -f "$ZRAM_CONF" ]; then
    echo "Removing $ZRAM_CONF..."
    rm -f "$ZRAM_CONF"
else
    echo "No zram configuration found at $ZRAM_CONF - nothing to remove"
fi

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo
echo "=== zram disabled successfully ==="
swapon --show
echo
echo "=== Operation Finished ==="
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling zram...")

        def _wait_zram_disable():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("zram disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "zram disabled")
            GLib.idle_add(refresh_zram_status_label, self)

        fn.threading.Thread(target=_wait_zram_disable, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable zram: {error}")


def get_root_filesystem_type():
    """Return the filesystem type of the root partition."""
    try:
        with open("/proc/mounts", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 3 and parts[1] == "/":
                    return parts[2]
    except Exception as error:
        fn.debug_print(error)
    return ""


def get_swapfile_size_label():
    """Return the current swapfile size in GB if /swapfile exists."""
    try:
        if fn.path.isfile("/swapfile"):
            size_bytes = fn.path.getsize("/swapfile")
            return format(size_bytes / 1024 / 1024 / 1024, ".0f") + " GB"
    except Exception as error:
        fn.debug_print(error)
    return None


def refresh_swapfile_label(self):
    """Refresh the swapfile label with current size."""
    if not hasattr(self, "swapfile_label"):
        return
    size = get_swapfile_size_label()
    if size:
        GLib.idle_add(
            self.swapfile_label.set_markup,
            "Create or manage a swapfile at /swapfile - " + size + " <b>present</b>",
        )
    else:
        GLib.idle_add(
            self.swapfile_label.set_text,
            "Create or manage a swapfile at /swapfile",
        )


def create_swapfile(self, _widget):
    """Create a swapfile with the selected size."""
    fn.log_subsection("Create Swapfile")
    try:
        size = fn.get_combo_text(self.swapfile_size)
        fn.debug_print(f"Creating swapfile with size: {size}")
        script = f"""
trap 'echo; read -p "Press Enter to close..."' EXIT

SWAPFILE=/swapfile
SIZE="{size}"

FSTYPE=$(findmnt -n -o FSTYPE /)

echo "Creating swapfile at $SWAPFILE with size $SIZE"
echo "Detected filesystem: $FSTYPE"
echo

if [ "$FSTYPE" != "ext4" ] && [ "$FSTYPE" != "btrfs" ]; then
    echo "ERROR: Unsupported filesystem: $FSTYPE"
    echo "Only ext4 and btrfs are supported."
    exit 1
fi

SIZE_UPPER=$(echo "$SIZE" | tr '[:lower:]' '[:upper:]')
NUM=$(echo "$SIZE_UPPER" | tr -cd '0-9')
UNIT=$(echo "$SIZE_UPPER" | tr -cd 'A-Z')
case "$UNIT" in
    G) MB=$(( NUM * 1024 )) ;;
    M) MB=$NUM ;;
    K) MB=$(( NUM / 1024 )) ;;
    *) MB=$(( NUM / 1024 / 1024 )) ;;
esac

if swapon --show | grep -q "$SWAPFILE"; then
    echo "Disabling existing swapfile..."
    swapoff "$SWAPFILE"
fi

if [ -f "$SWAPFILE" ]; then
    echo "Removing existing swapfile..."
    rm -f "$SWAPFILE"
fi

if [ "$FSTYPE" = "btrfs" ]; then
    echo "btrfs: disabling Copy-on-Write before writing..."
    touch "$SWAPFILE"
    chattr +C "$SWAPFILE"
fi

echo "Writing $SIZE swapfile (dd with progress)..."
dd if=/dev/zero of="$SWAPFILE" bs=1M count="$MB" status=progress
echo

echo "Setting permissions (chmod 600)..."
chmod 600 "$SWAPFILE"

echo "Formatting as swap..."
mkswap "$SWAPFILE"

echo "Activating swapfile..."
swapon "$SWAPFILE"

if ! grep -q "$SWAPFILE" /etc/fstab; then
    echo "Adding $SWAPFILE to /etc/fstab..."
    echo "$SWAPFILE none swap defaults 0 0" >> /etc/fstab
else
    echo "$SWAPFILE already in /etc/fstab - skipping"
fi

echo
echo "=== Swapfile created successfully ==="
swapon --show
echo
echo "=== Operation Finished ==="
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Creating swapfile...")

        def _wait_create_swapfile():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success(f"Swapfile ({size}) created at /swapfile")
            GLib.idle_add(fn.show_in_app_notification, self, f"Swapfile ({size}) created at /swapfile")
            GLib.idle_add(refresh_swapfile_label, self)

        fn.threading.Thread(target=_wait_create_swapfile, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to create swapfile: {error}")


def remove_swapfile(self, _widget):
    """Remove the swapfile."""
    fn.log_subsection("Remove Swapfile")
    try:
        fn.debug_print("Removing swapfile at /swapfile")
        script = """
trap 'echo; read -p "Press Enter to close..."' EXIT

SWAPFILE=/swapfile

echo "Removing swapfile at $SWAPFILE"
echo

if [ ! -f "$SWAPFILE" ]; then
    echo "No swapfile found at $SWAPFILE - nothing to do"
else
    if swapon --show | grep -q "$SWAPFILE"; then
        echo "Disabling swapfile..."
        swapoff "$SWAPFILE"
    fi

    echo "Removing $SWAPFILE from /etc/fstab..."
    sed -i "\\|$SWAPFILE|d" /etc/fstab

    echo "Deleting swapfile..."
    rm -f "$SWAPFILE"

    echo "=== Swapfile removed successfully ==="
fi

swapon --show
echo
echo "=== Operation Finished ==="
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Removing swapfile...")

        def _wait_remove_swapfile():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("Swapfile removed")
            GLib.idle_add(fn.show_in_app_notification, self, "Swapfile removed")
            GLib.idle_add(refresh_swapfile_label, self)

        fn.threading.Thread(target=_wait_remove_swapfile, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to remove swapfile: {error}")


def enable_fstrim_timer(self, _widget):
    """Enable the weekly fstrim timer."""
    fn.log_subsection("Enable fstrim Timer")
    try:
        script = (
            f"systemctl enable --now {fstrim_timer} "
            "&& echo 'fstrim.timer enabled for weekly TRIM' "
            "|| echo 'Failed to enable fstrim.timer'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling fstrim.timer...")

        def _wait_fstrim_enable():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fstrim.timer enabled for weekly TRIM")
            GLib.idle_add(fn.show_in_app_notification, self, "fstrim.timer enabled")
            GLib.idle_add(refresh_fstrim_status_label, self)

        fn.threading.Thread(target=_wait_fstrim_enable, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable fstrim.timer: {error}")


def disable_fstrim_timer(self, _widget):
    """Disable the weekly fstrim timer."""
    fn.log_subsection("Disable fstrim Timer")
    try:
        script = (
            f"systemctl disable --now {fstrim_timer} "
            "&& echo 'fstrim.timer disabled' "
            "|| echo 'Failed to disable fstrim.timer'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling fstrim.timer...")

        def _wait_fstrim_disable():
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("fstrim.timer disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "fstrim.timer disabled")
            GLib.idle_add(refresh_fstrim_status_label, self)

        fn.threading.Thread(target=_wait_fstrim_disable, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable fstrim.timer: {error}")


def install_irqbalance(self, _widget):
    """Install irqbalance."""
    if fn.check_package_installed("irqbalance"):
        fn.log_info("irqbalance is already installed")
        GLib.idle_add(fn.show_in_app_notification, self, "irqbalance is already installed")
        return
    fn.log_subsection("Install irqbalance")

    def _do_install():
        try:
            fn.log_info("Enabling service: irqbalance.service")
            fn.debug_print("Terminal: pacman -S --noconfirm --needed irqbalance")
            fn.debug_print("Terminal: systemctl enable --now irqbalance")
            install_script = """
set -o pipefail
pacman -S --noconfirm --needed irqbalance
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo ''
    echo 'Enabling irqbalance...'
    systemctl enable --now irqbalance && echo '✓ irqbalance enabled' || echo '✗ Failed'
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for irqbalance install terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing irqbalance labels")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed("irqbalance"):
                fn.log_success("irqbalance installed")
                GLib.idle_add(fn.show_in_app_notification, self, "irqbalance has been installed")
            else:
                fn.log_warn("irqbalance installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "irqbalance installation failed or was cancelled")
            GLib.idle_add(refresh_irqbalance_package_label, self)
            GLib.idle_add(refresh_irqbalance_service_buttons, self)
            GLib.idle_add(refresh_irqbalance_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to install irqbalance: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_irqbalance(self, _widget):
    """Remove irqbalance."""
    if not fn.check_package_installed("irqbalance"):
        fn.log_info("irqbalance is not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "irqbalance is not installed")
        return
    fn.log_subsection("Remove irqbalance")

    def _do_remove():
        try:
            fn.debug_print("Terminal: systemctl disable --now irqbalance")
            fn.debug_print("Terminal: pacman -R --noconfirm irqbalance")
            remove_script = """
echo 'Disabling irqbalance...'
systemctl disable --now irqbalance && echo '✓ irqbalance disabled' || echo '✗ Failed'

echo ''
echo 'Removing packages...'
pacman -R --noconfirm irqbalance
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {remove_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for irqbalance remove terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing irqbalance labels")
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed("irqbalance"):
                fn.log_success("irqbalance removed")
                GLib.idle_add(fn.show_in_app_notification, self, "irqbalance has been removed")
            else:
                fn.log_warn("irqbalance removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "irqbalance removal failed or was cancelled")
            GLib.idle_add(refresh_irqbalance_package_label, self)
            GLib.idle_add(refresh_irqbalance_service_buttons, self)
            GLib.idle_add(refresh_irqbalance_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to remove irqbalance: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def enable_irqbalance_service(self, _widget):
    """Enable the irqbalance service via a terminal."""
    fn.log_subsection("Enable irqbalance Service")
    try:
        fn.debug_print("Terminal: systemctl enable --now irqbalance")
        script = (
            "echo 'Enabling irqbalance...'\n"
            "systemctl enable --now irqbalance && echo '✓ irqbalance enabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling irqbalance...")

        def _wait_enable_irqbalance():
            fn.debug_print("Waiting for irqbalance enable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing irqbalance status label")
            fn.log_success("irqbalance service enabled")
            GLib.idle_add(fn.show_in_app_notification, self, "irqbalance has been enabled and started")
            GLib.idle_add(refresh_irqbalance_status_label, self)

        fn.threading.Thread(target=_wait_enable_irqbalance, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable irqbalance: {error}")


def disable_irqbalance_service(self, _widget):
    """Disable the irqbalance service via a terminal."""
    fn.log_subsection("Disable irqbalance Service")
    try:
        fn.debug_print("Terminal: systemctl disable --now irqbalance")
        script = (
            "echo 'Disabling irqbalance...'\n"
            "systemctl disable --now irqbalance && echo '✓ irqbalance disabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling irqbalance...")

        def _wait_disable_irqbalance():
            fn.debug_print("Waiting for irqbalance disable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing irqbalance status label")
            fn.log_success("irqbalance service disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "irqbalance has been disabled and stopped")
            GLib.idle_add(refresh_irqbalance_status_label, self)

        fn.threading.Thread(target=_wait_disable_irqbalance, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable irqbalance: {error}")


# ── Ananicy block ──────────────────────────────────────────────────────

ANANICY_PACKAGE = "ananicy-cpp"
ANANICY_RULES_PACKAGE = "cachyos-ananicy-rules-git"


def get_ananicy_status_markup():
    """Build the ananicy-cpp service status label text."""
    ananicy_status = get_service_status("ananicy-cpp")
    return "Auto nice daemon for CPU and I/O scheduling\nananicy-cpp service : " + ananicy_status


def refresh_ananicy_status_label(self):
    """Refresh the visible ananicy status label."""
    if hasattr(self, "ananicy_status_label"):
        GLib.idle_add(
            self.ananicy_status_label.set_markup,
            get_ananicy_status_markup(),
        )


def refresh_ananicy_package_label(self):
    """Refresh the ananicy package status label."""
    if not hasattr(self, "ananicy_package_label"):
        return

    ananicy_installed = fn.check_package_installed(ANANICY_PACKAGE)
    rules_installed = fn.check_package_installed(ANANICY_RULES_PACKAGE)

    if ananicy_installed and rules_installed:
        GLib.idle_add(
            self.ananicy_package_label.set_markup,
            "ananicy-cpp and cachyos-ananicy-rules-git are <b>installed</b>",
        )
    elif ananicy_installed:
        GLib.idle_add(
            self.ananicy_package_label.set_markup,
            "ananicy-cpp is <b>installed</b> (cachyos-ananicy-rules-git not installed)",
        )
    else:
        GLib.idle_add(
            self.ananicy_package_label.set_text,
            "Install ananicy-cpp and cachyos-ananicy-rules-git",
        )


def refresh_ananicy_service_buttons(self):
    """Refresh ananicy button sensitivity after installing or removing it."""
    installed = fn.check_package_installed(ANANICY_PACKAGE)
    for button_name in ["enable_ananicy", "disable_ananicy"]:
        if hasattr(self, button_name):
            GLib.idle_add(getattr(self, button_name).set_sensitive, installed)


def install_ananicy(self, _widget):
    """Install ananicy-cpp and cachyos-ananicy-rules-git."""
    if fn.check_package_installed(ANANICY_PACKAGE):
        fn.log_info("ananicy-cpp is already installed")
        GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp is already installed")
        return
    if not fn.check_chaotic_aur_active() and not fn.check_nemesis_repo_active():
        fn.log_warn("ananicy: cachyos-ananicy-rules-git requires Chaotic AUR or the Nemesis repo — enable one first")
        GLib.idle_add(
            fn.show_in_app_notification,
            self,
            "Enable Chaotic AUR or Nemesis repo first — cachyos-ananicy-rules-git is not in standard repos",
        )
        return
    fn.log_subsection("Install ananicy")

    def _do_install():
        try:
            fn.log_info("Enabling service: ananicy-cpp.service")
            fn.debug_print(f"Terminal: pacman -S --noconfirm --needed {ANANICY_PACKAGE} {ANANICY_RULES_PACKAGE}")
            fn.debug_print(f"Terminal: systemctl enable --now {ANANICY_PACKAGE}")
            install_script = f"""
set -o pipefail
pacman -S --noconfirm --needed {ANANICY_PACKAGE} {ANANICY_RULES_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo ''
    echo 'Enabling ananicy-cpp...'
    systemctl enable --now {ANANICY_PACKAGE} && echo '✓ ananicy-cpp enabled' || echo '✗ Failed'
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for ananicy install terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing ananicy labels")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed(ANANICY_PACKAGE):
                fn.log_success("ananicy-cpp and cachyos-ananicy-rules-git installed")
                GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp has been installed")
                GLib.idle_add(refresh_ananicy_package_label, self)
                GLib.idle_add(refresh_ananicy_service_buttons, self)
                GLib.idle_add(refresh_ananicy_status_label, self)
            else:
                fn.log_warn("ananicy-cpp installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp installation failed or was cancelled")
                GLib.idle_add(refresh_ananicy_package_label, self)
        except Exception as error:
            fn.log_error(f"Failed to install ananicy: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_ananicy(self, _widget):
    """Remove ananicy-cpp and cachyos-ananicy-rules-git."""
    if not fn.check_package_installed(ANANICY_PACKAGE):
        fn.log_info("ananicy-cpp is not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp is not installed")
        return
    fn.log_subsection("Remove ananicy")

    def _do_remove():
        try:
            fn.debug_print(f"Terminal: systemctl disable --now {ANANICY_PACKAGE}")
            fn.debug_print(f"Terminal: pacman -R --noconfirm {ANANICY_PACKAGE} {ANANICY_RULES_PACKAGE}")
            remove_script = f"""
echo 'Disabling ananicy-cpp...'
systemctl disable --now {ANANICY_PACKAGE} && echo '✓ ananicy-cpp disabled' || echo '✗ Failed'

echo ''
echo 'Removing packages...'
pacman -R --noconfirm {ANANICY_PACKAGE} {ANANICY_RULES_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {remove_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for ananicy remove terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — checking ananicy removal")
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed(ANANICY_PACKAGE):
                fn.log_success("ananicy-cpp and cachyos-ananicy-rules-git removed")
                GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp has been removed")
            else:
                fn.log_warn("ananicy-cpp removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp removal failed or was cancelled")
            GLib.idle_add(refresh_ananicy_package_label, self)
            GLib.idle_add(refresh_ananicy_service_buttons, self)
            GLib.idle_add(refresh_ananicy_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to remove ananicy: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def enable_ananicy_service(self, _widget):
    """Enable the ananicy-cpp service via a terminal."""
    fn.log_subsection("Enable ananicy Service")
    try:
        fn.debug_print(f"Terminal: systemctl enable --now {ANANICY_PACKAGE}")
        script = (
            f"echo 'Enabling ananicy-cpp...'\n"
            f"systemctl enable --now {ANANICY_PACKAGE} && echo '✓ ananicy-cpp enabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling ananicy-cpp...")

        def _wait_enable_ananicy():
            fn.debug_print("Waiting for ananicy enable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing ananicy status label")
            fn.log_success("ananicy-cpp service enabled")
            GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp has been enabled and started")
            GLib.idle_add(refresh_ananicy_status_label, self)

        fn.threading.Thread(target=_wait_enable_ananicy, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable ananicy: {error}")


def disable_ananicy_service(self, _widget):
    """Disable the ananicy-cpp service via a terminal."""
    fn.log_subsection("Disable ananicy Service")
    try:
        fn.debug_print(f"Terminal: systemctl disable --now {ANANICY_PACKAGE}")
        script = (
            f"echo 'Disabling ananicy-cpp...'\n"
            f"systemctl disable --now {ANANICY_PACKAGE} && echo '✓ ananicy-cpp disabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling ananicy-cpp...")

        def _wait_disable_ananicy():
            fn.debug_print("Waiting for ananicy disable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing ananicy status label")
            fn.log_success("ananicy-cpp service disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "ananicy-cpp has been disabled and stopped")
            GLib.idle_add(refresh_ananicy_status_label, self)

        fn.threading.Thread(target=_wait_disable_ananicy, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable ananicy: {error}")


# ── GameMode block ─────────────────────────────────────────────────────

GAMEMODE_PACKAGE = "gamemode"


def get_real_user():
    """Return the real (non-root) username running the app."""
    pkexec_uid = os.environ.get("PKEXEC_UID")
    if pkexec_uid:
        try:
            return pwd.getpwuid(int(pkexec_uid)).pw_name
        except Exception:
            pass
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        return sudo_user
    try:
        return (
            fn.subprocess.run(
                ["logname"],
                check=False,
                shell=False,
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.STDOUT,
            )
            .stdout.decode()
            .strip()
        )
    except Exception:
        pass
    return None


def get_gamemoded_user_status():
    """Check gamemoded user service status via --machine flag."""
    real_user = get_real_user()
    if not real_user:
        return "disabled"
    try:
        output = fn.subprocess.run(
            ["systemctl", "--user", f"--machine={real_user}@.host", "is-enabled", "gamemoded.service"],
            check=False,
            shell=False,
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.STDOUT,
        )
        status = output.stdout.decode().strip()
        if status == "enabled":
            return "<b>enabled</b>"
    except Exception as error:
        fn.debug_print(error)
    return "disabled"


def get_gamemode_status_markup():
    """Build the gamemode service status label text."""
    gamemode_status = get_gamemoded_user_status()
    return "Optimize system performance for gaming\ngamemoded service : " + gamemode_status


def refresh_gamemode_status_label(self):
    """Refresh the visible gamemode status label."""
    if hasattr(self, "gamemode_status_label"):
        GLib.idle_add(
            self.gamemode_status_label.set_markup,
            get_gamemode_status_markup(),
        )


def refresh_gamemode_package_label(self):
    """Refresh the gamemode package status label."""
    if not hasattr(self, "gamemode_package_label"):
        return

    if fn.check_package_installed(GAMEMODE_PACKAGE):
        GLib.idle_add(
            self.gamemode_package_label.set_markup,
            "gamemode package is <b>installed</b>",
        )
    else:
        GLib.idle_add(
            self.gamemode_package_label.set_text,
            "Install gamemode",
        )


def refresh_gamemode_service_buttons(self):
    """Refresh gamemode button sensitivity after installing or removing it."""
    installed = fn.check_package_installed(GAMEMODE_PACKAGE)
    for button_name in ["enable_gamemode", "disable_gamemode"]:
        if hasattr(self, button_name):
            GLib.idle_add(getattr(self, button_name).set_sensitive, installed)


def install_gamemode(self, _widget):
    """Install gamemode."""
    if fn.check_package_installed(GAMEMODE_PACKAGE):
        fn.log_info("gamemode is already installed")
        GLib.idle_add(fn.show_in_app_notification, self, "gamemode is already installed")
        return
    fn.log_subsection("Install gamemode")

    def _do_install():
        try:
            fn.log_info("Enabling service: gamemoded.service (user service)")
            fn.debug_print(f"Terminal: pacman -S --noconfirm --needed {GAMEMODE_PACKAGE}")
            fn.debug_print("Terminal: systemctl --user --machine=<real_user>@.host enable --now gamemoded.service")
            fn.debug_print(f"Real user (Python side): {get_real_user()}")
            install_script = f"""
REAL_USER="${{PKEXEC_UID:+$(getent passwd "$PKEXEC_UID" | cut -d: -f1)}}"
[ -z "$REAL_USER" ] && REAL_USER="${{SUDO_USER:-$(logname 2>/dev/null)}}"

set -o pipefail
pacman -S --noconfirm --needed {GAMEMODE_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    if [ -n "$REAL_USER" ]; then
        echo ''
        echo "Enabling gamemoded for user $REAL_USER..."
        systemctl --user --machine="${{REAL_USER}}@.host" enable --now gamemoded.service \\
            && echo '✓ gamemoded enabled' || echo '✗ Failed to enable'
    else
        echo '⚠ Could not determine real user - enable gamemoded manually'
    fi
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for gamemode install terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing gamemode labels")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed(GAMEMODE_PACKAGE):
                fn.log_success("gamemode installed")
                GLib.idle_add(fn.show_in_app_notification, self, "gamemode has been installed")
            else:
                fn.log_warn("gamemode installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "gamemode installation failed or was cancelled")
            GLib.idle_add(refresh_gamemode_package_label, self)
            GLib.idle_add(refresh_gamemode_service_buttons, self)
            GLib.idle_add(refresh_gamemode_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to install gamemode: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_gamemode(self, _widget):
    """Remove gamemode."""
    if not fn.check_package_installed(GAMEMODE_PACKAGE):
        fn.log_info("gamemode is not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "gamemode is not installed")
        return
    fn.log_subsection("Remove gamemode")

    def _do_remove():
        try:
            fn.debug_print("Terminal: systemctl --user --machine=<real_user>@.host disable --now gamemoded.service")
            fn.debug_print(f"Terminal: pacman -R --noconfirm {GAMEMODE_PACKAGE}")
            fn.debug_print(f"Real user (Python side): {get_real_user()}")
            remove_script = f"""
REAL_USER="${{PKEXEC_UID:+$(getent passwd "$PKEXEC_UID" | cut -d: -f1)}}"
[ -z "$REAL_USER" ] && REAL_USER="${{SUDO_USER:-$(logname 2>/dev/null)}}"

echo 'Disabling gamemoded...'
if [ -n "$REAL_USER" ]; then
    systemctl --user --machine="${{REAL_USER}}@.host" disable --now gamemoded.service \\
        && echo '✓ gamemoded disabled' || echo '✗ Failed (may already be disabled)'
else
    echo '⚠ Could not determine real user - skipping service disable'
fi

echo ''
echo 'Removing packages...'
pacman -R --noconfirm {GAMEMODE_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {remove_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for gamemode remove terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing gamemode labels")
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed(GAMEMODE_PACKAGE):
                fn.log_success("gamemode removed")
                GLib.idle_add(fn.show_in_app_notification, self, "gamemode has been removed")
            else:
                fn.log_warn("gamemode removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "gamemode removal failed or was cancelled")
            GLib.idle_add(refresh_gamemode_package_label, self)
            GLib.idle_add(refresh_gamemode_service_buttons, self)
            GLib.idle_add(refresh_gamemode_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to remove gamemode: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def enable_gamemode_service(self, _widget):
    """Enable the gamemoded user service for the real (non-root) user via a terminal."""
    fn.log_subsection("Enable gamemode Service")
    try:
        fn.debug_print(f"Real user (Python side): {get_real_user()}")
        fn.debug_print("Terminal: systemctl --user --machine=<real_user>@.host enable --now gamemoded.service")
        script = """
REAL_USER="${PKEXEC_UID:+$(getent passwd "$PKEXEC_UID" | cut -d: -f1)}"
[ -z "$REAL_USER" ] && REAL_USER="${SUDO_USER:-$(logname 2>/dev/null)}"

echo "Enabling gamemoded for user $REAL_USER..."
systemctl --user --machine="${REAL_USER}@.host" enable --now gamemoded.service \\
    && echo '✓ gamemoded enabled' || echo '✗ Failed'

echo
read -p 'Press Enter to close...'
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling gamemoded...")

        def _wait_enable_gamemode():
            fn.debug_print("Waiting for gamemode enable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing gamemode status label")
            fn.log_success("gamemode service enabled")
            GLib.idle_add(fn.show_in_app_notification, self, "gamemode has been enabled and started")
            GLib.idle_add(refresh_gamemode_status_label, self)

        fn.threading.Thread(target=_wait_enable_gamemode, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable gamemode: {error}")


# ── Preload block ──────────────────────────────────────────────────────

PRELOAD_PACKAGE = "preload"


def get_preload_status_markup():
    """Build the preload service status label text."""
    preload_status = get_service_status("preload")
    return "Adaptive readahead daemon — preloads frequently used binaries into RAM\npreload service : " + preload_status


def refresh_preload_status_label(self):
    """Refresh the visible preload status label."""
    if hasattr(self, "preload_status_label"):
        GLib.idle_add(
            self.preload_status_label.set_markup,
            get_preload_status_markup(),
        )


def refresh_preload_package_label(self):
    """Refresh the preload package status label."""
    if not hasattr(self, "preload_package_label"):
        return
    if fn.check_package_installed(PRELOAD_PACKAGE):
        GLib.idle_add(
            self.preload_package_label.set_markup,
            "preload package is <b>installed</b>",
        )
    else:
        GLib.idle_add(self.preload_package_label.set_text, "Install preload")


def refresh_preload_service_buttons(self):
    """Refresh preload button sensitivity after installing or removing it."""
    installed = fn.check_package_installed(PRELOAD_PACKAGE)
    for button_name in ["enable_preload", "disable_preload"]:
        if hasattr(self, button_name):
            GLib.idle_add(getattr(self, button_name).set_sensitive, installed)


def install_preload(self, _widget):
    """Install preload from Chaotic AUR or Nemesis repo."""
    if fn.check_package_installed(PRELOAD_PACKAGE):
        fn.log_info("preload is already installed")
        GLib.idle_add(fn.show_in_app_notification, self, "preload is already installed")
        return
    if not fn.check_chaotic_aur_active() and not fn.check_nemesis_repo_active():
        fn.log_warn("preload requires Chaotic AUR or the Nemesis repo — enable one first")
        GLib.idle_add(
            fn.show_in_app_notification,
            self,
            "Enable Chaotic AUR or Nemesis repo first — preload is not in standard repos",
        )
        return
    fn.log_subsection("Install preload")

    def _do_install():
        try:
            fn.log_info("Enabling service: preload.service")
            install_script = f"""
set -o pipefail
pacman -S --noconfirm --needed {PRELOAD_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then
    echo '✓ Installation successful'
    echo ''
    echo 'Enabling preload...'
    systemctl enable --now {PRELOAD_PACKAGE} && echo '✓ preload enabled' || echo '✗ Failed'
else
    echo '✗ Installation failed'
fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {install_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", install_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for preload install terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing preload labels")
            fn.invalidate_pkg_cache()
            if fn.check_package_installed(PRELOAD_PACKAGE):
                fn.log_success("preload installed and enabled")
                GLib.idle_add(fn.show_in_app_notification, self, "preload has been installed")
            else:
                fn.log_warn("preload installation did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "preload installation failed or was cancelled")
            GLib.idle_add(refresh_preload_package_label, self)
            GLib.idle_add(refresh_preload_service_buttons, self)
            GLib.idle_add(refresh_preload_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to install preload: {error}")

    fn.threading.Thread(target=_do_install, daemon=True).start()


def remove_preload(self, _widget):
    """Remove preload."""
    if not fn.check_package_installed(PRELOAD_PACKAGE):
        fn.log_info("preload is not installed")
        GLib.idle_add(fn.show_in_app_notification, self, "preload is not installed")
        return
    fn.log_subsection("Remove preload")

    def _do_remove():
        try:
            remove_script = f"""
echo 'Disabling preload...'
systemctl disable --now {PRELOAD_PACKAGE} && echo '✓ preload disabled' || echo '✗ Failed'

echo ''
echo 'Removing packages...'
pacman -R --noconfirm {PRELOAD_PACKAGE}
RESULT=$?

echo ''
if [ $RESULT -eq 0 ]; then echo '✓ Removal successful'; else echo '✗ Removal failed'; fi

echo ''
echo '=== Operation Finished ==='
read -p 'Press Enter to close...'
"""
            fn.debug_print(f"Terminal cmd: {remove_script}")
            proc = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", remove_script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            fn.debug_print("Waiting for preload remove terminal to close...")
            proc.wait()
            fn.debug_print("Terminal closed — refreshing preload labels")
            fn.invalidate_pkg_cache()
            if not fn.check_package_installed(PRELOAD_PACKAGE):
                fn.log_success("preload removed")
                GLib.idle_add(fn.show_in_app_notification, self, "preload has been removed")
            else:
                fn.log_warn("preload removal did not complete")
                GLib.idle_add(fn.show_in_app_notification, self, "preload removal failed or was cancelled")
            GLib.idle_add(refresh_preload_package_label, self)
            GLib.idle_add(refresh_preload_service_buttons, self)
            GLib.idle_add(refresh_preload_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to remove preload: {error}")

    fn.threading.Thread(target=_do_remove, daemon=True).start()


def enable_preload_service(self, _widget):
    """Enable the preload service via a terminal."""
    fn.log_subsection("Enable preload Service")
    try:
        script = (
            "echo 'Enabling preload...'\n"
            f"systemctl enable --now {PRELOAD_PACKAGE} && echo '✓ preload enabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Enabling preload...")

        def _wait_enable_preload():
            fn.debug_print("Waiting for preload enable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("preload service enabled")
            GLib.idle_add(fn.show_in_app_notification, self, "preload has been enabled and started")
            GLib.idle_add(refresh_preload_status_label, self)

        fn.threading.Thread(target=_wait_enable_preload, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to enable preload: {error}")


def disable_preload_service(self, _widget):
    """Disable the preload service via a terminal."""
    fn.log_subsection("Disable preload Service")
    try:
        script = (
            "echo 'Disabling preload...'\n"
            f"systemctl disable --now {PRELOAD_PACKAGE} && echo '✓ preload disabled' || echo '✗ Failed'\n"
            "echo\nread -p 'Press Enter to close...'"
        )
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling preload...")

        def _wait_disable_preload():
            fn.debug_print("Waiting for preload disable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.log_success("preload service disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "preload has been disabled and stopped")
            GLib.idle_add(refresh_preload_status_label, self)

        fn.threading.Thread(target=_wait_disable_preload, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable preload: {error}")


def disable_gamemode_service(self, _widget):
    """Disable the gamemoded user service for the real (non-root) user via a terminal."""
    fn.log_subsection("Disable gamemode Service")
    try:
        fn.debug_print(f"Real user (Python side): {get_real_user()}")
        fn.debug_print("Terminal: systemctl --user --machine=<real_user>@.host disable --now gamemoded.service")
        script = """
REAL_USER="${PKEXEC_UID:+$(getent passwd "$PKEXEC_UID" | cut -d: -f1)}"
[ -z "$REAL_USER" ] && REAL_USER="${SUDO_USER:-$(logname 2>/dev/null)}"

echo "Disabling gamemoded for user $REAL_USER..."
systemctl --user --machine="${REAL_USER}@.host" disable --now gamemoded.service \\
    && echo '✓ gamemoded disabled' || echo '✗ Failed'

echo
read -p 'Press Enter to close...'
"""
        fn.debug_print(f"Terminal cmd: {script}")
        process = fn.subprocess.Popen(
            ["alacritty", "-e", "bash", "-c", script],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        GLib.idle_add(fn.show_in_app_notification, self, "Disabling gamemoded...")

        def _wait_disable_gamemode():
            fn.debug_print("Waiting for gamemode disable terminal to close...")
            process.wait()
            fn.invalidate_pkg_cache()
            fn.debug_print("Terminal closed — refreshing gamemode status label")
            fn.log_success("gamemode service disabled")
            GLib.idle_add(fn.show_in_app_notification, self, "gamemode has been disabled and stopped")
            GLib.idle_add(refresh_gamemode_status_label, self)

        fn.threading.Thread(target=_wait_disable_gamemode, daemon=True).start()
    except Exception as error:
        fn.log_error(f"Failed to disable gamemode: {error}")


# ── makepkg.conf tuning (Build Settings) ───────────────────────────────

MAKEPKG_CONF = "/etc/makepkg.conf"
MAKEPKG_CONF_BAK = "/etc/makepkg.conf-bak"
ATT_TUNE_MAKEPKG = "/usr/share/archlinux-tweak-tool/data/bin/att-tune-makepkg"


def get_makepkg_status():
    """Return (makeflags_value, ncores) by parsing /etc/makepkg.conf."""
    makeflags = "unknown"
    try:
        with open(MAKEPKG_CONF, "r", encoding="utf-8") as makepkg_file:
            for line in makepkg_file:
                match = re.match(r"^\s*(#?)\s*MAKEFLAGS=(.+)$", line)
                if match:
                    commented, value = match.groups()
                    value = value.strip().split("#", 1)[0].strip().strip('"').strip("'")
                    makeflags = ("(default, commented) " + value) if commented else value
                    break
    except Exception as error:
        fn.debug_print(f"Could not read {MAKEPKG_CONF}: {error}")
        makeflags = "read error"

    ncores = os.cpu_count() or 1
    return makeflags, ncores


def get_makepkg_status_markup():
    """Build the makepkg.conf status label markup."""
    makeflags, ncores = get_makepkg_status()
    return (
        "MAKEFLAGS in /etc/makepkg.conf: <b>"
        + makeflags
        + "</b>   |   Detected CPU cores: <b>"
        + str(ncores)
        + "</b>"
    )


def refresh_makepkg_status_label(self):
    """Refresh the makepkg.conf status label and restore-button sensitivity."""
    if hasattr(self, "makepkg_status_label"):
        GLib.idle_add(self.makepkg_status_label.set_markup, get_makepkg_status_markup())
    if hasattr(self, "btn_restore_makepkg"):
        backup_exists = os.path.isfile(MAKEPKG_CONF_BAK)
        GLib.idle_add(self.btn_restore_makepkg.set_sensitive, backup_exists)
        tooltip = (
            "Restore /etc/makepkg.conf from /etc/makepkg.conf-bak"
            if backup_exists
            else "No backup file found at /etc/makepkg.conf-bak"
        )
        GLib.idle_add(self.btn_restore_makepkg.set_tooltip_text, tooltip)


def optimize_makepkg(self, _widget):
    """Set MAKEFLAGS in /etc/makepkg.conf to use all CPU cores."""
    ncores = os.cpu_count() or 1
    fn.log_subsection(f"Tune /etc/makepkg.conf for {ncores} cores")

    if ncores <= 1:
        fn.log_warn("Single core detected — no change.")
        fn.show_in_app_notification(self, "Single core detected — no change.")
        return

    cmd = f"alacritty -e bash -c '{ATT_TUNE_MAKEPKG} apply'"
    fn.debug_print(f"Terminal cmd: {cmd}")
    GLib.idle_add(fn.show_in_app_notification, self, f"Tuning /etc/makepkg.conf for {ncores} cores...")

    def _wait_optimize():
        try:
            returncode = fn.subprocess.Popen(cmd, shell=True, env=fn.get_terminal_env()).wait()
            if returncode == 0:
                fn.log_success(f"MAKEFLAGS set to -j{ncores} in /etc/makepkg.conf")
                GLib.idle_add(fn.show_in_app_notification, self, f"MAKEFLAGS set to -j{ncores}")
            else:
                fn.log_warn(f"Terminal exited with code {returncode}")
                GLib.idle_add(
                    fn.show_in_app_notification, self, "Tune failed — see terminal for details"
                )
            GLib.idle_add(refresh_makepkg_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to tune makepkg.conf: {error}")

    fn.threading.Thread(target=_wait_optimize, daemon=True).start()


def restore_makepkg(self, _widget):
    """Restore /etc/makepkg.conf from /etc/makepkg.conf-bak."""
    fn.log_subsection("Restore /etc/makepkg.conf from backup")

    if not os.path.isfile(MAKEPKG_CONF_BAK):
        fn.log_warn(f"No backup file at {MAKEPKG_CONF_BAK}")
        fn.show_in_app_notification(self, "No backup file at /etc/makepkg.conf-bak")
        return

    fn.log_info_concise(f"  From: {MAKEPKG_CONF_BAK}")
    fn.log_info_concise(f"  To:   {MAKEPKG_CONF}")

    cmd = f"alacritty -e bash -c '{ATT_TUNE_MAKEPKG} restore'"
    fn.debug_print(f"Terminal cmd: {cmd}")
    GLib.idle_add(fn.show_in_app_notification, self, "Restoring /etc/makepkg.conf...")

    def _wait_restore():
        try:
            returncode = fn.subprocess.Popen(cmd, shell=True, env=fn.get_terminal_env()).wait()
            if returncode == 0:
                fn.log_success("/etc/makepkg.conf restored from backup")
                GLib.idle_add(fn.show_in_app_notification, self, "/etc/makepkg.conf restored from backup")
            else:
                fn.log_warn(f"Terminal exited with code {returncode}")
                GLib.idle_add(
                    fn.show_in_app_notification, self, "Restore failed — see terminal for details"
                )
            GLib.idle_add(refresh_makepkg_status_label, self)
        except Exception as error:
            fn.log_error(f"Failed to restore makepkg.conf: {error}")

    fn.threading.Thread(target=_wait_restore, daemon=True).start()
