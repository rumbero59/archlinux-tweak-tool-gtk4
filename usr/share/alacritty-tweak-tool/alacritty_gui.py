"""GTK4 GUI for alacritty-tweak-tool — three-tab Notebook interface."""
import shutil
import subprocess
import threading

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "3.91")
from gi.repository import Gdk, GLib, Gtk, Vte

import alacritty_config as cfg
import alacritty_themes as themes


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
                ["sh", "-c", "fc-list : family | grep -i Mono"],
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

    # ── Paned: theme list (left) | detail panel (right) ──────────────────────
    paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
    paned.set_vexpand(True)
    paned.set_position(320)

    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll.set_min_content_width(300)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    listbox.add_css_class("theme-list")
    scroll.set_child(listbox)
    paned.set_start_child(scroll)

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
        prefs.update({"source": current_source[0], "search": search_text[0], "tone": tone_filter[0]})
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

    vte_terminal = Vte.Terminal()
    vte_terminal.set_vexpand(True)
    vte_terminal.set_hexpand(True)
    detail_box.append(vte_terminal)

    btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_row.set_margin_top(8)
    btn_row.set_margin_bottom(4)
    btn_apply = Gtk.Button(label="Apply Theme")
    btn_apply.add_css_class("suggested-action")
    btn_apply.set_sensitive(False)
    btn_undo = Gtk.Button(label="Undo Last Apply")
    btn_row.append(btn_apply)
    btn_row.append(btn_undo)
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

    paned.set_end_child(detail_box)
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

    def on_row_selected(_listbox, row):
        if row is None:
            btn_apply.set_sensitive(False)
            detail_name_lbl.set_markup("<b>Select a theme from the list</b>")
            _update_export_btn()
            return
        selected_colors[0] = row.theme_colors
        selected_name[0] = row.theme_name
        selected_source[0] = row.source_label
        detail_name_lbl.set_markup(f"<b>{GLib.markup_escape_text(row.theme_name)}</b>")
        _apply_vte_colors(vte_terminal, row.theme_colors)
        btn_apply.set_sensitive(True)
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
        print(f"[ATT] Theme applied: {name}")
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

    btn_apply.connect("clicked", on_apply)
    btn_undo.connect("clicked", on_undo)
    btn_export.connect("clicked", on_export)

    loading_lbl = _label("Loading themes…")
    outer.append(loading_lbl)

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
    return GLib.SOURCE_REMOVE


# ── Tab 2: Appearance ──────────────────────────────────────────────────────────

def _build_appearance_tab(window):
    """Return the Appearance tab with font and opacity controls."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    outer.set_margin_top(16)
    outer.set_margin_bottom(12)
    outer.set_margin_start(16)
    outer.set_margin_end(16)

    outer.append(_label("<b>Font</b>", markup=True))
    outer.append(_separator())

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

    outer.append(grid)
    outer.append(_label("<b>Window</b>", markup=True))
    outer.append(_separator())

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

    window_grid.attach(opacity_lbl, 0, 0, 1, 1)
    window_grid.attach(opacity_scale, 1, 0, 1, 1)
    window_grid.attach(decorations_lbl, 0, 1, 1, 1)
    window_grid.attach(decorations_drop, 1, 1, 1, 1)
    window_grid.attach(startup_lbl, 0, 2, 1, 1)
    window_grid.attach(startup_drop, 1, 2, 1, 1)
    window_grid.attach(dynamic_title_lbl, 0, 3, 1, 1)
    window_grid.attach(dynamic_title_switch, 1, 3, 1, 1)
    window_grid.attach(blur_lbl, 0, 4, 1, 1)
    window_grid.attach(blur_switch, 1, 4, 1, 1)

    outer.append(window_grid)

    status_lbl = _label("")

    btn_apply = Gtk.Button(label="Apply Appearance")
    btn_apply.add_css_class("suggested-action")
    btn_apply.set_halign(Gtk.Align.START)
    btn_apply.set_margin_top(12)

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
        status_lbl.set_label("Appearance applied. Restart Alacritty to see changes.")

    btn_apply.connect("clicked", on_apply_appearance)
    outer.append(btn_apply)
    outer.append(status_lbl)

    def _load_fonts():
        loaded_all = _get_fonts(mono_only=False)
        loaded_mono = _get_fonts(mono_only=True)
        GLib.idle_add(_populate_fonts, loaded_all, loaded_mono)

    def _populate_fonts(loaded_all, loaded_mono):
        all_fonts[0] = loaded_all
        mono_fonts[0] = loaded_mono
        _reload_drop(loaded_mono if mono_switch.get_active() else loaded_all)
        font_drop.set_sensitive(True)
        mono_switch.set_sensitive(True)
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
    btn_apply_scrolling.set_halign(Gtk.Align.START)
    btn_apply_scrolling.set_margin_top(8)
    status_scrolling = _label("")

    def on_apply_scrolling(_widget):
        cfg.apply_scrolling(int(scroll_spin.get_value()), int(multiplier_spin.get_value()))
        status_scrolling.set_label("Scrolling applied. Restart Alacritty to see changes.")

    btn_apply_scrolling.connect("clicked", on_apply_scrolling)
    outer.append(btn_apply_scrolling)
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
    btn_apply_padding.set_halign(Gtk.Align.START)
    btn_apply_padding.set_margin_top(8)
    status_padding = _label("")

    def on_apply_padding(_widget):
        cfg.apply_window_padding(int(pad_x_spin.get_value()), int(pad_y_spin.get_value()))
        status_padding.set_label("Padding applied. Restart Alacritty to see changes.")

    btn_apply_padding.connect("clicked", on_apply_padding)
    outer.append(btn_apply_padding)
    outer.append(status_padding)

    # ── Cursor ────────────────────────────────────────────────────────────────
    outer.append(_label("<b>Cursor</b>", markup=True))
    outer.append(_separator())

    cursor_grid = Gtk.Grid()
    cursor_grid.set_column_spacing(12)
    cursor_grid.set_row_spacing(10)
    cursor_grid.set_margin_top(8)

    current_shape, current_blink = cfg.get_current_cursor()
    current_thickness, current_blink_rate, current_blink_timeout, current_hollow = cfg.get_current_cursor_extras()
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

    blink_rate_lbl = _label("Blink rate (ms)")
    blink_rate_spin = Gtk.SpinButton.new_with_range(100, 2000, 50)
    blink_rate_spin.set_value(current_blink_rate)

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
    cursor_grid.attach(blink_rate_lbl, 0, 3, 1, 1)
    cursor_grid.attach(blink_rate_spin, 1, 3, 1, 1)
    cursor_grid.attach(blink_timeout_lbl, 0, 4, 1, 1)
    cursor_grid.attach(blink_timeout_spin, 1, 4, 1, 1)
    cursor_grid.attach(hollow_lbl, 0, 5, 1, 1)
    cursor_grid.attach(hollow_switch, 1, 5, 1, 1)
    outer.append(cursor_grid)

    btn_apply_cursor = Gtk.Button(label="Apply Cursor")
    btn_apply_cursor.add_css_class("suggested-action")
    btn_apply_cursor.set_halign(Gtk.Align.START)
    btn_apply_cursor.set_margin_top(8)
    status_cursor = _label("")

    def on_apply_cursor(_widget):
        selected = shape_drop.get_selected()
        shape = shapes[selected] if selected < len(shapes) else "Block"
        cfg.apply_cursor_full(
            shape, blink_switch.get_active(),
            thickness_scale.get_value(),
            int(blink_rate_spin.get_value()),
            int(blink_timeout_spin.get_value()),
            hollow_switch.get_active(),
        )
        status_cursor.set_label("Cursor applied. Restart Alacritty to see changes.")

    btn_apply_cursor.connect("clicked", on_apply_cursor)
    outer.append(btn_apply_cursor)
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
    btn_apply_font_offset.set_halign(Gtk.Align.START)
    btn_apply_font_offset.set_margin_top(8)
    status_font_offset = _label("")

    def on_apply_font_offset(_widget):
        cfg.apply_font_offset(int(off_x_spin.get_value()), int(off_y_spin.get_value()))
        status_font_offset.set_label("Font spacing applied. Restart Alacritty to see changes.")

    btn_apply_font_offset.connect("clicked", on_apply_font_offset)
    outer.append(btn_apply_font_offset)
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
    btn_apply.set_halign(Gtk.Align.START)
    btn_apply.set_margin_top(12)
    status_lbl = _label("")

    def on_apply_behavior(_widget):
        cfg.apply_behavior(save_switch.get_active(), hide_switch.get_active(), live_switch.get_active())
        status_lbl.set_label("Behavior applied. Restart Alacritty to see changes.")

    btn_apply.connect("clicked", on_apply_behavior)
    outer.append(btn_apply)
    outer.append(status_lbl)

    return outer
