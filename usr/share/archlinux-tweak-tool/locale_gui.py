# ============================================================
# Authors: Erik Dubois
# ============================================================

import functools
import subprocess
import locale_settings as locale


def _fetch(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()


def _find_idx(items, value):
    try:
        return items.index(value)
    except ValueError:
        return 0


def gui(self, Gtk, vboxstack_locale, fn):
    """Create the Locale, Keyboard and Timezone page."""

    # ── Title ─────────────────────────────────────────────
    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Locale, Keyboard & Timezone")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep.set_hexpand(True)
    hbox_sep.append(hsep)

    # ── Section: Current Settings ─────────────────────────
    hbox_status_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_status_header = Gtk.Label(xalign=0)
    lbl_status_header.set_markup("<b>Current Settings</b>")
    lbl_status_header.set_margin_start(10)
    lbl_status_header.set_margin_top(15)
    lbl_status_header.set_margin_bottom(5)
    hbox_status_header.append(lbl_status_header)

    hbox_locale_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_locale_key = Gtk.Label(xalign=0)
    lbl_locale_key.set_text("System Locale:")
    lbl_locale_key.set_margin_start(10)
    lbl_locale_key.set_size_request(160, -1)
    self.lbl_locale_current = Gtk.Label(xalign=0)
    self.lbl_locale_current.set_margin_start(10)
    hbox_locale_status.append(lbl_locale_key)
    hbox_locale_status.append(self.lbl_locale_current)

    hbox_keymap_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_keymap_key = Gtk.Label(xalign=0)
    lbl_keymap_key.set_text("Console Keymap:")
    lbl_keymap_key.set_margin_start(10)
    lbl_keymap_key.set_size_request(160, -1)
    self.lbl_keymap_current = Gtk.Label(xalign=0)
    self.lbl_keymap_current.set_margin_start(10)
    hbox_keymap_status.append(lbl_keymap_key)
    hbox_keymap_status.append(self.lbl_keymap_current)

    hbox_x11_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_key = Gtk.Label(xalign=0)
    lbl_x11_key.set_text("X11 Layout:")
    lbl_x11_key.set_margin_start(10)
    lbl_x11_key.set_size_request(160, -1)
    self.lbl_x11_current = Gtk.Label(xalign=0)
    self.lbl_x11_current.set_margin_start(10)
    hbox_x11_status.append(lbl_x11_key)
    hbox_x11_status.append(self.lbl_x11_current)

    hbox_tz_status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_tz_key = Gtk.Label(xalign=0)
    lbl_tz_key.set_text("Timezone:")
    lbl_tz_key.set_margin_start(10)
    lbl_tz_key.set_size_request(160, -1)
    self.lbl_timezone_current = Gtk.Label(xalign=0)
    self.lbl_timezone_current.set_margin_start(10)
    hbox_tz_status.append(lbl_tz_key)
    hbox_tz_status.append(self.lbl_timezone_current)

    # ── Fetch data for dropdowns ───────────────────────────
    locales = _fetch(["localectl", "list-locales"]) or ["en_US.UTF-8"]
    keymaps = _fetch(["localectl", "list-keymaps"]) or ["us"]
    x11_layouts = _fetch(["localectl", "list-x11-keymap-layouts"]) or ["us"]
    timezones = _fetch(["timedatectl", "list-timezones"]) or ["UTC"]

    status_raw = subprocess.run(["localectl", "status"], capture_output=True, text=True).stdout
    parsed = {}
    for line in status_raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            parsed[k.strip()] = v.strip()

    current_locale = parsed.get("System Locale", "LANG=en_US.UTF-8").replace("LANG=", "")
    current_keymap = parsed.get("VC Keymap", "")
    current_x11_layout = parsed.get("X11 Layout", "")
    current_x11_variant = parsed.get("X11 Variant", "")
    current_tz = subprocess.run(
        ["timedatectl", "show", "--property=Timezone", "--value"],
        capture_output=True, text=True
    ).stdout.strip()

    # ── Section: System Locale ─────────────────────────────
    hbox_locale_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_locale_header = Gtk.Label(xalign=0)
    lbl_locale_header.set_markup("<b>System Locale</b>")
    lbl_locale_header.set_margin_start(10)
    lbl_locale_header.set_margin_top(15)
    lbl_locale_header.set_margin_bottom(5)
    hbox_locale_header.append(lbl_locale_header)

    hbox_locale_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.locale_dropdown = Gtk.DropDown.new_from_strings(locales)
    self.locale_dropdown.set_size_request(300, -1)
    self.locale_dropdown.set_margin_start(10)
    self.locale_dropdown.set_selected(_find_idx(locales, current_locale))
    btn_locale_apply = Gtk.Button(label="Apply")
    btn_locale_apply.set_margin_start(10)
    btn_locale_apply.connect("clicked", functools.partial(locale.on_apply_locale, self))
    hbox_locale_ctrl.append(self.locale_dropdown)
    hbox_locale_ctrl.append(btn_locale_apply)

    # ── Section: Generate New Locale ──────────────────────
    hbox_gen_locale_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_gen_locale_header = Gtk.Label(xalign=0)
    lbl_gen_locale_header.set_markup("<b>Generate New Locale</b>")
    lbl_gen_locale_header.set_margin_start(10)
    lbl_gen_locale_header.set_margin_top(15)
    lbl_gen_locale_header.set_margin_bottom(5)
    hbox_gen_locale_header.append(lbl_gen_locale_header)

    hbox_gen_locale_load = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_load_available = Gtk.Button(label="Load Available Locales")
    btn_load_available.set_margin_start(10)
    self.available_locale_dropdown = Gtk.DropDown.new_from_strings([""])
    self.available_locale_dropdown.set_size_request(300, -1)
    self.available_locale_dropdown.set_sensitive(False)
    hbox_gen_locale_load.append(btn_load_available)
    hbox_gen_locale_load.append(self.available_locale_dropdown)

    hbox_gen_locale_apply = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.btn_available_apply = Gtk.Button(label="Apply")
    self.btn_available_apply.set_margin_start(10)
    self.btn_available_apply.set_sensitive(False)
    self.btn_available_apply.connect("clicked", functools.partial(locale.on_apply_generate_locale, self))
    hbox_gen_locale_apply.append(self.btn_available_apply)

    def _on_load_available(_widget):
        available = locale.get_available_locales()
        fn.log_info(f"Loaded {len(available)} available locales")
        model = Gtk.StringList()
        for loc in available:
            model.append(loc)
        self.available_locale_dropdown.set_model(model)
        self.available_locale_dropdown.set_sensitive(True)
        self.btn_available_apply.set_sensitive(True)

    btn_load_available.connect("clicked", _on_load_available)

    # ── Section: Console Keyboard (TTY) ───────────────────
    hbox_keymap_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_keymap_header = Gtk.Label(xalign=0)
    lbl_keymap_header.set_markup("<b>Console Keyboard (TTY)</b>")
    lbl_keymap_header.set_margin_start(10)
    lbl_keymap_header.set_margin_top(15)
    lbl_keymap_header.set_margin_bottom(5)
    hbox_keymap_header.append(lbl_keymap_header)

    hbox_keymap_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.keymap_dropdown = Gtk.DropDown.new_from_strings(keymaps)
    self.keymap_dropdown.set_size_request(300, -1)
    self.keymap_dropdown.set_margin_start(10)
    self.keymap_dropdown.set_selected(_find_idx(keymaps, current_keymap))
    btn_keymap_apply = Gtk.Button(label="Apply")
    btn_keymap_apply.set_margin_start(10)
    btn_keymap_apply.connect("clicked", functools.partial(locale.on_apply_keymap, self))
    btn_keymap_sync = Gtk.Button(label="Sync from X11")
    btn_keymap_sync.set_margin_start(10)
    btn_keymap_sync.connect("clicked", functools.partial(locale.on_sync_keymap, self))
    hbox_keymap_ctrl.append(self.keymap_dropdown)
    hbox_keymap_ctrl.append(btn_keymap_apply)
    hbox_keymap_ctrl.append(btn_keymap_sync)

    # ── Section: X11 / Wayland Keyboard ───────────────────
    hbox_x11_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_header = Gtk.Label(xalign=0)
    lbl_x11_header.set_markup("<b>X11 / Wayland Keyboard</b>")
    lbl_x11_header.set_margin_start(10)
    lbl_x11_header.set_margin_top(15)
    lbl_x11_header.set_margin_bottom(5)
    hbox_x11_header.append(lbl_x11_header)

    hbox_x11_layout_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_layout = Gtk.Label(xalign=0)
    lbl_x11_layout.set_text("Layout:")
    lbl_x11_layout.set_margin_start(10)
    lbl_x11_layout.set_size_request(70, -1)
    self.x11_layout_dropdown = Gtk.DropDown.new_from_strings(x11_layouts)
    self.x11_layout_dropdown.set_size_request(250, -1)
    hbox_x11_layout_ctrl.append(lbl_x11_layout)
    hbox_x11_layout_ctrl.append(self.x11_layout_dropdown)

    hbox_x11_variant_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_x11_variant = Gtk.Label(xalign=0)
    lbl_x11_variant.set_text("Variant:")
    lbl_x11_variant.set_margin_start(10)
    lbl_x11_variant.set_size_request(70, -1)
    self.x11_variant_dropdown = Gtk.DropDown.new_from_strings([""])
    self.x11_variant_dropdown.set_size_request(250, -1)
    hbox_x11_variant_ctrl.append(lbl_x11_variant)
    hbox_x11_variant_ctrl.append(self.x11_variant_dropdown)

    hbox_x11_apply_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    btn_x11_apply = Gtk.Button(label="Apply")
    btn_x11_apply.set_margin_start(10)
    btn_x11_apply.connect("clicked", functools.partial(locale.on_apply_x11, self))
    hbox_x11_apply_ctrl.append(btn_x11_apply)

    # Pre-select X11 layout and populate variants before connecting the signal
    if current_x11_layout in x11_layouts:
        self.x11_layout_dropdown.set_selected(x11_layouts.index(current_x11_layout))
    variants = locale.get_x11_variants(current_x11_layout) if current_x11_layout else [""]
    variant_model = Gtk.StringList()
    for v in variants:
        variant_model.append(v)
    self.x11_variant_dropdown.set_model(variant_model)
    self.x11_variant_dropdown.set_selected(_find_idx(variants, current_x11_variant))

    # Connect layout-change signal after pre-selection so it doesn't clobber variant
    def _on_layout_changed(dropdown, _param):
        layout_obj = dropdown.get_selected_item()
        if layout_obj is None:
            return
        new_variants = locale.get_x11_variants(layout_obj.get_string())
        new_model = Gtk.StringList()
        for v in new_variants:
            new_model.append(v)
        self.x11_variant_dropdown.set_model(new_model)
        self.x11_variant_dropdown.set_selected(0)

    self.x11_layout_dropdown.connect("notify::selected", _on_layout_changed)

    # ── Section: Timezone ─────────────────────────────────
    hbox_tz_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_tz_header = Gtk.Label(xalign=0)
    lbl_tz_header.set_markup("<b>Timezone</b>")
    lbl_tz_header.set_margin_start(10)
    lbl_tz_header.set_margin_top(15)
    lbl_tz_header.set_margin_bottom(5)
    hbox_tz_header.append(lbl_tz_header)

    hbox_tz_ctrl = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.timezone_dropdown = Gtk.DropDown.new_from_strings(timezones)
    self.timezone_dropdown.set_size_request(300, -1)
    self.timezone_dropdown.set_margin_start(10)
    self.timezone_dropdown.set_selected(_find_idx(timezones, current_tz))
    btn_tz_apply = Gtk.Button(label="Apply")
    btn_tz_apply.set_margin_start(10)
    btn_tz_apply.connect("clicked", functools.partial(locale.on_apply_timezone, self))
    hbox_tz_ctrl.append(self.timezone_dropdown)
    hbox_tz_ctrl.append(btn_tz_apply)

    # ── Assemble page ──────────────────────────────────────
    vboxstack_locale.append(hbox_title)
    vboxstack_locale.append(hbox_sep)
    vboxstack_locale.append(hbox_status_header)
    vboxstack_locale.append(hbox_locale_status)
    vboxstack_locale.append(hbox_keymap_status)
    vboxstack_locale.append(hbox_x11_status)
    vboxstack_locale.append(hbox_tz_status)
    vboxstack_locale.append(hbox_locale_header)
    vboxstack_locale.append(hbox_locale_ctrl)
    vboxstack_locale.append(hbox_gen_locale_header)
    vboxstack_locale.append(hbox_gen_locale_load)
    vboxstack_locale.append(hbox_gen_locale_apply)
    vboxstack_locale.append(hbox_keymap_header)
    vboxstack_locale.append(hbox_keymap_ctrl)
    vboxstack_locale.append(hbox_x11_header)
    vboxstack_locale.append(hbox_x11_layout_ctrl)
    vboxstack_locale.append(hbox_x11_variant_ctrl)
    vboxstack_locale.append(hbox_x11_apply_ctrl)
    vboxstack_locale.append(hbox_tz_header)
    vboxstack_locale.append(hbox_tz_ctrl)

    locale.refresh_status(self)
