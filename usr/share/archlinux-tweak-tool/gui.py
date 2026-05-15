# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================

# ============Functions============
import functions as fn

import desktopr
import maintenance
import fastfetch
import performance
import sddm
import icons
import themes
import themer
import user
import zsh_theme

# =============GUI=================
import icons_gui
import themes_gui
import autostart
import desktopr_gui
import maintenance_gui
import fastfetch_gui
import kernel_gui
import pacman_gui
import performance_gui
import sddm_gui
import privacy_gui
import services_gui
import shell_gui
import themer_gui
import user_gui
import ai_gui
import logging_gui
import network_gui
import system_gui
import software_gui
import packages_gui
import wallpaper
import wallpaper_gui
import plymouth_gui
import locale_gui
import dev_gui

_SDDM_HIDDEN_DISTROS = {"prismlinux"}


def gui(self, Gtk, Gdk, GdkPixbuf, base_dir, os, Pango, GLib):
    """creation of the gui"""

    # =======================================================
    #                       App Notifications
    # =======================================================

    hbox_notification = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    self.notification_revealer = Gtk.Revealer()
    self.notification_revealer.set_reveal_child(False)

    self.notification_label = Gtk.Label()
    self.notification_label.set_hexpand(True)

    notification_bg = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    notification_bg.set_size_request(-1, 30)
    notification_bg.add_css_class("att-notification-bar")
    notification_bg.append(self.notification_label)

    css_notif = Gtk.CssProvider()
    css_notif.load_from_data(b".att-notification-bar { background-color: #1a1a1a; }")
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_notif,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )

    self.notification_revealer.set_child(notification_bg)

    self.notification_revealer.set_hexpand(True)
    self.notification_revealer.set_vexpand(False)
    hbox_notification.append(self.notification_revealer)

    # ==========================================================
    #                       CONTAINER
    # ==========================================================

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    vbox_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

    hbox.set_hexpand(True)
    hbox.set_vexpand(True)
    vbox.append(hbox_notification)
    vbox.append(hbox)
    self.set_child(vbox)

    # ==========================================================
    #                    INITIALIZE STACK
    # ==========================================================
    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT)
    stack.set_transition_duration(350)

    vboxstack1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_fastfetch = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack10 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_desktop = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_autostart = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack14 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack18 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack19 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack23 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack25 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack26 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack27 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack28 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_sddm = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_ai = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_logging = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_network = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_system = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_software = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_themes = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_wallpaper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_plymouth = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_locale = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack_dev = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # ==========================================================
    #                 LAZY TAB BUILDER
    # ==========================================================

    def _defer_tab(container, build_fn):
        built = [False]

        def on_map(_widget):
            if not built[0]:
                built[0] = True
                build_fn()

        container.connect("map", on_map)

    # ==========================================================
    #                 ICONS
    # ==========================================================

    _defer_tab(vboxstack25, lambda: icons_gui.gui(self, Gtk, GdkPixbuf, vboxstack25, icons, fn, base_dir))

    # ==========================================================
    #                THEMES
    # ==========================================================

    _defer_tab(vboxstack_themes, lambda: themes_gui.gui(self, Gtk, GdkPixbuf, vboxstack_themes, themes, fn, base_dir))

    # ==========================================================
    #                AUTOSTART
    # ==========================================================

    _defer_tab(vboxstack_autostart, lambda: autostart.gui(self, Gtk, vboxstack_autostart, fn))

    # ==========================================================
    #                DESKTOP
    # ==========================================================

    _defer_tab(vboxstack_desktop,
               lambda: desktopr_gui.gui(self, Gtk, GdkPixbuf, vboxstack_desktop, desktopr, fn, base_dir))

    # # ==========================================================
    # #               FASTFETCH
    # # ==========================================================

    def _build_fastfetch():
        if fn.file_check(fn.fastfetch_config):
            fastfetch_gui.gui(self, Gtk, GdkPixbuf, vboxstack_fastfetch, fastfetch, fn, base_dir)
        else:
            hbox_ff_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            hbox_ff_separator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            lbl1 = Gtk.Label(xalign=0)
            lbl1.set_text("fastfetch Editor")
            lbl1.set_name("title")
            hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            hseparator.set_hexpand(True)
            hseparator.set_vexpand(False)
            hbox_ff_separator.append(hseparator)
            hbox_ff_title.append(lbl1)
            vboxstack_fastfetch.append(hbox_ff_title)
            vboxstack_fastfetch.append(hbox_ff_separator)
            fastfetch_message = Gtk.Label()
            fastfetch_message.set_hexpand(True)
            fastfetch_message.set_markup(
                "fastfetch configuration file not found.\n"
                "Install <b>fastfetch</b> and enable it to use this tab."
            )
            vboxstack_fastfetch.append(fastfetch_message)

    _defer_tab(vboxstack_fastfetch, _build_fastfetch)

    # # ==========================================================
    # #               MAINTENANCE
    # # ==========================================================

    _defer_tab(vboxstack19, lambda: maintenance_gui.gui(self, Gtk, Gdk, GdkPixbuf, vboxstack19, fn, maintenance))

    # ==========================================================
    #                 PACMAN
    # ==========================================================

    if fn.file_check(fn.pacman):
        pacman_gui.gui(self, Gtk, vboxstack1, fn)

    # ==========================================================
    #                 PRIVACY - HBLOCK
    # ==========================================================

    privacy_gui.gui(self, Gtk, vboxstack3, fn)

    # ==========================================================
    #                      SERVICES
    # ==========================================================

    _defer_tab(vboxstack14, lambda: services_gui.gui(self, Gtk, vboxstack14, fn))

    # ==========================================================
    #                        SHELLS
    # ==========================================================

    _defer_tab(vboxstack23, lambda: shell_gui.gui(self, Gtk, vboxstack23, zsh_theme, base_dir, GdkPixbuf, fn))

    # ==========================================================
    #                 THEMER
    # ==========================================================

    def _build_themer():
        themer_gui.gui(self, Gtk, GdkPixbuf, vboxstack10, themer, fn, base_dir)
        self.on_desktop_changed = lambda: themer_gui.refresh_themer_dropdowns(self, fn, themer)

    _defer_tab(vboxstack10, _build_themer)

    # # ==========================================================
    # #                USER
    # # ==========================================================

    _defer_tab(vboxstack18, lambda: user_gui.gui(self, Gtk, vboxstack18, user, fn))

    # =====================================================
    #                       PACKAGES - EXPORT/INSTALL
    # =====================================================

    _defer_tab(vboxstack26, lambda: packages_gui.gui(self, Gtk, vboxstack26, fn))

    # =====================================================
    #                       PERFORMANCE
    # =====================================================

    if fn.distr != "artix":
        performance_gui.gui(self, Gtk, vboxstack27, performance, fn)

    # =====================================================
    #                       SDDM
    # =====================================================

    def _build_sddm():
        sddm_gui.gui(self, Gtk, Pango, vboxstack_sddm, sddm, fn)

        def _rebuild_sddm_page():
            child = vboxstack_sddm.get_first_child()
            while child:
                vboxstack_sddm.remove(child)
                child = vboxstack_sddm.get_first_child()
            sddm_gui.gui(self, Gtk, Pango, vboxstack_sddm, sddm, fn)

        self.rebuild_sddm_page = _rebuild_sddm_page

    _defer_tab(vboxstack_sddm, _build_sddm)

    _defer_tab(vboxstack28, lambda: kernel_gui.gui(self, Gtk, vboxstack28, fn))

    _defer_tab(vboxstack_ai, lambda: ai_gui.gui(self, Gtk, vboxstack_ai, fn))

    _defer_tab(vboxstack_logging, lambda: logging_gui.gui(self, Gtk, vboxstack_logging, fn))

    network_gui.gui(self, Gtk, vboxstack_network, fn)

    _defer_tab(vboxstack_system, lambda: system_gui.gui(self, Gtk, vboxstack_system, fn))

    _defer_tab(vboxstack_software, lambda: software_gui.gui(self, Gtk, vboxstack_software, fn))

    wallpaper_gui.gui(self, Gtk, Pango, vboxstack_wallpaper, wallpaper, fn, base_dir)

    _defer_tab(vboxstack_plymouth, lambda: plymouth_gui.gui(self, Gtk, vboxstack_plymouth, fn))

    _defer_tab(vboxstack_locale, lambda: locale_gui.gui(self, Gtk, vboxstack_locale, fn))

    if fn.DEV:
        dev_gui.gui(self, Gtk, vboxstack_dev, fn)

    # ==========================================================
    #                   ADD TO WINDOW
    # ==========================================================
    stack.add_titled(vboxstack_ai, "stack_ai", "AI Tools")  # AI tools

    stack.add_titled(vboxstack_autostart, "stack13", "Autostart")  # Autostart

    stack.add_titled(vboxstack_desktop, "stack12", "Desktop")  # Desktop installer

    if fn.distr != "garuda":
        stack.add_titled(vboxstack_fastfetch, "stack4", "Fastfetch")  # fastfetch config

    stack.add_titled(vboxstack25, "stack25", "Icons")  # Icons and themes

    stack.add_titled(vboxstack28, "stack28", "Kernels")  # kernel manager

    stack.add_titled(vboxstack_locale, "stack_locale", "Locale")  # locale, keyboard, timezone

    stack.add_titled(vboxstack_logging, "stack_logging", "Logging")  # log investigator

    stack.add_titled(vboxstack19, "stack19", "Maintenance")  # Maintenance

    stack.add_titled(vboxstack_network, "stack_network", "Network")  # network + samba

    stack.add_titled(vboxstack26, "packages", "Packages")  # Packages

    stack.add_titled(vboxstack1, "stack6", "Pacman")  # Pacman config

    stack.add_titled(vboxstack_plymouth, "stack_plymouth", "Plymouth")  # Plymouth boot theme

    stack.add_titled(vboxstack3, "stack2", "Privacy")  # Privacy

    if fn.distr != "artix":
        stack.add_titled(vboxstack27, "stack27", "Performance")  # performance

    if (fn.distr not in _SDDM_HIDDEN_DISTROS
            and not (fn.check_service_enabled("plasma-login") or fn.check_service_enabled("plasmalogin"))):
        stack.add_titled(vboxstack_sddm, "stack_sddm", "Sddm")  # sddm

    if fn.distr != "artix":
        stack.add_titled(vboxstack14, "stack14", "Services")  # services

    stack.add_titled(vboxstack23, "stack23", "Shells")  # shell

    stack.add_titled(vboxstack_software, "stack_software", "Software")  # software installers

    stack.add_titled(vboxstack_system, "stack_system", "System")  # system inspector

    stack.add_titled(vboxstack10, "stack11", "Themer")  # Themer

    stack.add_titled(vboxstack_themes, "stack_themes", "Themes")  # arc themes

    stack.add_titled(vboxstack18, "stack18", "User")  # user

    stack.add_titled(vboxstack_wallpaper, "stack_wallpaper", "Wallpaper")  # wallpaper

    if fn.DEV:
        stack.add_titled(vboxstack_dev, "stack_dev", "Dev")

    stack_switcher = Gtk.StackSidebar()
    stack_switcher.set_name("sidebar")
    stack_switcher.set_stack(stack)

    # =====================================================
    #                       LOGO
    # =====================================================

    ivbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    # =====================================================
    #               RESTART/QUIT BUTTON
    # =====================================================

    def on_quit(widget):
        fn.unlink("/tmp/att.lock")
        self.get_application().quit()
        fn.debug_print("Thanks for using ArchLinux Tweak Tool")
        fn.debug_print("Report issues to make it even better")
        fn.debug_print("=" * 75)

    lbl_os_label = Gtk.Label(xalign=0)
    lbl_os_label.set_markup("OS: " + fn.get_distro_label())
    btn_restart_att = Gtk.Button(label="Restart ATT")
    btn_restart_att.set_size_request(100, 30)
    btn_restart_att.set_visible(False)
    btn_restart_att.connect("clicked", self.on_refresh_att_clicked)
    btn_quit_att = Gtk.Button(label="Quit ATT")
    btn_quit_att.set_size_request(100, 30)
    btn_quit_att.connect("clicked", on_quit)

    # =====================================================
    #                      PACKS
    # =====================================================

    hbox_restart_att = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
    hbox_quit_att = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
    hbox_os_label = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)

    hbox_os_label.append(lbl_os_label)
    hbox_restart_att.append(btn_restart_att)
    hbox_quit_att.append(btn_quit_att)

    stack_switcher.set_size_request(70, -1)
    stack_switcher.set_hexpand(False)
    stack_switcher.set_vexpand(True)
    ivbox.append(stack_switcher)

    ivbox.append(hbox_os_label)
    ivbox.append(hbox_restart_att)
    ivbox.append(hbox_quit_att)

    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox_content.append(stack)

    # make the content scrollable
    scrolledWindow = Gtk.ScrolledWindow()
    scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
    scrolledWindow.set_child(vbox_content)

    hbox.append(ivbox)
    scrolledWindow.set_hexpand(True)
    scrolledWindow.set_vexpand(True)
    hbox.append(scrolledWindow)

    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)
