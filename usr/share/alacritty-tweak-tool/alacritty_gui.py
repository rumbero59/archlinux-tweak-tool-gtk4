"""GTK4 GUI for alacritty-tweak-tool — three-tab Notebook interface."""
import json
import os
import shutil
import subprocess
import threading
from datetime import date

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gdk, GLib, Gtk, Pango, Vte

import alacritty_config as cfg
import alacritty_themes as themes
import log

_vte_themes = None
_vte_appearance = None
_vte_creator = None


# ── Helpers ────────────────────────────────────────────────────────────────────

def _label(text, css_class=None, markup=False):
    """Create a Gtk.Label with optional CSS class or markup."""
    lbl = Gtk.Label()
    if markup:
        lbl.set_markup(text)
    else:
        lbl.set_label(text)
    lbl.set_xalign(0.0)
    if css_class:
        lbl.add_css_class(css_class)
    return lbl


def _separator():
    return Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)


def _make_swatch_area(rgb_rows, width, height):
    """Return a DrawingArea showing rows of colored rectangles from rgb_rows list-of-lists."""
    area = Gtk.DrawingArea()
    area.set_size_request(width, height)

    def draw(a, cr, w, h, data):
        rows = data
        if not rows:
            return
        n_rows = len(rows)
        row_h = h / n_rows
        for ri, row_colors in enumerate(rows):
            n = len(row_colors)
            if n == 0:
                continue
            sw = w / n
            for ci, (r, g, b) in enumerate(row_colors):
                cr.set_source_rgb(r, g, b)
                cr.rectangle(ci * sw, ri * row_h, sw, row_h)
                cr.fill()

    area.set_draw_func(draw, rgb_rows)
    return area


def _get_fonts(mono_only=False):
    """Return a sorted deduplicated list of font family names via fc-list."""
    try:
        if mono_only:
            result = subprocess.run(
                ["fc-list", ":spacing=100", "family"],
                capture_output=True, text=True, timeout=5,
            )
        else:
            result = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=5)
        fonts = set()
        for line in result.stdout.splitlines():
            family = line.split(",")[0].strip()
            if family:
                fonts.add(family)
        return sorted(fonts) or ["monospace"]
    except Exception:
        return ["monospace"]


def _hex_to_rgba(hex_str):
    """Convert '0xrrggbb' or '#rrggbb' color string to a Gdk.RGBA."""
    s = hex_str.strip()
    if s.startswith(("0x", "0X")):
        s = "#" + s[2:]
    elif not s.startswith("#"):
        s = "#" + s
    rgba = Gdk.RGBA()
    if not rgba.parse(s):
        rgba.parse("#808080")
    return rgba


def _apply_vte_colors(vte, colors):
    """Apply a theme colors dict to a Vte.Terminal, updating palette live."""
    primary = colors.get("primary", {})
    fg = _hex_to_rgba(str(primary.get("foreground", "#aaaaaa")))
    bg = _hex_to_rgba(str(primary.get("background", "#000000")))
    order = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    palette = []
    for section in ("normal", "bright"):
        sec_data = colors.get(section, {})
        for name in order:
            palette.append(_hex_to_rgba(str(sec_data.get(name, "#808080"))))
    vte.set_colors(fg, bg, palette)


def _spawn_in_vte(vte):
    """Spawn fastfetch (then a shell) inside the given Vte.Terminal."""
    if shutil.which("fastfetch"):
        argv = ["bash", "-c", "fastfetch; exec bash"]
    else:
        argv = ["bash"]
    vte.set_input_enabled(False)
    vte.spawn_async(
        Vte.PtyFlags.DEFAULT, None, argv, None,
        GLib.SpawnFlags.SEARCH_PATH,
        None, None, -1, None, None, None,
    )


# ── Build entry point ──────────────────────────────────────────────────────────

def build(window, version="1.0.0"):
    """Build and attach the full GUI to the given Gtk.ApplicationWindow."""
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    root.set_margin_top(12)
    root.set_margin_bottom(12)
    root.set_margin_start(12)
    root.set_margin_end(12)

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    hbox_title.set_margin_bottom(8)

    title = _label("Alacritty Tweak Tool")
    title.set_name("title")
    title.set_hexpand(True)

    lbl_version = _label(f"v{version}", css_class="info-label")
    lbl_version.set_valign(Gtk.Align.CENTER)

    btn_quit = Gtk.Button(label="Quit")
    btn_quit.connect("clicked", lambda _w: window.get_application().quit())

    hbox_title.append(title)
    hbox_title.append(lbl_version)
    hbox_title.append(btn_quit)
    root.append(hbox_title)
    root.append(_separator())

    notebook = Gtk.Notebook()
    notebook.set_margin_top(10)
    notebook.set_vexpand(True)

    notebook.append_page(_build_themes_tab(window), Gtk.Label(label="  Themes  "))
    notebook.append_page(_build_appearance_tab(window), Gtk.Label(label="  Appearance  "))
    notebook.append_page(_build_advanced_tab(window), Gtk.Label(label="  Advanced  "))
    notebook.append_page(_build_behavior_tab(window), Gtk.Label(label="  Behavior  "))
    notebook.append_page(_build_creator_tab(window, notebook), Gtk.Label(label="  Creator  "))
    if log.DEV:
        notebook.append_page(_build_dev_tab(), Gtk.Label(label="  Dev  "))

    root.append(notebook)
    window.set_child(root)

    threading.Thread(target=_load_themes_async, args=(window,), daemon=True).start()


# ── Tab 1: Themes ──────────────────────────────────────────────────────────────

def _build_themes_tab(window):
    """Return the Themes tab with source dropdown, search bar, ListBox, and action buttons."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    outer.set_margin_top(10)
    outer.set_margin_bottom(6)
    outer.set_margin_start(6)
    outer.set_margin_end(6)

    info_lbl = _label(
        "Applying a theme overwrites colors currently managed by ohmychadwm-menu. "
        "A backup is saved to alacritty.toml-bak before every write.",
        css_class="info-label"
    )
    info_lbl.set_wrap(True)
    info_lbl.set_margin_bottom(4)
    outer.append(info_lbl)

    # ── Source dropdown + search bar ──────────────────────────────────────────
    controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    controls_box.set_margin_bottom(4)

    source_drop = Gtk.DropDown.new(Gtk.StringList.new(["Loading…"]), None)
    source_drop.set_size_request(220, -1)

    search_entry = Gtk.SearchEntry()
    search_entry.set_placeholder_text("Filter by name…")
    search_entry.set_hexpand(True)

    tone_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    tone_box.add_css_class("linked")
    btn_tone_all = Gtk.ToggleButton(label="All")
    btn_tone_all.set_active(True)
    btn_tone_dark = Gtk.ToggleButton(label="Dark")
    btn_tone_dark.set_group(btn_tone_all)
    btn_tone_light = Gtk.ToggleButton(label="Light")
    btn_tone_light.set_group(btn_tone_all)
    tone_box.append(btn_tone_all)
    tone_box.append(btn_tone_dark)
    tone_box.append(btn_tone_light)

    controls_box.append(source_drop)
    controls_box.append(search_entry)
    controls_box.append(tone_box)
    outer.append(controls_box)

    # ── Shared filter state ───────────────────────────────────────────────────
    # Mutable containers so closures can update them after async load.
    current_source = [""]
    search_text = [""]
    tone_filter = ["all"]   # "all" | "dark" | "light"
    source_labels = []

    # ── Split: theme list (left, fixed) | detail panel (right) ───────────────
    paned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    paned.set_vexpand(True)

    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll.set_size_request(360, -1)
    scroll.set_hexpand(False)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    listbox.add_css_class("theme-list")
    scroll.set_child(listbox)
    paned.append(scroll)
    paned.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

    # ── Filter function ───────────────────────────────────────────────────────
    def filter_row(row):
        if not hasattr(row, "source_label"):
            return False
        q = search_text[0].lower()
        # Current-colors row bypasses source and tone filters but still matches search.
        if getattr(row, "is_current", False):
            return not q or q in row.theme_name.lower()
        if current_source[0] and row.source_label != current_source[0]:
            return False
        if q and q not in row.theme_name.lower():
            return False
        tf = tone_filter[0]
        if tf != "all" and hasattr(row, "is_dark"):
            if tf == "dark" and not row.is_dark:
                return False
            if tf == "light" and row.is_dark:
                return False
        return True

    listbox.set_filter_func(filter_row)

    def _save_prefs():
        prefs = cfg.load_prefs()
        prefs.update({
            "source": current_source[0],
            "search": search_text[0],
            "tone": tone_filter[0],
        })
        cfg.save_prefs(prefs)

    def on_source_changed(_drop, _param):
        idx = source_drop.get_selected()
        if idx < len(source_labels):
            current_source[0] = source_labels[idx]
            listbox.invalidate_filter()
            _save_prefs()

    def on_search_changed(entry):
        search_text[0] = entry.get_text()
        listbox.invalidate_filter()
        _save_prefs()

    def on_tone_toggled(_btn, _param):
        if btn_tone_all.get_active():
            tone_filter[0] = "all"
        elif btn_tone_dark.get_active():
            tone_filter[0] = "dark"
        else:
            tone_filter[0] = "light"
        listbox.invalidate_filter()
        _save_prefs()

    source_drop.connect("notify::selected", on_source_changed)
    search_entry.connect("search-changed", on_search_changed)
    btn_tone_all.connect("notify::active", on_tone_toggled)
    btn_tone_dark.connect("notify::active", on_tone_toggled)
    btn_tone_light.connect("notify::active", on_tone_toggled)

    # ── Detail panel: VTE terminal (right) ───────────────────────────────────
    detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    detail_box.set_margin_start(12)

    detail_name_lbl = _label("")
    detail_name_lbl.set_markup("<b>Select a theme from the list</b>")
    detail_name_lbl.set_margin_top(8)
    detail_name_lbl.set_margin_bottom(6)
    detail_box.append(detail_name_lbl)

    global _vte_themes
    vte_terminal = Vte.Terminal()
    vte_terminal.set_vexpand(True)
    vte_terminal.set_hexpand(True)
    _vte_themes = vte_terminal
    detail_box.append(vte_terminal)

    btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row.set_margin_top(8)
    btn_row.set_margin_bottom(4)
    btn_apply = Gtk.Button(label="Apply Theme")
    btn_apply.add_css_class("suggested-action")
    btn_apply.set_sensitive(False)
    btn_undo = Gtk.Button(label="Undo Last Apply")
    btn_delete = Gtk.Button(label="Delete Theme")
    btn_delete.add_css_class("destructive-action")
    btn_delete.set_sensitive(False)
    btn_delete.set_tooltip_text("Only available for My Themes")
    btn_row.append(btn_apply)
    btn_row.append(btn_undo)
    btn_row.append(btn_delete)
    detail_box.append(btn_row)

    export_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    export_box.set_margin_bottom(4)
    export_entry = Gtk.Entry()
    export_entry.set_placeholder_text("Save selection as…")
    export_entry.set_hexpand(True)
    btn_export = Gtk.Button(label="Export")
    btn_export.set_sensitive(False)
    export_box.append(export_entry)
    export_box.append(btn_export)
    detail_box.append(export_box)

    status_lbl = _label("")
    detail_box.append(status_lbl)

    detail_box.set_hexpand(True)
    paned.append(detail_box)
    outer.append(paned)

    # Spawn fastfetch once when VTE is first shown; subsequent theme selections
    # only update the color palette — VTE re-renders existing text with new colors.
    vte_terminal.connect("realize", lambda _w: _spawn_in_vte(vte_terminal))

    # ── Selection callback ────────────────────────────────────────────────────
    selected_colors = [None]
    selected_name = [None]
    selected_source = [None]

    def _update_export_btn():
        btn_export.set_sensitive(selected_colors[0] is not None and bool(export_entry.get_text().strip()))

    def _user_theme_path(name):
        return os.path.join(themes.USER_THEMES_BASE, "user", f"{name}.toml")

    def on_row_selected(_listbox, row):
        if row is None:
            btn_apply.set_sensitive(False)
            btn_delete.set_sensitive(False)
            detail_name_lbl.set_markup("<b>Select a theme from the list</b>")
            _update_export_btn()
            return
        selected_colors[0] = row.theme_colors
        selected_name[0] = row.theme_name
        selected_source[0] = row.source_label
        detail_name_lbl.set_markup(f"<b>{GLib.markup_escape_text(row.theme_name)}</b>")
        _apply_vte_colors(vte_terminal, row.theme_colors)
        if _vte_appearance is not None:
            _apply_vte_colors(_vte_appearance, row.theme_colors)
        btn_apply.set_sensitive(True)
        btn_delete.set_sensitive(
            row.source_label == "My Themes" and os.path.isfile(_user_theme_path(row.theme_name))
        )
        _update_export_btn()
        status_lbl.set_label("")

    listbox.connect("row-selected", on_row_selected)
    export_entry.connect("changed", lambda _e: _update_export_btn())

    def on_apply(_widget):
        if selected_colors[0] is None:
            return
        themes.apply_theme(selected_colors[0])
        name = selected_name[0] or ""
        prefs = cfg.load_prefs()
        prefs["last_theme"] = name
        prefs["last_source"] = selected_source[0] or ""
        cfg.save_prefs(prefs)
        log.log_success(f"Theme applied: {name}")
        if hasattr(window, "_current_theme_lbl") and window._current_theme_lbl:
            GLib.idle_add(window._current_theme_lbl.set_markup,
                          f"<b>Current theme</b>  {GLib.markup_escape_text(name)}")
        status_lbl.set_label("Theme applied. Restart Alacritty to see changes.")

    def on_undo(_widget):
        ok = cfg.restore_backup()
        status_lbl.set_label("Restored from backup." if ok else "No backup found.")

    def on_export(_widget):
        if selected_colors[0] is None:
            return
        name = export_entry.get_text().strip()
        if not name:
            return
        themes.export_theme(name, selected_colors[0])
        status_lbl.set_label(f"Saved '{name}' — reloading…")
        while (child := listbox.get_first_child()):
            listbox.remove(child)
        window._theme_loading_lbl.set_label("Reloading…")
        threading.Thread(target=_load_themes_async, args=(window,), daemon=True).start()

    def on_delete(_widget):
        name = selected_name[0]
        if not name:
            return
        path = _user_theme_path(name)
        if not os.path.isfile(path):
            status_lbl.set_label("File not found — already deleted?")
            return
        try:
            os.remove(path)
            log.log_success(f"Deleted theme: {name}")
            status_lbl.set_label(f"Deleted '{name}'")
        except Exception as e:
            log.log_error(f"Could not delete theme: {e}")
            status_lbl.set_label("Delete failed — check permissions.")
            return
        btn_delete.set_sensitive(False)
        while (child := listbox.get_first_child()):
            listbox.remove(child)
        window._theme_loading_lbl.set_label("Reloading…")
        threading.Thread(target=_load_themes_async, args=(window,), daemon=True).start()

    btn_apply.connect("clicked", on_apply)
    btn_undo.connect("clicked", on_undo)
    btn_export.connect("clicked", on_export)
    btn_delete.connect("clicked", on_delete)

    loading_lbl = _label("Loading themes…")
    hbox_loading = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_credits = _label("Themes by their respective authors & communities", css_class="dim-label")
    lbl_credits.set_hexpand(True)
    lbl_credits.set_xalign(1.0)
    hbox_loading.append(loading_lbl)
    hbox_loading.append(lbl_credits)
    outer.append(hbox_loading)

    # Store references for async population and pref restoration.
    window._theme_listbox = listbox
    window._source_drop = source_drop
    window._source_labels = source_labels
    window._current_source = current_source
    window._search_text = search_text
    window._search_entry = search_entry
    window._tone_filter = tone_filter
    window._tone_buttons = (btn_tone_all, btn_tone_dark, btn_tone_light)
    window._theme_loading_lbl = loading_lbl

    return outer


def _load_themes_async(window):
    """Load all theme sources in a background thread, then populate the ListBox."""
    log.debug_print("Loading themes in background thread...")
    by_source = themes.load_themes_by_source()
    GLib.idle_add(_populate_theme_list, window, by_source)


def _make_theme_row(theme_name, colors, source_label):
    """Build a standard ListBoxRow for a theme entry."""
    normal_rgb = themes.colors_to_rgb_list(colors, "normal")
    row = Gtk.ListBoxRow()
    row.theme_name = theme_name
    row.theme_colors = colors
    row.source_label = source_label
    row.is_dark = themes.theme_luminance(colors) < 0.25
    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    hbox.set_margin_top(4)
    hbox.set_margin_bottom(4)
    hbox.set_margin_start(6)
    hbox.set_margin_end(6)
    name_lbl = Gtk.Label(label=theme_name)
    name_lbl.set_xalign(0.0)
    name_lbl.set_hexpand(True)
    hbox.append(name_lbl)
    hbox.append(_make_swatch_area([normal_rgb], 80, 14))
    row.set_child(hbox)
    return row


def _populate_theme_list(window, by_source):
    """Called on the GTK main thread to populate the ListBox and update the source dropdown."""
    listbox = window._theme_listbox
    source_drop = window._source_drop
    source_labels = window._source_labels
    current_source = window._current_source
    search_text = window._search_text
    tone_filter = window._tone_filter
    btn_tone_all, btn_tone_dark, btn_tone_light = window._tone_buttons

    labels = list(by_source.keys())
    display_labels = [f"{lbl}  ·  {len(by_source[lbl])}" for lbl in labels]

    # Populate source_labels before updating model to avoid a stale read in on_source_changed.
    source_labels.clear()
    source_labels.extend(labels)

    prefs = cfg.load_prefs()
    saved_source = prefs.get("source", "")
    saved_search = prefs.get("search", "")
    saved_tone = prefs.get("tone", "all")

    if saved_source in labels:
        current_source[0] = saved_source
        source_drop.set_model(Gtk.StringList.new(display_labels))
        source_drop.set_selected(labels.index(saved_source))
    else:
        if labels:
            current_source[0] = labels[0]
        source_drop.set_model(Gtk.StringList.new(display_labels))
        source_drop.set_selected(0)

    if saved_search:
        search_text[0] = saved_search
        window._search_entry.set_text(saved_search)

    if saved_tone == "dark":
        tone_filter[0] = "dark"
        btn_tone_dark.set_active(True)
    elif saved_tone == "light":
        tone_filter[0] = "light"
        btn_tone_light.set_active(True)
    else:
        btn_tone_all.set_active(True)

    total = 0
    for label in labels:
        for theme_name, colors in by_source[label]:
            listbox.append(_make_theme_row(theme_name, colors, label))
            total += 1

    # Pinned current-colors row always at the top regardless of source filter.
    current_colors = cfg.get_current_colors()
    saved_theme = prefs.get("last_theme", "")
    if current_colors:
        cur_row = Gtk.ListBoxRow()
        cur_row.theme_name = "Current theme"
        cur_row.theme_colors = current_colors
        cur_row.source_label = ""
        cur_row.is_current = True
        cur_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        cur_hbox.set_margin_top(4)
        cur_hbox.set_margin_bottom(4)
        cur_hbox.set_margin_start(6)
        cur_hbox.set_margin_end(6)
        cur_name_lbl = Gtk.Label()
        markup = "<b>Current theme</b>"
        if saved_theme:
            markup += f"  {GLib.markup_escape_text(saved_theme)}"
        cur_name_lbl.set_markup(markup)
        cur_name_lbl.set_xalign(0.0)
        cur_name_lbl.set_hexpand(True)
        cur_normal_rgb = themes.colors_to_rgb_list(current_colors, "normal")
        cur_hbox.append(cur_name_lbl)
        cur_hbox.append(_make_swatch_area([cur_normal_rgb], 80, 14))
        cur_row.set_child(cur_hbox)
        listbox.insert(cur_row, 0)
        window._current_theme_lbl = cur_name_lbl

    listbox.invalidate_filter()
    window._theme_loading_lbl.set_label(f"{total} themes loaded")
    log.log_timing("themes populated")
    return GLib.SOURCE_REMOVE


# ── Tab 2: Appearance ──────────────────────────────────────────────────────────

def _build_appearance_tab(window):
    """Return the Appearance tab with font and opacity controls."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
    outer.set_vexpand(True)
    outer.set_margin_top(10)
    outer.set_margin_bottom(6)
    outer.set_margin_start(6)
    outer.set_margin_end(6)

    paned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    paned.set_vexpand(True)

    # ── Left: settings panel ──────────────────────────────────────────────────
    scroll_settings = Gtk.ScrolledWindow()
    scroll_settings.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_settings.set_size_request(360, -1)
    scroll_settings.set_hexpand(False)

    left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    left_box.set_margin_top(16)
    left_box.set_margin_bottom(12)
    left_box.set_margin_start(16)
    left_box.set_margin_end(16)
    scroll_settings.set_child(left_box)

    left_box.append(_label("<b>Font</b>", markup=True))
    left_box.append(_separator())

    grid = Gtk.Grid()
    grid.set_column_spacing(12)
    grid.set_row_spacing(10)
    grid.set_margin_top(8)

    current_family, current_size = cfg.get_current_font()

    all_fonts = [[]]
    mono_fonts = [[]]

    font_lbl = _label("Family")

    font_drop = Gtk.DropDown.new(Gtk.StringList.new(["Loading…"]), None)
    font_drop.set_hexpand(True)
    font_drop.set_enable_search(True)
    font_drop.set_expression(Gtk.PropertyExpression.new(Gtk.StringObject, None, "string"))
    font_drop.set_sensitive(False)

    grid.attach(font_lbl, 0, 0, 1, 1)
    grid.attach(font_drop, 1, 0, 1, 1)

    mono_lbl = _label("Monospace only")
    mono_switch = Gtk.Switch()
    mono_switch.set_active(True)
    mono_switch.set_halign(Gtk.Align.START)
    mono_switch.set_sensitive(False)

    def _reload_drop(fonts):
        font_drop.set_model(Gtk.StringList.new(fonts))
        if current_family in fonts:
            font_drop.set_selected(fonts.index(current_family))

    def on_mono_toggled(_switch, _param):
        fonts = mono_fonts[0] if mono_switch.get_active() else all_fonts[0]
        _reload_drop(fonts)

    mono_switch.connect("notify::active", on_mono_toggled)

    grid.attach(mono_lbl, 0, 1, 1, 1)
    grid.attach(mono_switch, 1, 1, 1, 1)

    # ── Font size ─────────────────────────────────────────────────────────────
    size_lbl = _label("Size")
    size_spin = Gtk.SpinButton.new_with_range(6.0, 32.0, 0.5)
    size_spin.set_value(current_size)
    size_spin.set_digits(1)

    grid.attach(size_lbl, 0, 2, 1, 1)
    grid.attach(size_spin, 1, 2, 1, 1)

    left_box.append(grid)
    left_box.append(_label("<b>Window</b>", markup=True))
    left_box.append(_separator())

    window_grid = Gtk.Grid()
    window_grid.set_column_spacing(12)
    window_grid.set_row_spacing(10)
    window_grid.set_margin_top(8)

    current_opacity = cfg.get_current_opacity()
    current_decorations, current_dynamic_title, current_startup_mode, current_blur = cfg.get_current_window_style()

    opacity_lbl = _label("Opacity")
    opacity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.1, 1.0, 0.05)
    opacity_scale.set_value(current_opacity)
    opacity_scale.set_draw_value(True)
    opacity_scale.set_digits(2)
    opacity_scale.set_hexpand(True)
    opacity_scale.set_size_request(250, -1)

    decorations_list = ["Full", "None", "Transparent", "Buttonless"]
    decorations_lbl = _label("Decorations")
    decorations_drop = Gtk.DropDown.new(Gtk.StringList.new(decorations_list), None)
    if current_decorations in decorations_list:
        decorations_drop.set_selected(decorations_list.index(current_decorations))

    startup_list = ["Windowed", "Maximized", "Fullscreen", "SimpleFullscreen"]
    startup_lbl = _label("Startup mode")
    startup_drop = Gtk.DropDown.new(Gtk.StringList.new(startup_list), None)
    if current_startup_mode in startup_list:
        startup_drop.set_selected(startup_list.index(current_startup_mode))

    dynamic_title_lbl = _label("Dynamic title")
    dynamic_title_switch = Gtk.Switch()
    dynamic_title_switch.set_active(current_dynamic_title)
    dynamic_title_switch.set_halign(Gtk.Align.START)

    blur_lbl = _label("Background blur")
    blur_switch = Gtk.Switch()
    blur_switch.set_active(current_blur)
    blur_switch.set_halign(Gtk.Align.START)

    opacity_hint = _label("Apply and relaunch Alacritty to see the effect")
    opacity_hint.add_css_class("dim-label")
    opacity_hint.set_halign(Gtk.Align.START)

    window_grid.attach(opacity_lbl, 0, 0, 1, 1)
    window_grid.attach(opacity_scale, 1, 0, 1, 1)
    window_grid.attach(opacity_hint, 1, 1, 1, 1)
    window_grid.attach(decorations_lbl, 0, 2, 1, 1)
    window_grid.attach(decorations_drop, 1, 2, 1, 1)
    window_grid.attach(startup_lbl, 0, 3, 1, 1)
    window_grid.attach(startup_drop, 1, 3, 1, 1)
    window_grid.attach(dynamic_title_lbl, 0, 4, 1, 1)
    window_grid.attach(dynamic_title_switch, 1, 4, 1, 1)
    window_grid.attach(blur_lbl, 0, 5, 1, 1)
    window_grid.attach(blur_switch, 1, 5, 1, 1)

    left_box.append(window_grid)

    btn_apply = Gtk.Button(label="Apply Appearance")
    btn_apply.add_css_class("suggested-action")

    btn_reset_appearance = Gtk.Button(label="Reset to defaults")
    btn_reset_appearance.add_css_class("flat")

    btn_row_appearance = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_appearance.set_margin_top(12)
    btn_row_appearance.append(btn_apply)
    btn_row_appearance.append(btn_reset_appearance)
    left_box.append(btn_row_appearance)

    paned.append(scroll_settings)
    paned.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

    # ── Right: VTE preview panel ──────────────────────────────────────────────
    detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    detail_box.set_margin_start(12)

    preview_lbl = _label("")
    preview_lbl.set_markup("<b>Font Preview</b>")
    preview_lbl.set_margin_top(8)
    preview_lbl.set_margin_bottom(6)
    detail_box.append(preview_lbl)

    global _vte_appearance
    vte_preview = Vte.Terminal()
    vte_preview.set_vexpand(True)
    vte_preview.set_hexpand(True)
    vte_preview.set_font(Pango.FontDescription.from_string(f"{current_family} {current_size:.1f}"))
    vte_preview.connect("realize", lambda _w: _spawn_in_vte(vte_preview))
    _vte_appearance = vte_preview
    detail_box.append(vte_preview)

    detail_box.set_hexpand(True)
    paned.append(detail_box)
    outer.append(paned)

    def _update_vte_font(*_):
        idx = font_drop.get_selected()
        model = font_drop.get_model()
        family = model.get_string(idx) if model and idx < model.get_n_items() else current_family
        font_desc = Pango.FontDescription.from_string(f"{family} {size_spin.get_value():.1f}")
        vte_preview.set_font(font_desc)
        if _vte_themes is not None:
            _vte_themes.set_font(font_desc)

    font_drop.connect("notify::selected", _update_vte_font)
    size_spin.connect("value-changed", _update_vte_font)

    def on_apply_appearance(_widget):
        idx = font_drop.get_selected()
        model = font_drop.get_model()
        family = model.get_string(idx) if model and idx < model.get_n_items() else "monospace"
        size = size_spin.get_value()
        opacity = opacity_scale.get_value()
        cfg.apply_appearance(family, size, opacity)
        dec_idx = decorations_drop.get_selected()
        dec = decorations_list[dec_idx] if dec_idx < len(decorations_list) else "Full"
        sm_idx = startup_drop.get_selected()
        sm = startup_list[sm_idx] if sm_idx < len(startup_list) else "Windowed"
        cfg.apply_window_style(dec, dynamic_title_switch.get_active(), sm, blur_switch.get_active())
        vte_preview.set_font(Pango.FontDescription.from_string(f"{family} {size:.1f}"))

    def on_reset_appearance(_widget):
        active_fonts = mono_fonts[0] if mono_switch.get_active() else all_fonts[0]
        default_family = cfg.DEFAULTS["font_family"]
        if default_family in active_fonts:
            font_drop.set_selected(active_fonts.index(default_family))
        size_spin.set_value(cfg.DEFAULTS["font_size"])
        opacity_scale.set_value(cfg.DEFAULTS["opacity"])
        decorations_drop.set_selected(decorations_list.index(cfg.DEFAULTS["decorations"]))
        startup_drop.set_selected(startup_list.index(cfg.DEFAULTS["startup_mode"]))
        dynamic_title_switch.set_active(cfg.DEFAULTS["dynamic_title"])
        blur_switch.set_active(cfg.DEFAULTS["blur"])
        log.log_info("Appearance reset to defaults")

    btn_apply.connect("clicked", on_apply_appearance)
    btn_reset_appearance.connect("clicked", on_reset_appearance)

    def _load_fonts():
        log.debug_print("Loading fonts in background thread...")
        loaded_all = _get_fonts(mono_only=False)
        loaded_mono = _get_fonts(mono_only=True)
        GLib.idle_add(_populate_fonts, loaded_all, loaded_mono)

    def _populate_fonts(loaded_all, loaded_mono):
        all_fonts[0] = loaded_all
        mono_fonts[0] = loaded_mono
        _reload_drop(loaded_mono if mono_switch.get_active() else loaded_all)
        font_drop.set_sensitive(True)
        mono_switch.set_sensitive(True)
        log.log_timing("fonts ready")
        return GLib.SOURCE_REMOVE

    threading.Thread(target=_load_fonts, daemon=True).start()

    return outer


# ── Tab 3: Advanced ────────────────────────────────────────────────────────────

def _build_advanced_tab(window):
    """Return the Advanced tab with scrolling, padding, cursor, and font spacing controls."""
    scroll_win = Gtk.ScrolledWindow()
    scroll_win.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll_win.set_vexpand(True)

    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    outer.set_margin_top(16)
    outer.set_margin_bottom(12)
    outer.set_margin_start(16)
    outer.set_margin_end(16)
    scroll_win.set_child(outer)

    # ── Scrolling ─────────────────────────────────────────────────────────────
    outer.append(_label("<b>Scrolling</b>", markup=True))
    outer.append(_separator())

    scrolling_grid = Gtk.Grid()
    scrolling_grid.set_column_spacing(12)
    scrolling_grid.set_row_spacing(10)
    scrolling_grid.set_margin_top(8)

    current_scrollback = cfg.get_current_scrollback()
    current_multiplier = cfg.get_current_scroll_multiplier()

    scroll_lbl = _label("History (lines)")
    # Alacritty has no true unlimited scrollback; 0 disables it entirely.
    # High values work but consume RAM proportionally.
    scroll_spin = Gtk.SpinButton.new_with_range(0, 999999, 1000)
    scroll_spin.set_value(current_scrollback)
    scroll_note = _label("Max ~1 million lines. There is no true unlimited.", css_class="info-label")

    multiplier_lbl = _label("Scroll speed (multiplier)")
    multiplier_spin = Gtk.SpinButton.new_with_range(1, 10, 1)
    multiplier_spin.set_value(current_multiplier)

    scrolling_grid.attach(scroll_lbl, 0, 0, 1, 1)
    scrolling_grid.attach(scroll_spin, 1, 0, 1, 1)
    scrolling_grid.attach(scroll_note, 1, 1, 1, 1)
    scrolling_grid.attach(multiplier_lbl, 0, 2, 1, 1)
    scrolling_grid.attach(multiplier_spin, 1, 2, 1, 1)
    outer.append(scrolling_grid)

    btn_apply_scrolling = Gtk.Button(label="Apply Scrolling")
    btn_apply_scrolling.add_css_class("suggested-action")
    status_scrolling = _label("")

    def on_apply_scrolling(_widget):
        cfg.apply_scrolling(int(scroll_spin.get_value()), int(multiplier_spin.get_value()))
        status_scrolling.set_label("Scrolling applied. Restart Alacritty to see changes.")

    btn_reset_scrolling = Gtk.Button(label="Reset to defaults")
    btn_reset_scrolling.add_css_class("flat")

    def on_reset_scrolling(_widget):
        scroll_spin.set_value(cfg.DEFAULTS["scroll_history"])
        multiplier_spin.set_value(cfg.DEFAULTS["scroll_multiplier"])
        log.log_info("Scrolling reset to defaults")

    btn_apply_scrolling.connect("clicked", on_apply_scrolling)
    btn_reset_scrolling.connect("clicked", on_reset_scrolling)

    btn_row_scrolling = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_scrolling.set_margin_top(8)
    btn_row_scrolling.append(btn_apply_scrolling)
    btn_row_scrolling.append(btn_reset_scrolling)
    outer.append(btn_row_scrolling)
    outer.append(status_scrolling)

    # ── Window Padding ────────────────────────────────────────────────────────
    outer.append(_label("<b>Window Padding</b>", markup=True))
    outer.append(_separator())

    padding_grid = Gtk.Grid()
    padding_grid.set_column_spacing(12)
    padding_grid.set_row_spacing(10)
    padding_grid.set_margin_top(8)

    current_pad_x, current_pad_y = cfg.get_current_padding()

    pad_x_lbl = _label("Horizontal (px)")
    pad_x_spin = Gtk.SpinButton.new_with_range(0, 50, 1)
    pad_x_spin.set_value(current_pad_x)

    pad_y_lbl = _label("Vertical (px)")
    pad_y_spin = Gtk.SpinButton.new_with_range(0, 50, 1)
    pad_y_spin.set_value(current_pad_y)

    padding_grid.attach(pad_x_lbl, 0, 0, 1, 1)
    padding_grid.attach(pad_x_spin, 1, 0, 1, 1)
    padding_grid.attach(pad_y_lbl, 0, 1, 1, 1)
    padding_grid.attach(pad_y_spin, 1, 1, 1, 1)
    outer.append(padding_grid)

    btn_apply_padding = Gtk.Button(label="Apply Padding")
    btn_apply_padding.add_css_class("suggested-action")
    status_padding = _label("")

    def on_apply_padding(_widget):
        cfg.apply_window_padding(int(pad_x_spin.get_value()), int(pad_y_spin.get_value()))
        status_padding.set_label("Padding applied. Restart Alacritty to see changes.")

    btn_reset_padding = Gtk.Button(label="Reset to defaults")
    btn_reset_padding.add_css_class("flat")

    def on_reset_padding(_widget):
        pad_x_spin.set_value(cfg.DEFAULTS["pad_x"])
        pad_y_spin.set_value(cfg.DEFAULTS["pad_y"])
        log.log_info("Window padding reset to defaults")

    btn_apply_padding.connect("clicked", on_apply_padding)
    btn_reset_padding.connect("clicked", on_reset_padding)

    btn_row_padding = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_padding.set_margin_top(8)
    btn_row_padding.append(btn_apply_padding)
    btn_row_padding.append(btn_reset_padding)
    outer.append(btn_row_padding)
    outer.append(status_padding)

    # ── Cursor ────────────────────────────────────────────────────────────────
    outer.append(_label("<b>Cursor</b>", markup=True))
    outer.append(_separator())

    cursor_grid = Gtk.Grid()
    cursor_grid.set_column_spacing(12)
    cursor_grid.set_row_spacing(10)
    cursor_grid.set_margin_top(8)

    current_shape, current_blink = cfg.get_current_cursor()
    current_thickness, current_blink_timeout, current_hollow = cfg.get_current_cursor_extras()
    shapes = ["Block", "Beam", "Underline"]

    shape_lbl = _label("Shape")
    shape_drop = Gtk.DropDown.new(Gtk.StringList.new(shapes), None)
    if current_shape in shapes:
        shape_drop.set_selected(shapes.index(current_shape))

    blink_lbl = _label("Blink")
    blink_switch = Gtk.Switch()
    blink_switch.set_active(current_blink)
    blink_switch.set_halign(Gtk.Align.START)

    thickness_lbl = _label("Thickness")
    thickness_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.0, 1.0, 0.05)
    thickness_scale.set_value(current_thickness)
    thickness_scale.set_draw_value(True)
    thickness_scale.set_digits(2)
    thickness_scale.set_hexpand(True)
    thickness_scale.set_size_request(200, -1)

    blink_timeout_lbl = _label("Blink timeout (s, 0 = never stop)")
    blink_timeout_spin = Gtk.SpinButton.new_with_range(0, 30, 1)
    blink_timeout_spin.set_value(current_blink_timeout)

    hollow_lbl = _label("Hollow when unfocused")
    hollow_switch = Gtk.Switch()
    hollow_switch.set_active(current_hollow)
    hollow_switch.set_halign(Gtk.Align.START)

    cursor_grid.attach(shape_lbl, 0, 0, 1, 1)
    cursor_grid.attach(shape_drop, 1, 0, 1, 1)
    cursor_grid.attach(blink_lbl, 0, 1, 1, 1)
    cursor_grid.attach(blink_switch, 1, 1, 1, 1)
    cursor_grid.attach(thickness_lbl, 0, 2, 1, 1)
    cursor_grid.attach(thickness_scale, 1, 2, 1, 1)
    cursor_grid.attach(blink_timeout_lbl, 0, 3, 1, 1)
    cursor_grid.attach(blink_timeout_spin, 1, 3, 1, 1)
    cursor_grid.attach(hollow_lbl, 0, 4, 1, 1)
    cursor_grid.attach(hollow_switch, 1, 4, 1, 1)
    outer.append(cursor_grid)

    btn_apply_cursor = Gtk.Button(label="Apply Cursor")
    btn_apply_cursor.add_css_class("suggested-action")
    status_cursor = _label("")

    def on_apply_cursor(_widget):
        selected = shape_drop.get_selected()
        shape = shapes[selected] if selected < len(shapes) else "Block"
        cfg.apply_cursor_full(
            shape, blink_switch.get_active(),
            thickness_scale.get_value(),
            int(blink_timeout_spin.get_value()),
            hollow_switch.get_active(),
        )
        status_cursor.set_label("Cursor applied. Restart Alacritty to see changes.")

    btn_reset_cursor = Gtk.Button(label="Reset to defaults")
    btn_reset_cursor.add_css_class("flat")

    def on_reset_cursor(_widget):
        default_shape = cfg.DEFAULTS["cursor_shape"]
        if default_shape in shapes:
            shape_drop.set_selected(shapes.index(default_shape))
        blink_switch.set_active(cfg.DEFAULTS["cursor_blink"])
        thickness_scale.set_value(cfg.DEFAULTS["cursor_thickness"])
        blink_timeout_spin.set_value(cfg.DEFAULTS["blink_timeout"])
        hollow_switch.set_active(cfg.DEFAULTS["unfocused_hollow"])
        log.log_info("Cursor reset to defaults")

    btn_apply_cursor.connect("clicked", on_apply_cursor)
    btn_reset_cursor.connect("clicked", on_reset_cursor)

    btn_row_cursor = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_cursor.set_margin_top(8)
    btn_row_cursor.append(btn_apply_cursor)
    btn_row_cursor.append(btn_reset_cursor)
    outer.append(btn_row_cursor)
    outer.append(status_cursor)

    # ── Font Spacing ──────────────────────────────────────────────────────────
    outer.append(_label("<b>Font Spacing</b>", markup=True))
    outer.append(_separator())

    font_offset_grid = Gtk.Grid()
    font_offset_grid.set_column_spacing(12)
    font_offset_grid.set_row_spacing(10)
    font_offset_grid.set_margin_top(8)

    current_off_x, current_off_y = cfg.get_current_font_offset()

    off_x_lbl = _label("Char spacing (offset.x)")
    off_x_spin = Gtk.SpinButton.new_with_range(-5, 10, 1)
    off_x_spin.set_value(current_off_x)

    off_y_lbl = _label("Line spacing (offset.y)")
    off_y_spin = Gtk.SpinButton.new_with_range(-5, 10, 1)
    off_y_spin.set_value(current_off_y)

    font_offset_grid.attach(off_x_lbl, 0, 0, 1, 1)
    font_offset_grid.attach(off_x_spin, 1, 0, 1, 1)
    font_offset_grid.attach(off_y_lbl, 0, 1, 1, 1)
    font_offset_grid.attach(off_y_spin, 1, 1, 1, 1)
    outer.append(font_offset_grid)

    btn_apply_font_offset = Gtk.Button(label="Apply Font Spacing")
    btn_apply_font_offset.add_css_class("suggested-action")
    status_font_offset = _label("")

    def on_apply_font_offset(_widget):
        cfg.apply_font_offset(int(off_x_spin.get_value()), int(off_y_spin.get_value()))
        status_font_offset.set_label("Font spacing applied. Restart Alacritty to see changes.")

    btn_reset_font_offset = Gtk.Button(label="Reset to defaults")
    btn_reset_font_offset.add_css_class("flat")

    def on_reset_font_offset(_widget):
        off_x_spin.set_value(cfg.DEFAULTS["font_offset_x"])
        off_y_spin.set_value(cfg.DEFAULTS["font_offset_y"])
        log.log_info("Font spacing reset to defaults")

    btn_apply_font_offset.connect("clicked", on_apply_font_offset)
    btn_reset_font_offset.connect("clicked", on_reset_font_offset)

    btn_row_font_offset = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_font_offset.set_margin_top(8)
    btn_row_font_offset.append(btn_apply_font_offset)
    btn_row_font_offset.append(btn_reset_font_offset)
    outer.append(btn_row_font_offset)
    outer.append(status_font_offset)

    return scroll_win


# ── Tab 4: Behavior ────────────────────────────────────────────────────────────

def _build_behavior_tab(window):
    """Return the Behavior tab with selection, mouse, and general behavior controls."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    outer.set_margin_top(16)
    outer.set_margin_bottom(12)
    outer.set_margin_start(16)
    outer.set_margin_end(16)

    current_save, current_hide, current_live = cfg.get_current_behavior()

    outer.append(_label("<b>Selection</b>", markup=True))
    outer.append(_separator())

    sel_grid = Gtk.Grid()
    sel_grid.set_column_spacing(12)
    sel_grid.set_row_spacing(10)
    sel_grid.set_margin_top(8)

    save_lbl = _label("Copy on select")
    save_switch = Gtk.Switch()
    save_switch.set_active(current_save)
    save_switch.set_halign(Gtk.Align.START)

    sel_grid.attach(save_lbl, 0, 0, 1, 1)
    sel_grid.attach(save_switch, 1, 0, 1, 1)
    outer.append(sel_grid)

    outer.append(_label("<b>Mouse</b>", markup=True))
    outer.append(_separator())

    mouse_grid = Gtk.Grid()
    mouse_grid.set_column_spacing(12)
    mouse_grid.set_row_spacing(10)
    mouse_grid.set_margin_top(8)

    hide_lbl = _label("Hide when typing")
    hide_switch = Gtk.Switch()
    hide_switch.set_active(current_hide)
    hide_switch.set_halign(Gtk.Align.START)

    mouse_grid.attach(hide_lbl, 0, 0, 1, 1)
    mouse_grid.attach(hide_switch, 1, 0, 1, 1)
    outer.append(mouse_grid)

    outer.append(_label("<b>General</b>", markup=True))
    outer.append(_separator())

    general_grid = Gtk.Grid()
    general_grid.set_column_spacing(12)
    general_grid.set_row_spacing(10)
    general_grid.set_margin_top(8)

    live_lbl = _label("Live config reload")
    live_switch = Gtk.Switch()
    live_switch.set_active(current_live)
    live_switch.set_halign(Gtk.Align.START)

    general_grid.attach(live_lbl, 0, 0, 1, 1)
    general_grid.attach(live_switch, 1, 0, 1, 1)
    outer.append(general_grid)

    btn_apply = Gtk.Button(label="Apply Behavior")
    btn_apply.add_css_class("suggested-action")
    status_lbl = _label("")

    def on_apply_behavior(_widget):
        cfg.apply_behavior(save_switch.get_active(), hide_switch.get_active(), live_switch.get_active())
        status_lbl.set_label("Behavior applied. Restart Alacritty to see changes.")

    btn_reset_behavior = Gtk.Button(label="Reset to defaults")
    btn_reset_behavior.add_css_class("flat")

    def on_reset_behavior(_widget):
        save_switch.set_active(cfg.DEFAULTS["save_to_clipboard"])
        hide_switch.set_active(cfg.DEFAULTS["hide_when_typing"])
        live_switch.set_active(cfg.DEFAULTS["live_config_reload"])
        log.log_info("Behavior reset to defaults")

    btn_apply.connect("clicked", on_apply_behavior)
    btn_reset_behavior.connect("clicked", on_reset_behavior)

    btn_row_behavior = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row_behavior.set_margin_top(12)
    btn_row_behavior.append(btn_apply)
    btn_row_behavior.append(btn_reset_behavior)
    outer.append(btn_row_behavior)
    outer.append(status_lbl)
    return outer


# ── Tab 5: Creator ─────────────────────────────────────────────────────────────

def _get_current_wallpaper():
    """Return (path, source_label) for the current wallpaper, or (None, None)."""
    import re
    variety_txt = os.path.expanduser("~/.config/variety/wallpaper/wallpaper.jpg.txt")
    if os.path.isfile(variety_txt):
        try:
            with open(variety_txt, "r", encoding="utf-8") as f:
                path = f.read().strip()
            if path and os.path.isfile(path):
                return path, "Variety"
        except Exception:
            pass
    fehbg = os.path.expanduser("~/.fehbg")
    if os.path.isfile(fehbg):
        try:
            with open(fehbg, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r"feh\s+.*?['\"]([^'\"]+\.(jpg|jpeg|png|webp|gif|bmp))['\"]", content, re.IGNORECASE)
            if match:
                return match.group(1), "feh"
        except Exception:
            pass
    return None, None


_CREATOR_DEFAULTS = {
    "primary": {"background": "#1e1e2e", "foreground": "#cdd6f4"},
    "cursor": {"text": "#1e1e2e", "cursor": "#f5e0dc"},
    "normal": {
        "black": "#45475a", "red": "#f38ba8", "green": "#a6e3a1",
        "yellow": "#f9e2af", "blue": "#89b4fa", "magenta": "#f5c2e7",
        "cyan": "#94e2d5", "white": "#bac2de",
    },
    "bright": {
        "black": "#585b70", "red": "#f38ba8", "green": "#a6e3a1",
        "yellow": "#f9e2af", "blue": "#89b4fa", "magenta": "#f5c2e7",
        "cyan": "#94e2d5", "white": "#a6adc8",
    },
}

_ANSI_NAMES = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")


def _rgba_to_hex(rgba):
    """Convert a Gdk.RGBA to a lowercase '#rrggbb' hex string."""
    r = int(round(rgba.red * 255))
    g = int(round(rgba.green * 255))
    b = int(round(rgba.blue * 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def _extract_colors_from_image(path):
    """Run ImageMagick to extract dominant colors from an image and map to ANSI slots.

    Returns a colors dict with primary/normal/bright/cursor sections, or None on error.
    """
    try:
        result = subprocess.run(
            ["convert", path, "+dither", "-colors", "16", "-unique-colors", "txt:-"],
            capture_output=True, text=True, timeout=15,
        )
        hexcolors = []
        for line in result.stdout.splitlines():
            for part in line.split():
                if part.startswith("#") and len(part) == 7:
                    hexcolors.append(part.lower())
                    break
        if not hexcolors:
            return None

        def _lin(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        def _lum(h):
            r, g, b = themes.hex_to_rgb(h)
            return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)

        def _hue(h):
            r, g, b = themes.hex_to_rgb(h)
            mx, mn = max(r, g, b), min(r, g, b)
            if mx == mn:
                return 0.0
            d = mx - mn
            if mx == r:
                hue = (g - b) / d % 6
            elif mx == g:
                hue = (b - r) / d + 2
            else:
                hue = (r - g) / d + 4
            return hue * 60

        def _closest_by_hue(candidates, target):
            def _dist(h):
                d = abs(_hue(h) - target)
                return min(d, 360 - d)
            return min(candidates, key=_dist)

        sorted_colors = sorted(set(hexcolors), key=_lum)
        mid = sorted_colors[1:-1] if len(sorted_colors) > 2 else sorted_colors

        hue_targets = {"red": 0, "yellow": 60, "green": 120, "cyan": 180, "blue": 240, "magenta": 300}
        ansi_normal, ansi_bright = {}, {}
        for name, target in hue_targets.items():
            color = _closest_by_hue(mid, target)
            ansi_normal[name] = color
            brighter = [c for c in mid if _lum(c) > _lum(color)]
            ansi_bright[name] = _closest_by_hue(brighter, target) if brighter else color

        ansi_normal["black"] = sorted_colors[0]
        ansi_normal["white"] = sorted_colors[-2] if len(sorted_colors) > 1 else sorted_colors[-1]
        ansi_bright["black"] = sorted_colors[1] if len(sorted_colors) > 1 else sorted_colors[0]
        ansi_bright["white"] = sorted_colors[-1]

        bg = sorted_colors[0]
        fg = sorted_colors[-1]
        return {
            "primary": {"background": bg, "foreground": fg},
            "cursor": {"text": bg, "cursor": fg},
            "normal": ansi_normal,
            "bright": ansi_bright,
        }
    except Exception as e:
        log.log_error(f"Color extraction failed: {e}")
        return None


def _build_creator_tab(window, notebook):
    """Return the Creator tab for building custom themes color-by-color."""
    global _vte_creator

    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    outer.set_margin_top(10)
    outer.set_margin_bottom(6)
    outer.set_margin_start(6)
    outer.set_margin_end(6)

    # ── Wallpaper row (only if ImageMagick is available) ──────────────────────
    wallpaper_path = [""]
    if shutil.which("convert"):
        wall_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        wall_box.set_margin_bottom(6)
        wall_box.append(_label("Wallpaper:"))
        wall_entry = Gtk.Entry()
        wall_entry.set_placeholder_text("Select an image to extract colors…")
        wall_entry.set_hexpand(True)
        btn_browse = Gtk.Button(label="Browse")
        btn_current = Gtk.Button(label="Current Wallpaper")
        btn_extract = Gtk.Button(label="Extract Colors")
        btn_extract.set_sensitive(False)
        lbl_wall_source = _label("", css_class="info-label")
        current_wp, current_src = _get_current_wallpaper()
        if current_wp is None:
            btn_current.set_sensitive(False)
            btn_current.set_tooltip_text("No current wallpaper found (Variety / ~/.fehbg)")
        else:
            lbl_wall_source.set_text(f"Detected via {current_src}")
        wall_box.append(wall_entry)
        wall_box.append(btn_browse)
        wall_box.append(btn_current)
        wall_box.append(btn_extract)
        wall_box.append(lbl_wall_source)
        outer.append(wall_box)
        outer.append(_separator())
    else:
        wall_entry = btn_browse = btn_extract = None

    # ── Split: left = editor (fixed), right = VTE preview ────────────────────
    paned = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
    paned.set_vexpand(True)

    left_scroll = Gtk.ScrolledWindow()
    left_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    left_scroll.set_size_request(360, -1)
    left_scroll.set_hexpand(False)

    editor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    editor.set_margin_top(10)
    editor.set_margin_bottom(10)
    editor.set_margin_start(10)
    editor.set_margin_end(10)

    # ── Color buttons dict: keys like "primary.background", "normal.red" ──────
    btns = {}

    def _make_btn(hex_color):
        btn = Gtk.ColorButton()
        btn.set_rgba(_hex_to_rgba(hex_color))
        btn.set_use_alpha(False)
        return btn

    # Primary
    editor.append(_label("<b>Primary</b>", markup=True))
    editor.append(_separator())
    primary_grid = Gtk.Grid()
    primary_grid.set_column_spacing(12)
    primary_grid.set_row_spacing(6)
    primary_grid.set_margin_top(4)
    for row, key in enumerate(("background", "foreground")):
        primary_grid.attach(_label(key.capitalize()), 0, row, 1, 1)
        btn = _make_btn(_CREATOR_DEFAULTS["primary"][key])
        btns[f"primary.{key}"] = btn
        primary_grid.attach(btn, 1, row, 1, 1)
    editor.append(primary_grid)

    # Cursor
    editor.append(_label("<b>Cursor</b>", markup=True))
    editor.append(_separator())
    cursor_grid = Gtk.Grid()
    cursor_grid.set_column_spacing(12)
    cursor_grid.set_row_spacing(6)
    cursor_grid.set_margin_top(4)
    for row, key in enumerate(("text", "cursor")):
        cursor_grid.attach(_label(key.capitalize()), 0, row, 1, 1)
        btn = _make_btn(_CREATOR_DEFAULTS["cursor"][key])
        btns[f"cursor.{key}"] = btn
        cursor_grid.attach(btn, 1, row, 1, 1)
    editor.append(cursor_grid)

    # Normal / Bright
    editor.append(_label("<b>Colors</b>", markup=True))
    editor.append(_separator())
    colors_grid = Gtk.Grid()
    colors_grid.set_column_spacing(12)
    colors_grid.set_row_spacing(6)
    colors_grid.set_margin_top(4)
    hdr_n = Gtk.Label()
    hdr_n.set_markup("<b>Normal</b>")
    hdr_b = Gtk.Label()
    hdr_b.set_markup("<b>Bright</b>")
    colors_grid.attach(hdr_n, 1, 0, 1, 1)
    colors_grid.attach(hdr_b, 2, 0, 1, 1)
    for row, name in enumerate(_ANSI_NAMES, start=1):
        colors_grid.attach(_label(name.capitalize()), 0, row, 1, 1)
        btn_n = _make_btn(_CREATOR_DEFAULTS["normal"][name])
        btn_b = _make_btn(_CREATOR_DEFAULTS["bright"][name])
        btns[f"normal.{name}"] = btn_n
        btns[f"bright.{name}"] = btn_b
        colors_grid.attach(btn_n, 1, row, 1, 1)
        colors_grid.attach(btn_b, 2, row, 1, 1)
    editor.append(colors_grid)

    # Save row
    editor.append(_separator())
    save_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    save_row.set_margin_top(4)
    name_entry = Gtk.Entry()
    name_entry.set_placeholder_text("Theme name…")
    name_entry.set_hexpand(True)
    btn_save = Gtk.Button(label="Save Theme")
    btn_save.add_css_class("suggested-action")
    status_lbl = _label("", css_class="info-label")
    save_row.append(name_entry)
    save_row.append(btn_save)
    editor.append(save_row)
    editor.append(status_lbl)

    left_scroll.set_child(editor)
    paned.append(left_scroll)
    paned.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))

    vte_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    vte_box.set_margin_start(12)
    vte_box.set_hexpand(True)

    vte_lbl = _label("")
    vte_lbl.set_markup("<b>Color Preview</b>")
    vte_lbl.set_margin_top(8)
    vte_lbl.set_margin_bottom(6)
    vte_box.append(vte_lbl)

    vte_terminal = Vte.Terminal()
    vte_terminal.set_hexpand(True)
    vte_terminal.set_vexpand(True)
    _vte_creator = vte_terminal
    vte_box.append(vte_terminal)
    paned.append(vte_box)

    outer.append(paned)

    # ── Build colors dict from current button values ───────────────────────────
    def _read_colors():
        return {
            "primary": {k: _rgba_to_hex(btns[f"primary.{k}"].get_rgba()) for k in ("background", "foreground")},
            "cursor": {k: _rgba_to_hex(btns[f"cursor.{k}"].get_rgba()) for k in ("text", "cursor")},
            "normal": {n: _rgba_to_hex(btns[f"normal.{n}"].get_rgba()) for n in _ANSI_NAMES},
            "bright": {n: _rgba_to_hex(btns[f"bright.{n}"].get_rgba()) for n in _ANSI_NAMES},
        }

    # Live VTE update on any color change
    def _on_color_changed(_btn):
        _apply_vte_colors(vte_terminal, _read_colors())

    for btn in btns.values():
        btn.connect("color-set", _on_color_changed)

    # VTE realize: spawn shell and apply initial palette
    def _on_vte_realize(_vte):
        _spawn_in_vte(vte_terminal)
        _apply_vte_colors(vte_terminal, _read_colors())

    vte_terminal.connect("realize", _on_vte_realize)

    # ── Wallpaper browse + extract ────────────────────────────────────────────
    if shutil.which("convert"):
        def _on_browse(_w):
            dialog = Gtk.FileChooserNative(
                title="Select wallpaper image",
                transient_for=window,
                action=Gtk.FileChooserAction.OPEN,
            )
            img_filter = Gtk.FileFilter()
            img_filter.set_name("Images")
            img_filter.add_mime_type("image/*")
            dialog.add_filter(img_filter)

            def _on_response(d, response):
                if response == Gtk.ResponseType.ACCEPT:
                    path = d.get_file().get_path()
                    wall_entry.set_text(path)
                    wallpaper_path[0] = path
                    btn_extract.set_sensitive(True)
                d.destroy()

            dialog.connect("response", _on_response)
            dialog.show()

        def _on_extract(_w):
            path = wallpaper_path[0] or wall_entry.get_text().strip()
            if not path:
                return
            btn_extract.set_sensitive(False)
            status_lbl.set_text("Extracting colors…")

            def _do_extract():
                colors = _extract_colors_from_image(path)

                def _apply_extracted():
                    btn_extract.set_sensitive(True)
                    if colors is None:
                        status_lbl.set_text("Could not extract colors — check file path.")
                        return
                    for section, keys in (("primary", ("background", "foreground")),
                                          ("cursor", ("text", "cursor"))):
                        for key in keys:
                            if key in colors.get(section, {}):
                                btns[f"{section}.{key}"].set_rgba(_hex_to_rgba(colors[section][key]))
                    for section in ("normal", "bright"):
                        for name in _ANSI_NAMES:
                            if name in colors.get(section, {}):
                                btns[f"{section}.{name}"].set_rgba(_hex_to_rgba(colors[section][name]))
                    _apply_vte_colors(vte_terminal, _read_colors())
                    status_lbl.set_text("Colors extracted — tweak and save.")
                    log.log_success("Wallpaper colors extracted")

                GLib.idle_add(_apply_extracted)

            threading.Thread(target=_do_extract, daemon=True).start()

        def _on_current(_w):
            path, source = _get_current_wallpaper()
            if path:
                wall_entry.set_text(path)
                wallpaper_path[0] = path
                btn_extract.set_sensitive(True)
                lbl_wall_source.set_text(f"via {source}")

        btn_browse.connect("clicked", _on_browse)
        btn_current.connect("clicked", _on_current)
        btn_extract.connect("clicked", _on_extract)

    # ── Save theme ────────────────────────────────────────────────────────────
    def _on_save(_w):
        name = name_entry.get_text().strip()
        if not name:
            status_lbl.set_text("Enter a theme name first.")
            return
        colors = _read_colors()
        themes.export_theme(name, colors)
        status_lbl.set_text("Saved — switching to Themes tab…")
        log.log_success(f"Theme created: {name}")
        prefs = cfg.load_prefs()
        prefs["last_source"] = "My Themes"
        cfg.save_prefs(prefs)
        threading.Thread(target=_load_themes_async, args=(window,), daemon=True).start()
        GLib.timeout_add(300, lambda: notebook.set_current_page(0) or False)

    btn_save.connect("clicked", _on_save)

    return outer


# ── Tab 6: Dev (--dev only) ────────────────────────────────────────────────────

def _build_dev_tab():
    """Return the Dev tab with theme source maintenance controls."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    outer.set_margin_top(16)
    outer.set_margin_bottom(16)
    outer.set_margin_start(16)
    outer.set_margin_end(16)

    lbl_title = _label("Developer Tools")
    lbl_title.set_name("title")
    outer.append(lbl_title)
    outer.append(_separator())

    lbl_section = Gtk.Label()
    lbl_section.set_markup("<b>Theme Sources</b>")
    lbl_section.set_halign(Gtk.Align.START)
    lbl_section.set_margin_top(12)
    lbl_section.set_margin_bottom(8)
    outer.append(lbl_section)

    grid = Gtk.Grid()
    grid.set_column_spacing(24)
    grid.set_row_spacing(8)

    for col, text in enumerate(("Source", "Themes", "Added", "Last Checked", "")):
        h = Gtk.Label()
        h.set_markup(f"<b>{text}</b>")
        h.set_halign(Gtk.Align.START)
        grid.attach(h, col, 0, 1, 1)

    themes_base = themes.THEMES_BASE_DIR
    row_idx = 1
    for entry in sorted(os.scandir(themes_base), key=lambda e: e.name):
        if not entry.is_dir():
            continue
        source_json_path = os.path.join(entry.path, "source.json")
        if not os.path.isfile(source_json_path):
            continue
        with open(source_json_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        update_cmd = meta.get("update_command") or ""
        lbl_last = _label(meta.get("last_checked") or "—")

        grid.attach(_label(meta.get("label", entry.name)), 0, row_idx, 1, 1)
        grid.attach(_label(str(meta.get("theme_count", "?"))), 1, row_idx, 1, 1)
        grid.attach(_label(meta.get("copied_date", "—")), 2, row_idx, 1, 1)
        grid.attach(lbl_last, 3, row_idx, 1, 1)

        btn = Gtk.Button(label="Update")
        if not update_cmd:
            btn.set_sensitive(False)
            btn.set_tooltip_text("Built-in source — edit manually")
        else:
            def _on_update(_w, path=source_json_path, cmd=update_cmd, lbl=lbl_last):
                log.log_subsection(f"Updating theme source: {path}")
                proc = subprocess.Popen(
                    ["alacritty", "-e", "bash", "-c",
                     f"{cmd}; echo; read -p 'Press Enter to close...'"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                def _wait(p=proc, src=path, lbl_ref=lbl):
                    p.wait()
                    today = date.today().isoformat()
                    try:
                        with open(src, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        data["last_checked"] = today
                        with open(src, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2)
                        log.log_success(f"last_checked updated: {today}")
                    except Exception as e:
                        log.log_error(f"Could not update last_checked: {e}")
                    GLib.idle_add(lbl_ref.set_text, today)

                threading.Thread(target=_wait, daemon=True).start()

            btn.connect("clicked", _on_update)
        grid.attach(btn, 4, row_idx, 1, 1)
        row_idx += 1

    outer.append(grid)
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_child(outer)
    return scroll

    return outer
