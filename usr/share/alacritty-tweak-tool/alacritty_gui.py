"""GTK4 GUI for alacritty-tweak-tool — three-tab Notebook interface."""
import shutil
import subprocess
import threading

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Vte", "2.91")
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
    """Return a sorted deduplicated list of font family names.

    Pass mono_only=True to restrict to fonts with spacing=mono.
    """
    fc_args = ["fc-list", ":spacing=mono:", "family"] if mono_only else ["fc-list", "family"]
    try:
        result = subprocess.run(fc_args, capture_output=True, text=True, timeout=5)
        fonts = set()
        for line in result.stdout.splitlines():
            for name in line.split(","):
                name = name.strip()
                if name:
                    fonts.add(name)
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

def build(window):
    """Build and attach the full GUI to the given Gtk.ApplicationWindow."""
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    root.set_margin_top(12)
    root.set_margin_bottom(12)
    root.set_margin_start(12)
    root.set_margin_end(12)

    title = _label("Alacritty Tweak Tool")
    title.set_name("title")
    title.set_margin_bottom(8)
    root.append(title)
    root.append(_separator())

    notebook = Gtk.Notebook()
    notebook.set_margin_top(10)
    notebook.set_vexpand(True)

    notebook.append_page(_build_themes_tab(window), Gtk.Label(label="  Themes  "))
    notebook.append_page(_build_appearance_tab(window), Gtk.Label(label="  Appearance  "))
    notebook.append_page(_build_advanced_tab(window), Gtk.Label(label="  Advanced  "))

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

    controls_box.append(source_drop)
    controls_box.append(search_entry)
    outer.append(controls_box)

    # ── Shared filter state ───────────────────────────────────────────────────
    # Mutable containers so closures can update them after async load.
    current_source = [""]
    search_text = [""]
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
        if current_source[0] and row.source_label != current_source[0]:
            return False
        q = search_text[0].lower()
        if q and q not in row.theme_name.lower():
            return False
        return True

    listbox.set_filter_func(filter_row)

    def on_source_changed(_drop, _param):
        idx = source_drop.get_selected()
        if idx < len(source_labels):
            current_source[0] = source_labels[idx]
            listbox.invalidate_filter()

    def on_search_changed(entry):
        search_text[0] = entry.get_text()
        listbox.invalidate_filter()

    source_drop.connect("notify::selected", on_source_changed)
    search_entry.connect("search-changed", on_search_changed)

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
    btn_row.append(btn_apply)
    detail_box.append(btn_row)

    status_lbl = _label("")
    detail_box.append(status_lbl)

    paned.set_end_child(detail_box)
    outer.append(paned)

    # Spawn fastfetch once when VTE is first shown; subsequent theme selections
    # only update the color palette — VTE re-renders existing text with new colors.
    vte_terminal.connect("realize", lambda _w: _spawn_in_vte(vte_terminal))

    # ── Selection callback ────────────────────────────────────────────────────
    selected_colors = [None]

    def on_row_selected(_listbox, row):
        if row is None:
            btn_apply.set_sensitive(False)
            detail_name_lbl.set_markup("<b>Select a theme from the list</b>")
            return
        selected_colors[0] = row.theme_colors
        detail_name_lbl.set_markup(f"<b>{GLib.markup_escape_text(row.theme_name)}</b>")
        _apply_vte_colors(vte_terminal, row.theme_colors)
        btn_apply.set_sensitive(True)
        status_lbl.set_label("")

    listbox.connect("row-selected", on_row_selected)

    def on_apply(_widget):
        if selected_colors[0] is None:
            return
        themes.apply_theme(selected_colors[0])
        status_lbl.set_label("Theme applied. Restart Alacritty to see changes.")

    btn_apply.connect("clicked", on_apply)

    loading_lbl = _label("Loading themes…")
    outer.append(loading_lbl)

    # Store references for async population
    window._theme_listbox = listbox
    window._source_drop = source_drop
    window._source_labels = source_labels
    window._current_source = current_source
    window._theme_loading_lbl = loading_lbl

    return outer


def _load_themes_async(window):
    """Load all theme sources in a background thread, then populate the ListBox."""
    by_source = themes.load_themes_by_source()
    GLib.idle_add(_populate_theme_list, window, by_source)


def _populate_theme_list(window, by_source):
    """Called on the GTK main thread to populate the ListBox and update the source dropdown."""
    listbox = window._theme_listbox
    source_drop = window._source_drop
    source_labels = window._source_labels
    current_source = window._current_source

    labels = list(by_source.keys())
    display_labels = [f"{lbl}  ·  {len(by_source[lbl])}" for lbl in labels]

    # Populate source_labels before updating model to avoid a stale read in on_source_changed.
    source_labels.clear()
    source_labels.extend(labels)
    if labels:
        current_source[0] = labels[0]

    source_drop.set_model(Gtk.StringList.new(display_labels))
    source_drop.set_selected(0)

    total = 0
    for label in labels:
        for theme_name, colors in by_source[label]:
            normal_rgb = themes.colors_to_rgb_list(colors, "normal")
            row = Gtk.ListBoxRow()
            row.theme_name = theme_name
            row.theme_colors = colors
            row.source_label = label

            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            hbox.set_margin_top(4)
            hbox.set_margin_bottom(4)
            hbox.set_margin_start(6)
            hbox.set_margin_end(6)

            name_lbl = Gtk.Label(label=theme_name)
            name_lbl.set_xalign(0.0)
            name_lbl.set_hexpand(True)

            swatch = _make_swatch_area([normal_rgb], 80, 14)

            hbox.append(name_lbl)
            hbox.append(swatch)
            row.set_child(hbox)
            listbox.append(row)
            total += 1

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
    mono_fonts = _get_fonts(mono_only=True)
    filter_text = [""]

    # ── Font family: text entry + popover showing filtered mono fonts ─────────
    font_lbl = _label("Family")

    font_entry = Gtk.Entry()
    font_entry.set_text(current_family)
    font_entry.set_hexpand(True)
    font_entry.set_placeholder_text("Type to search monospace fonts…")

    pop_scroll = Gtk.ScrolledWindow()
    pop_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    pop_scroll.set_size_request(300, 180)

    font_listbox = Gtk.ListBox()
    font_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    for fname in mono_fonts:
        row = Gtk.ListBoxRow()
        row.font_name = fname
        lbl = Gtk.Label(label=fname)
        lbl.set_xalign(0.0)
        lbl.set_margin_start(8)
        lbl.set_margin_end(8)
        lbl.set_margin_top(3)
        lbl.set_margin_bottom(3)
        row.set_child(lbl)
        font_listbox.append(row)

    def font_filter_func(row):
        q = filter_text[0].lower()
        return not q or q in row.font_name.lower()

    font_listbox.set_filter_func(font_filter_func)
    pop_scroll.set_child(font_listbox)

    font_popover = Gtk.Popover()
    font_popover.set_has_arrow(False)
    font_popover.set_position(Gtk.PositionType.BOTTOM)
    font_popover.set_child(pop_scroll)
    font_popover.set_parent(font_entry)

    def on_font_entry_changed(entry):
        filter_text[0] = entry.get_text()
        font_listbox.invalidate_filter()
        font_popover.popup()

    def on_font_row_activated(_listbox, row):
        font_entry.set_text(row.font_name)
        filter_text[0] = ""
        font_listbox.invalidate_filter()
        font_popover.popdown()

    # Close popover when focus leaves the entry (short delay lets a row click register).
    focus_ctrl = Gtk.EventControllerFocus()
    focus_ctrl.connect("leave", lambda _: GLib.timeout_add(150, font_popover.popdown))
    font_entry.add_controller(focus_ctrl)

    font_entry.connect("changed", on_font_entry_changed)
    font_entry.connect("activate", lambda _: font_popover.popdown())
    font_listbox.connect("row-activated", on_font_row_activated)

    grid.attach(font_lbl, 0, 0, 1, 1)
    grid.attach(font_entry, 1, 0, 1, 1)

    # ── Font size ─────────────────────────────────────────────────────────────
    size_lbl = _label("Size")
    size_spin = Gtk.SpinButton.new_with_range(6.0, 32.0, 0.5)
    size_spin.set_value(current_size)
    size_spin.set_digits(1)

    grid.attach(size_lbl, 0, 1, 1, 1)
    grid.attach(size_spin, 1, 1, 1, 1)

    outer.append(grid)
    outer.append(_label("<b>Window</b>", markup=True))
    outer.append(_separator())

    opacity_grid = Gtk.Grid()
    opacity_grid.set_column_spacing(12)
    opacity_grid.set_row_spacing(10)
    opacity_grid.set_margin_top(8)

    current_opacity = cfg.get_current_opacity()

    opacity_lbl = _label("Opacity")
    opacity_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0.1, 1.0, 0.05)
    opacity_scale.set_value(current_opacity)
    opacity_scale.set_draw_value(True)
    opacity_scale.set_digits(2)
    opacity_scale.set_hexpand(True)
    opacity_scale.set_size_request(250, -1)

    opacity_grid.attach(opacity_lbl, 0, 0, 1, 1)
    opacity_grid.attach(opacity_scale, 1, 0, 1, 1)

    outer.append(opacity_grid)

    status_lbl = _label("")

    btn_apply = Gtk.Button(label="Apply Appearance")
    btn_apply.add_css_class("suggested-action")
    btn_apply.set_halign(Gtk.Align.START)
    btn_apply.set_margin_top(12)

    def on_apply_appearance(_widget):
        family = font_entry.get_text().strip() or "monospace"
        size = size_spin.get_value()
        opacity = opacity_scale.get_value()
        cfg.apply_appearance(family, size, opacity)
        status_lbl.set_label("Appearance applied. Restart Alacritty to see changes.")

    btn_apply.connect("clicked", on_apply_appearance)
    outer.append(btn_apply)
    outer.append(status_lbl)

    return outer


# ── Tab 3: Advanced ────────────────────────────────────────────────────────────

def _build_advanced_tab(window):
    """Return the Advanced tab with scrollback and cursor controls."""
    outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    outer.set_margin_top(16)
    outer.set_margin_bottom(12)
    outer.set_margin_start(16)
    outer.set_margin_end(16)

    outer.append(_label("<b>Scrollback</b>", markup=True))
    outer.append(_separator())

    scroll_grid = Gtk.Grid()
    scroll_grid.set_column_spacing(12)
    scroll_grid.set_row_spacing(10)
    scroll_grid.set_margin_top(8)

    current_scrollback = cfg.get_current_scrollback()

    scroll_lbl = _label("History (lines)")
    # Alacritty has no true unlimited scrollback; 0 disables it entirely.
    # High values work but consume RAM proportionally.
    scroll_spin = Gtk.SpinButton.new_with_range(0, 999999, 1000)
    scroll_spin.set_value(current_scrollback)

    scroll_note = _label("Max ~1 million lines. There is no true unlimited.", css_class="info-label")

    scroll_grid.attach(scroll_lbl, 0, 0, 1, 1)
    scroll_grid.attach(scroll_spin, 1, 0, 1, 1)
    scroll_grid.attach(scroll_note, 1, 1, 1, 1)
    outer.append(scroll_grid)

    outer.append(_label("<b>Cursor</b>", markup=True))
    outer.append(_separator())

    cursor_grid = Gtk.Grid()
    cursor_grid.set_column_spacing(12)
    cursor_grid.set_row_spacing(10)
    cursor_grid.set_margin_top(8)

    current_shape, current_blink = cfg.get_current_cursor()
    shapes = ["Block", "Beam", "Underline"]

    shape_lbl = _label("Shape")
    shape_list = Gtk.StringList.new(shapes)
    shape_drop = Gtk.DropDown.new(shape_list, None)
    if current_shape in shapes:
        shape_drop.set_selected(shapes.index(current_shape))

    blink_lbl = _label("Blink")
    blink_switch = Gtk.Switch()
    blink_switch.set_active(current_blink)
    blink_switch.set_halign(Gtk.Align.START)

    cursor_grid.attach(shape_lbl, 0, 0, 1, 1)
    cursor_grid.attach(shape_drop, 1, 0, 1, 1)
    cursor_grid.attach(blink_lbl, 0, 1, 1, 1)
    cursor_grid.attach(blink_switch, 1, 1, 1, 1)
    outer.append(cursor_grid)

    status_lbl = _label("")

    btn_apply = Gtk.Button(label="Apply Advanced Settings")
    btn_apply.add_css_class("suggested-action")
    btn_apply.set_halign(Gtk.Align.START)
    btn_apply.set_margin_top(12)

    def on_apply_advanced(_widget):
        scrollback = int(scroll_spin.get_value())
        selected = shape_drop.get_selected()
        shape = shapes[selected] if selected < len(shapes) else "Block"
        blink = blink_switch.get_active()
        cfg.apply_advanced(scrollback, shape, blink)
        status_lbl.set_label("Advanced settings applied. Restart Alacritty to see changes.")

    btn_apply.connect("clicked", on_apply_advanced)
    outer.append(btn_apply)
    outer.append(status_lbl)

    return outer
