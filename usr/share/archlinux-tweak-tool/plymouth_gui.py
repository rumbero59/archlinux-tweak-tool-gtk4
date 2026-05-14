import plymouth


def gui(self, Gtk, vboxstack_plymouth, fn):
    _default_theme = {
        "omarchy": "omarchy",
        "cachyos": "cachyos-bootanimation",
        "prismlinux": "prismlinux-theme",
    }.get(fn.distr)

    _plymouth_initialized = [False]

    # ── title ─────────────────────────────────────────────────────────────

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text("Plymouth")
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep_top = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_top.set_hexpand(True)
    hsep_top.set_vexpand(False)
    hbox_sep_top.append(hsep_top)

    # ── section: Install Plymouth ──────────────────────────────────────────

    hbox_section_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_install = Gtk.Label(xalign=0)
    lbl_section_install.set_markup("<b>Install Plymouth</b>")
    lbl_section_install.set_margin_start(10)
    lbl_section_install.set_margin_top(6)
    hbox_section_install.append(lbl_section_install)

    hbox_install_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_desc.set_margin_start(10)
    hbox_install_desc.set_margin_top(4)
    lbl_install_desc = Gtk.Label(xalign=0)
    lbl_install_desc.set_markup(
        "Installs plymouth, adds the plymouth hook to <tt>/etc/mkinitcpio.conf</tt>,\n"
        "and rebuilds the initramfs automatically."
    )
    hbox_install_desc.append(lbl_install_desc)

    hbox_install_plymouth = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_plymouth.set_margin_start(10)
    hbox_install_plymouth.set_margin_top(8)
    btn_install_plymouth = Gtk.Button(label="Install Plymouth")
    btn_install_plymouth.set_size_request(160, 30)
    lbl_plymouth_installed = Gtk.Label(xalign=0)
    lbl_plymouth_installed.set_markup("<b>Installed</b>")
    lbl_plymouth_installed.set_margin_start(10)
    lbl_plymouth_installed.set_visible(False)
    hbox_install_plymouth.append(btn_install_plymouth)
    hbox_install_plymouth.append(lbl_plymouth_installed)

    # ── section: Bootloader Integration ───────────────────────────────────

    hbox_sep_bootloader = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_bootloader.set_margin_top(10)
    hsep_bootloader = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_bootloader.set_hexpand(True)
    hsep_bootloader.set_vexpand(False)
    hbox_sep_bootloader.append(hsep_bootloader)

    hbox_section_bootloader = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_bootloader = Gtk.Label(xalign=0)
    lbl_section_bootloader.set_markup("<b>Bootloader Integration</b>")
    lbl_section_bootloader.set_margin_start(10)
    lbl_section_bootloader.set_margin_top(6)
    hbox_section_bootloader.append(lbl_section_bootloader)

    _bootloader = plymouth.detect_bootloader()

    hbox_bootloader_detected = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bootloader_detected.set_margin_start(10)
    hbox_bootloader_detected.set_margin_top(4)
    lbl_bootloader_title = Gtk.Label(xalign=0)
    lbl_bootloader_title.set_markup("Detected bootloader")
    lbl_bootloader_title.set_size_request(180, -1)
    lbl_bootloader_detected = Gtk.Label(xalign=0)
    lbl_bootloader_detected.set_text(_bootloader)
    hbox_bootloader_detected.append(lbl_bootloader_title)
    hbox_bootloader_detected.append(lbl_bootloader_detected)

    # systemd-boot splash check

    _use_cmdline = plymouth.check_kernel_cmdline_exists()

    hbox_sdboot_cmdline_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_cmdline_status.set_margin_start(10)
    hbox_sdboot_cmdline_status.set_margin_top(6)
    lbl_sdboot_cmdline_status = Gtk.Label(xalign=0)
    hbox_sdboot_cmdline_status.append(lbl_sdboot_cmdline_status)

    hbox_sdboot_entries_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_entries_status.set_margin_start(10)
    hbox_sdboot_entries_status.set_margin_top(4)
    lbl_sdboot_entries_status = Gtk.Label(xalign=0)
    hbox_sdboot_entries_status.append(lbl_sdboot_entries_status)

    hbox_sdboot_fix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sdboot_fix.set_margin_start(10)
    hbox_sdboot_fix.set_margin_top(6)
    btn_sdboot_fix = Gtk.Button(label="Add quiet splash to cmdline + entries")
    btn_sdboot_fix.set_size_request(260, 30)
    hbox_sdboot_fix.append(btn_sdboot_fix)

    if _bootloader == "systemd-boot":
        _cmdline_ok = plymouth.check_kernel_cmdline_splash() if _use_cmdline else True
        _sdboot_missing, _ = plymouth.check_systemd_boot_splash()
        _entries_ok = not bool(_sdboot_missing)
        _all_ok = _cmdline_ok and _entries_ok

        if _use_cmdline:
            if _cmdline_ok:
                lbl_sdboot_cmdline_status.set_markup(
                    "<b>OK:</b> <tt>/etc/kernel/cmdline</tt> contains <tt>quiet splash</tt>."
                )
            else:
                lbl_sdboot_cmdline_status.set_markup(
                    '<span foreground="#FFA500"><b>Warning:</b></span>'
                    " <tt>/etc/kernel/cmdline</tt> is missing <tt>quiet splash</tt>."
                )
        if _entries_ok:
            lbl_sdboot_entries_status.set_markup(
                "<b>OK:</b> all boot entries contain <tt>quiet splash</tt>."
            )
        else:
            _n = len(_sdboot_missing)
            lbl_sdboot_entries_status.set_markup(
                '<span foreground="#FFA500"><b>Warning:</b></span>'
                f" {_n} boot entr{'y' if _n == 1 else 'ies'} missing <tt>quiet splash</tt>."
            )
        hbox_sdboot_cmdline_status.set_visible(_use_cmdline)
        hbox_sdboot_entries_status.set_visible(True)
        hbox_sdboot_fix.set_visible(not _all_ok)
    else:
        hbox_sdboot_cmdline_status.set_visible(False)
        hbox_sdboot_entries_status.set_visible(False)
        hbox_sdboot_fix.set_visible(False)

    # GRUB splash check

    hbox_grub_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_grub_status.set_margin_start(10)
    hbox_grub_status.set_margin_top(6)
    lbl_grub_status = Gtk.Label(xalign=0)

    hbox_grub_fix = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_grub_fix.set_margin_start(10)
    hbox_grub_fix.set_margin_top(4)
    btn_grub_fix = Gtk.Button(label="Add quiet splash and run grub-mkconfig")
    btn_grub_fix.set_size_request(280, 30)
    hbox_grub_fix.append(btn_grub_fix)

    if _bootloader == "grub":
        if plymouth.check_grub_splash():
            lbl_grub_status.set_markup(
                "<b>OK:</b>"
                " <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> contains <tt>quiet splash</tt>."
            )
            btn_grub_fix.set_sensitive(False)
        else:
            lbl_grub_status.set_markup(
                '<span foreground="#FFA500"><b>Warning:</b></span>'
                " <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> in <tt>/etc/default/grub</tt>"
                " is missing <tt>quiet splash</tt>."
            )
        hbox_grub_status.append(lbl_grub_status)
        hbox_grub_status.set_visible(True)
        hbox_grub_fix.set_visible(not plymouth.check_grub_splash())
    else:
        hbox_grub_status.set_visible(False)
        hbox_grub_fix.set_visible(False)

    # limine / refind info

    hbox_bootloader_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_bootloader_info.set_margin_start(10)
    hbox_bootloader_info.set_margin_top(6)
    lbl_bootloader_info = Gtk.Label(xalign=0)

    if _bootloader == "limine":
        lbl_bootloader_info.set_markup(
            "Add <tt>quiet splash</tt> to the <tt>cmdline</tt>\n"
            "in your limine configuration file <tt>limine.conf</tt>"
        )
        hbox_bootloader_info.append(lbl_bootloader_info)
        hbox_bootloader_info.set_visible(True)
    elif _bootloader == "refind":
        lbl_bootloader_info.set_markup(
            "Add <tt>quiet splash</tt> to the <tt>options</tt> line\n"
            "in your rEFInd stanza (<tt>/boot/EFI/refind/refind.conf</tt>)."
        )
        hbox_bootloader_info.append(lbl_bootloader_info)
        hbox_bootloader_info.set_visible(True)
    else:
        hbox_bootloader_info.set_visible(False)

    # hooks order warning

    hbox_hooks_warn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hooks_warn.set_margin_start(10)
    hbox_hooks_warn.set_margin_top(6)
    lbl_hooks_warn = Gtk.Label(xalign=0)
    lbl_hooks_warn.set_markup(
        '<span foreground="#FFA500"><b>Warning:</b></span>'
        " In <tt>/etc/mkinitcpio.conf</tt>, <tt>encrypt</tt>/<tt>lvm2</tt> appears before"
        " <tt>plymouth</tt>.\n"
        "Move <tt>plymouth</tt> before <tt>encrypt</tt>/<tt>sd-encrypt</tt>/<tt>lvm2</tt>"
        " so the splash screen renders correctly."
    )
    hbox_hooks_warn.append(lbl_hooks_warn)
    hbox_hooks_warn.set_visible(not plymouth.check_hooks_order())

    # ── section: Installed themes ──────────────────────────────────────────

    hbox_sep_install = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_install.set_margin_top(10)
    hsep_install = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_install.set_hexpand(True)
    hsep_install.set_vexpand(False)
    hbox_sep_install.append(hsep_install)

    hbox_section_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_installed = Gtk.Label(xalign=0)
    lbl_section_installed.set_markup("<b>Installed themes</b>")
    lbl_section_installed.set_margin_start(10)
    lbl_section_installed.set_margin_top(6)
    hbox_section_installed.append(lbl_section_installed)

    # mkinitcpio hook warning

    _mkinitcpio_lines = fn.get_lines("/etc/mkinitcpio.conf") or []
    _hook_ok = any(
        "plymouth" in line
        for line in _mkinitcpio_lines
        if line.strip().startswith("HOOKS=")
    )

    hbox_hook_warn = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_hook_warn.set_margin_start(10)
    hbox_hook_warn.set_margin_top(4)
    lbl_hook_warn = Gtk.Label(xalign=0)
    lbl_hook_warn.set_markup(
        '<span foreground="#FFA500"><b>Warning:</b></span>'
        " plymouth hook not found in /etc/mkinitcpio.conf — themes will not render at boot."
    )
    hbox_hook_warn.append(lbl_hook_warn)
    hbox_hook_warn.set_visible(not _hook_ok)

    hbox_current = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_current.set_margin_start(10)
    hbox_current.set_margin_top(6)
    lbl_current_title = Gtk.Label(xalign=0)
    lbl_current_title.set_markup("<b>Active theme</b>")
    lbl_current_title.set_size_request(120, -1)
    lbl_current = Gtk.Label(xalign=0)
    lbl_current.set_text("")
    hbox_current.append(lbl_current_title)
    hbox_current.append(lbl_current)

    hbox_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_select.set_margin_start(10)
    hbox_select.set_margin_top(6)
    lbl_select = Gtk.Label(xalign=0)
    lbl_select.set_markup("Select theme")
    lbl_select.set_size_request(120, -1)
    dd_installed = Gtk.ComboBoxText()
    hbox_select.append(lbl_select)
    hbox_select.append(dd_installed)

    hbox_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_apply.set_margin_start(10)
    hbox_apply.set_margin_top(6)
    btn_apply = Gtk.Button(label="Apply theme")
    btn_apply.set_size_request(140, 30)
    hbox_apply.append(btn_apply)

    hbox_apply_desc = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_apply_desc.set_margin_start(10)
    hbox_apply_desc.set_margin_top(4)
    lbl_apply_desc = Gtk.Label(xalign=0)
    lbl_apply_desc.set_markup(
        "Applying a theme runs <tt>plymouth-set-default-theme -R</tt> which\n"
        "rebuilds the initramfs. This takes a few seconds."
    )
    hbox_apply_desc.append(lbl_apply_desc)

    hbox_reset = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_reset.set_margin_start(10)
    hbox_reset.set_margin_top(6)
    btn_reset = Gtk.Button(label=f"Reset to {fn.distr.capitalize()} default")
    btn_reset.set_size_request(200, 30)
    hbox_reset.append(btn_reset)
    hbox_reset.set_visible(_default_theme is not None)

    # ── section: Available themes ──────────────────────────────────────────

    hbox_sep_installed = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_sep_installed.set_margin_top(10)
    hsep_installed = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep_installed.set_hexpand(True)
    hsep_installed.set_vexpand(False)
    hbox_sep_installed.append(hsep_installed)

    hbox_section_available = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_section_available = Gtk.Label(xalign=0)
    lbl_section_available.set_markup("<b>Available themes</b>")
    lbl_section_available.set_margin_start(10)
    lbl_section_available.set_margin_top(6)
    lbl_section_available.set_hexpand(True)
    hbox_section_available.append(lbl_section_available)
    btn_refresh_avail = Gtk.Button(label="Refresh list")
    btn_refresh_avail.set_size_request(100, 28)
    btn_refresh_avail.set_margin_end(10)
    btn_refresh_avail.set_margin_top(4)
    hbox_section_available.append(btn_refresh_avail)

    hbox_avail_select = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_avail_select.set_margin_start(10)
    hbox_avail_select.set_margin_top(6)
    lbl_avail_select = Gtk.Label(xalign=0)
    lbl_avail_select.set_markup("Select package")
    lbl_avail_select.set_size_request(120, -1)
    dd_available = Gtk.ComboBoxText()
    hbox_avail_select.append(lbl_avail_select)
    hbox_avail_select.append(dd_available)

    hbox_install_theme = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_theme.set_margin_start(10)
    hbox_install_theme.set_margin_top(6)
    btn_install_theme = Gtk.Button(label="Install theme")
    btn_install_theme.set_size_request(140, 30)
    hbox_install_theme.append(btn_install_theme)

    hbox_install_note = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_install_note.set_margin_start(10)
    hbox_install_note.set_margin_top(4)
    lbl_install_note = Gtk.Label(xalign=0)
    lbl_install_note.set_markup(
        '<span foreground="#FFA500"><b>Note:</b></span>'
        " Installing a theme does not activate it."
        " Go to <b>Select theme</b> above and click <b>Apply theme</b>."
    )
    hbox_install_note.append(lbl_install_note)

    aur_helper = fn.get_aur_helper()
    repo_active = fn.check_nemesis_repo_active() or fn.check_chaotic_aur_active()
    if not aur_helper and not repo_active:
        btn_install_theme.set_sensitive(False)
        lbl_no_aur = Gtk.Label(xalign=0)
        lbl_no_aur.set_markup("<i>No AUR helper (paru/yay) or active repo found</i>")
        lbl_no_aur.set_margin_start(10)
        hbox_install_theme.append(lbl_no_aur)

    # ── populate dropdowns ─────────────────────────────────────────────────

    def populate_installed():
        dd_installed.remove_all()
        themes = plymouth.list_themes()
        current = plymouth.get_current_theme()
        for t in themes:
            dd_installed.append_text(t)
        if current in themes:
            dd_installed.set_active(themes.index(current))
        elif themes:
            dd_installed.set_active(0)

    def populate_available():
        dd_available.remove_all()
        pkgs = plymouth.list_available_packages()
        for p in pkgs:
            dd_available.append_text(p)
        if pkgs:
            dd_available.set_active(0)
        btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))

    def _refresh_plymouth(_widget):
        if _plymouth_initialized[0]:
            return
        _plymouth_initialized[0] = True
        installed = fn.check_package_installed("plymouth")
        lbl_plymouth_installed.set_visible(installed)
        if not installed:
            return

        def _load_initial_data():
            themes = plymouth.list_themes()
            current = plymouth.get_current_theme()
            pkgs = plymouth.list_available_packages()

            def _apply():
                dd_installed.remove_all()
                for t in themes:
                    dd_installed.append_text(t)
                if current in themes:
                    dd_installed.set_active(themes.index(current))
                elif themes:
                    dd_installed.set_active(0)
                lbl_current.set_text(current)
                dd_available.remove_all()
                for p in pkgs:
                    dd_available.append_text(p)
                if pkgs:
                    dd_available.set_active(0)
                btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))
                return False

            fn.GLib.idle_add(_apply)

        fn.threading.Thread(target=_load_initial_data, daemon=True).start()

    # ── callbacks ──────────────────────────────────────────────────────────

    def on_install_plymouth_clicked(_widget):
        fn.log_subsection("Installing Plymouth — full setup")
        fn.show_in_app_notification(self, "Installing Plymouth...")
        btn_install_plymouth.set_sensitive(False)

        script = (
            "set -euo pipefail\n"
            "trap 'echo \"\"; read -p \"Press Enter to close...\"' EXIT\n"
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
            "echo \"${CYAN}Step 1/3 — Installing plymouth...${RESET}\"\n"
            "pacman -S --noconfirm plymouth\n"
            "echo \"\"\n"
            "echo \"${CYAN}Step 2/3 — Adding plymouth hook to /etc/mkinitcpio.conf...${RESET}\"\n"
            "if grep -qP '(?:^|\\s)plymouth(?:\\s|$)' /etc/mkinitcpio.conf; then\n"
            "    echo '  plymouth hook already present — skipping'\n"
            "else\n"
            "    cp /etc/mkinitcpio.conf /etc/mkinitcpio.conf-bak\n"
            "    sed -i 's/\\budev\\b/udev plymouth/' /etc/mkinitcpio.conf\n"
            "    echo '  plymouth hook added after udev'\n"
            "fi\n"
            "echo \"\"\n"
            "echo \"${CYAN}Step 3/3 — Rebuilding initramfs (mkinitcpio -P)...${RESET}\"\n"
            "mkinitcpio -P\n"
            "echo \"\"\n"
            "echo \"${GREEN}Plymouth installation complete.${RESET}\"\n"
        )

        def run_install():
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(on_install_plymouth_done)

        fn.threading.Thread(target=run_install, daemon=True).start()

    def on_install_plymouth_done():
        btn_install_plymouth.set_sensitive(True)
        if fn.check_package_installed("plymouth"):
            fn.log_success("Plymouth installed — refreshing theme manager")
            lbl_plymouth_installed.set_visible(True)
            lines = fn.get_lines("/etc/mkinitcpio.conf") or []
            hook_present = any(
                "plymouth" in line
                for line in lines
                if line.strip().startswith("HOOKS=")
            )
            hbox_hook_warn.set_visible(not hook_present)
            lbl_current.set_text(plymouth.get_current_theme())
            populate_installed()
            populate_available()
        else:
            fn.log_warn("Plymouth package not found after install — check terminal output")

    def on_apply_clicked(_widget):
        selected = dd_installed.get_active_text()
        if not selected:
            fn.log_warn("No Plymouth theme selected")
            return
        fn.log_subsection(f"Applying Plymouth theme: {selected}")
        fn.show_in_app_notification(self, f"Applying Plymouth theme: {selected}")
        script = (
            f"echo 'Setting Plymouth theme to {selected}...'\n"
            f"plymouth-set-default-theme -R {selected}\n"
            "echo ''\n"
            "read -p 'Done. Press Enter to close...'\n"
        )

        def run_apply():
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            if fn.distr == "omarchy":
                fn.os.makedirs("/etc/att", exist_ok=True)
                open("/etc/att/att-omarchy-marker", "w").close()
                fn.log_info("ATT Omarchy marker written to /etc/att/att-omarchy-marker")
            fn.GLib.idle_add(refresh_after_apply)

        fn.threading.Thread(target=run_apply, daemon=True).start()

    def refresh_after_apply():
        new_theme = plymouth.get_current_theme()
        lbl_current.set_text(new_theme)
        fn.log_success(f"Plymouth theme now: {new_theme}")
        populate_installed()

    def on_install_theme_clicked(_widget):
        selected = dd_available.get_active_text()
        if not selected:
            fn.log_warn("No Plymouth package selected")
            return
        fn.log_subsection(f"Installing Plymouth theme package: {selected}")
        fn.show_in_app_notification(self, f"Installing: {selected}")

        def run_install():
            if aur_helper:
                process = fn.launch_aur_install_in_terminal(aur_helper, selected)
            else:
                process = fn.launch_pacman_install_in_terminal(selected)
            if process:
                process.wait()
                fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_after_install)

        fn.threading.Thread(target=run_install, daemon=True).start()

    def refresh_after_install():
        populate_installed()
        populate_available()
        fn.log_success("Plymouth theme list refreshed")

    def on_reset_clicked(_widget):
        fn.log_subsection(f"Resetting Plymouth theme to {fn.distr.capitalize()} default")
        fn.show_in_app_notification(self, f"Resetting Plymouth theme to {_default_theme}...")
        themes = plymouth.list_themes()
        if _default_theme in themes:
            dd_installed.set_active(themes.index(_default_theme))
        script = (
            f"echo 'Resetting Plymouth theme to {_default_theme}...'\n"
            f"plymouth-set-default-theme -R {_default_theme}\n"
            "echo ''\n"
            "read -p 'Done. Press Enter to close...'\n"
        )

        def run_reset():
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_after_apply)

        fn.threading.Thread(target=run_reset, daemon=True).start()

    def on_refresh_avail_clicked(_widget):
        fn.log_subsection("Refreshing Plymouth available themes...")
        fn.show_in_app_notification(self, "Refreshing available themes...")
        btn_refresh_avail.set_sensitive(False)

        def _fetch():
            pkgs = plymouth.list_available_packages()
            themes = plymouth.list_themes()
            current = plymouth.get_current_theme()

            def _update():
                dd_available.remove_all()
                for p in pkgs:
                    dd_available.append_text(p)
                if pkgs:
                    dd_available.set_active(0)
                btn_install_theme.set_sensitive(bool(pkgs) and (aur_helper is not None or repo_active))
                dd_installed.remove_all()
                for t in themes:
                    dd_installed.append_text(t)
                if current in themes:
                    dd_installed.set_active(themes.index(current))
                elif themes:
                    dd_installed.set_active(0)
                lbl_current.set_text(current)
                btn_refresh_avail.set_sensitive(True)
                fn.log_success("Plymouth theme list refreshed")

            fn.GLib.idle_add(_update)

        fn.threading.Thread(target=_fetch, daemon=True).start()

    def on_sdboot_fix_clicked(_widget):
        fn.log_subsection("Adding quiet splash to cmdline + entries")
        fn.show_in_app_notification(self, "Adding quiet splash to cmdline + entries...")
        btn_sdboot_fix.set_sensitive(False)

        def run_both():
            if _use_cmdline:
                try:
                    content = open(plymouth.KERNEL_CMDLINE).read().rstrip()
                    tokens = content.split()
                    if "quiet" not in tokens:
                        content += " quiet"
                    if "splash" not in tokens:
                        content += " splash"
                    open(plymouth.KERNEL_CMDLINE, "w").write(content.strip() + "\n")
                    fn.log_info(f"Patched: {plymouth.KERNEL_CMDLINE}")
                except OSError as e:
                    fn.log_error(f"Could not patch {plymouth.KERNEL_CMDLINE}: {e}")
            missing, _ = plymouth.check_systemd_boot_splash()
            for path in missing:
                try:
                    lines = open(path).readlines()
                    new_lines = []
                    for line in lines:
                        if line.strip().startswith("options"):
                            stripped = line.rstrip()
                            tokens = stripped.split()
                            if "quiet" not in tokens:
                                stripped += " quiet"
                            if "splash" not in tokens:
                                stripped += " splash"
                            new_lines.append(stripped + "\n")
                        else:
                            new_lines.append(line)
                    open(path, "w").writelines(new_lines)
                    fn.log_info(f"Patched: {path}")
                except OSError as e:
                    fn.log_error(f"Could not patch {path}: {e}")
            fn.GLib.idle_add(refresh_sdboot_status)

        fn.threading.Thread(target=run_both, daemon=True).start()

    def refresh_sdboot_status():
        cmdline_ok = plymouth.check_kernel_cmdline_splash() if _use_cmdline else True
        new_missing, _ = plymouth.check_systemd_boot_splash()
        entries_ok = not bool(new_missing)
        all_ok = cmdline_ok and entries_ok
        if _use_cmdline:
            if cmdline_ok:
                lbl_sdboot_cmdline_status.set_markup(
                    "<b>OK:</b> <tt>/etc/kernel/cmdline</tt> contains <tt>quiet splash</tt>."
                )
            else:
                lbl_sdboot_cmdline_status.set_markup(
                    '<span foreground="#FFA500"><b>Warning:</b></span>'
                    " <tt>/etc/kernel/cmdline</tt> is missing <tt>quiet splash</tt>."
                )
        if entries_ok:
            lbl_sdboot_entries_status.set_markup(
                "<b>OK:</b> all boot entries contain <tt>quiet splash</tt>."
            )
        else:
            n = len(new_missing)
            lbl_sdboot_entries_status.set_markup(
                '<span foreground="#FFA500"><b>Warning:</b></span>'
                f" {n} boot entr{'y' if n == 1 else 'ies'} missing <tt>quiet splash</tt>."
            )
        if all_ok:
            hbox_sdboot_fix.set_visible(False)
        else:
            btn_sdboot_fix.set_sensitive(True)
        fn.log_success("systemd-boot splash status refreshed")

    def on_grub_fix_clicked(_widget):
        fn.log_subsection("Adding quiet splash to GRUB config")
        fn.show_in_app_notification(self, "Patching GRUB config and regenerating...")
        btn_grub_fix.set_sensitive(False)
        script = (
            "set -euo pipefail\n"
            "RESET=$(tput sgr0); CYAN=$(tput setaf 6); GREEN=$(tput setaf 2)\n"
            "echo \"${CYAN}Step 1/2 — Patching /etc/default/grub...${RESET}\"\n"
            "cp /etc/default/grub /etc/default/grub-bak\n"
            r"""sed -i 's/^\(GRUB_CMDLINE_LINUX_DEFAULT="[^"]*\)"/\1 quiet splash"/' /etc/default/grub"""
            "\n"
            "echo \"${CYAN}Step 2/2 — Regenerating GRUB config...${RESET}\"\n"
            "grub-mkconfig -o /boot/grub/grub.cfg\n"
            "echo \"\"\n"
            "echo \"${GREEN}Done.${RESET}\"\n"
            "read -p 'Press Enter to close...'\n"
        )

        def run_grub():
            fn.debug_print(f"Terminal cmd: {script}")
            process = fn.subprocess.Popen(
                ["alacritty", "-e", "bash", "-c", script],
                stdout=fn.subprocess.PIPE,
                stderr=fn.subprocess.PIPE,
            )
            process.wait()
            fn.invalidate_pkg_cache()
            fn.GLib.idle_add(refresh_grub_status)

        fn.threading.Thread(target=run_grub, daemon=True).start()

    def refresh_grub_status():
        if plymouth.check_grub_splash():
            lbl_grub_status.set_markup(
                "<b>OK:</b>"
                " <tt>GRUB_CMDLINE_LINUX_DEFAULT</tt> contains <tt>quiet splash</tt>."
            )
            hbox_grub_fix.set_visible(False)
        else:
            btn_grub_fix.set_sensitive(True)
        fn.log_success("GRUB splash status refreshed")

    btn_install_plymouth.connect("clicked", on_install_plymouth_clicked)
    btn_sdboot_fix.connect("clicked", on_sdboot_fix_clicked)
    btn_grub_fix.connect("clicked", on_grub_fix_clicked)
    btn_apply.connect("clicked", on_apply_clicked)
    btn_install_theme.connect("clicked", on_install_theme_clicked)
    btn_reset.connect("clicked", on_reset_clicked)
    btn_refresh_avail.connect("clicked", on_refresh_avail_clicked)

    # ── layout ─────────────────────────────────────────────────────────────

    vboxstack_plymouth.append(hbox_title)
    vboxstack_plymouth.append(hbox_sep_top)
    vboxstack_plymouth.append(hbox_section_install)
    vboxstack_plymouth.append(hbox_install_desc)
    vboxstack_plymouth.append(hbox_install_plymouth)
    vboxstack_plymouth.append(hbox_sep_bootloader)
    vboxstack_plymouth.append(hbox_section_bootloader)
    vboxstack_plymouth.append(hbox_bootloader_detected)
    vboxstack_plymouth.append(hbox_sdboot_cmdline_status)
    vboxstack_plymouth.append(hbox_sdboot_entries_status)
    vboxstack_plymouth.append(hbox_sdboot_fix)
    vboxstack_plymouth.append(hbox_grub_status)
    vboxstack_plymouth.append(hbox_grub_fix)
    vboxstack_plymouth.append(hbox_bootloader_info)
    vboxstack_plymouth.append(hbox_hooks_warn)
    vboxstack_plymouth.append(hbox_sep_install)
    vboxstack_plymouth.append(hbox_section_installed)
    vboxstack_plymouth.append(hbox_hook_warn)
    vboxstack_plymouth.append(hbox_current)
    vboxstack_plymouth.append(hbox_select)
    vboxstack_plymouth.append(hbox_apply)
    vboxstack_plymouth.append(hbox_apply_desc)
    vboxstack_plymouth.append(hbox_reset)
    vboxstack_plymouth.append(hbox_sep_installed)
    vboxstack_plymouth.append(hbox_section_available)
    vboxstack_plymouth.append(hbox_avail_select)
    vboxstack_plymouth.append(hbox_install_theme)
    vboxstack_plymouth.append(hbox_install_note)

    vboxstack_plymouth.connect("map", _refresh_plymouth)
