# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

import functions as fn


def _refresh_ublock_label(self):
    installed = fn.check_package_installed("firefox-ublock-origin")
    self.lbl_ublock.set_markup("uBlock Origin for Firefox" + (" <b>installed</b>" if installed else ""))


def _is_hblock_active():
    try:
        with open("/etc/hosts", "r") as f:
            return any("hblock" in line for line in f)
    except OSError:
        return False


def _refresh_hblock_label(self):
    installed = fn.check_package_installed("hblock")
    self.lbl_hblock.set_markup(
        "hblock — ad/tracker blocking via /etc/hosts" + (" <b>installed</b>" if installed else "")
    )
    self.btn_enable_hblock.set_sensitive(installed)
    self.btn_disable_hblock.set_sensitive(installed)
    active = _is_hblock_active()
    self.lbl_hblock_status.set_markup(
        "Enable or disable hblock — check /etc/hosts <b>active</b>"
        if active
        else "Enable or disable hblock — check /etc/hosts inactive"
    )


def on_click_install_ublock(self, _widget):
    """Install the firefox-ublock-origin package via a terminal."""
    if fn.check_package_installed("firefox-ublock-origin"):
        fn.log_info("uBlock Origin is already installed")
        fn.show_in_app_notification(self, "uBlock Origin is already installed")
        return
    fn.log_subsection("Install uBlock Origin")
    script = "sudo pacman -S firefox-ublock-origin --needed; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_ublock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_ublock(self, _widget):
    """Remove the firefox-ublock-origin package via a terminal."""
    if not fn.check_package_installed("firefox-ublock-origin"):
        fn.log_info("uBlock Origin is not installed")
        fn.show_in_app_notification(self, "uBlock Origin is not installed")
        return
    fn.log_subsection("Remove uBlock Origin")
    script = "sudo pacman -Rs firefox-ublock-origin; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_ublock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_install_hblock(self, _widget):
    """Install the hblock package via a terminal."""
    if fn.check_package_installed("hblock"):
        fn.log_info("hblock is already installed")
        fn.show_in_app_notification(self, "hblock is already installed")
        return
    fn.log_subsection("Install hblock")
    script = "sudo pacman -S hblock --needed; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_hblock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_remove_hblock(self, _widget):
    """Remove the hblock package via a terminal."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, "hblock is not installed")
        return
    fn.log_subsection("Remove hblock")
    script = "sudo pacman -Rs hblock; read -p 'Press enter to close'"
    fn.debug_print(f"Terminal cmd: {script}")
    process = fn.subprocess.Popen(
        ["alacritty", "-e", "bash", "-c", script],
        stdout=fn.subprocess.PIPE,
        stderr=fn.subprocess.PIPE,
    )

    def wait_and_refresh():
        process.wait()
        fn.invalidate_pkg_cache()
        fn.GLib.idle_add(_refresh_hblock_label, self)

    fn.threading.Thread(target=wait_and_refresh, daemon=True).start()


def on_click_enable_hblock(self, _widget):
    """Run hblock to populate /etc/hosts with blocklists."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, "hblock is not installed — install it first")
        return
    fn.log_subsection("Enable hblock")

    def run_enable():
        stop_pulse = fn.threading.Event()

        def _pulse():
            while not stop_pulse.is_set():
                fn.GLib.idle_add(self.progress.pulse)
                fn.time.sleep(0.1)

        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, "Enabling hblock...")
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, True)
        fn.GLib.idle_add(self.progress.set_visible, True)
        fn.threading.Thread(target=_pulse, daemon=True).start()
        fn.subprocess.run(
            ["/usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        stop_pulse.set()
        fn.log_success("hblock enabled")
        fn.GLib.idle_add(self.progress.set_visible, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, "hblock enabled")
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, False)
        fn.GLib.idle_add(fn.show_in_app_notification, self, "hblock enabled")
        fn.GLib.idle_add(
            self.lbl_hblock_status.set_markup,
            "Enable or disable hblock — check /etc/hosts <b>enabled</b>",
        )
        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, True)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, True)

    fn.threading.Thread(target=run_enable, daemon=True).start()


def on_click_disable_hblock(self, _widget):
    """Run hblock with empty sources to restore a clean /etc/hosts."""
    if not fn.check_package_installed("hblock"):
        fn.log_info("hblock is not installed")
        fn.show_in_app_notification(self, "hblock is not installed")
        return
    fn.log_subsection("Disable hblock")

    def run_disable():
        stop_pulse = fn.threading.Event()

        def _pulse():
            while not stop_pulse.is_set():
                fn.GLib.idle_add(self.progress.pulse)
                fn.time.sleep(0.1)

        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, "Disabling hblock...")
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, True)
        fn.GLib.idle_add(self.progress.set_visible, True)
        fn.threading.Thread(target=_pulse, daemon=True).start()
        fn.subprocess.run(
            ["sh", "-c", "HBLOCK_SOURCES='' /usr/bin/hblock"],
            stdout=fn.subprocess.PIPE,
            stderr=fn.subprocess.PIPE,
        )
        stop_pulse.set()
        fn.log_success("hblock disabled")
        fn.GLib.idle_add(self.progress.set_visible, False)
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_text, "hblock disabled")
        fn.GLib.idle_add(self.lbl_hblock_progress_msg.set_visible, False)
        fn.GLib.idle_add(fn.show_in_app_notification, self, "hblock disabled")
        fn.GLib.idle_add(
            self.lbl_hblock_status.set_markup,
            "Enable or disable hblock — check /etc/hosts disabled",
        )
        fn.GLib.idle_add(self.btn_enable_hblock.set_sensitive, True)
        fn.GLib.idle_add(self.btn_disable_hblock.set_sensitive, True)

    fn.threading.Thread(target=run_disable, daemon=True).start()
