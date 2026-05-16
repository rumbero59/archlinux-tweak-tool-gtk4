"""GTK4 GUI for alacritty-tweak-tool — three-tab Notebook interface."""
import subprocess
import threading

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib

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


def _get_monospace_fonts():
    """Return a sorted deduplicated list of monospace font family names."""
    try:
        result = subprocess.run(
            ["fc-list", ":spacing=mono:", "family"],
            capture_output=True, text=True, timeout=5
        )
        fonts = set()
        for line in result.stdout.splitlines():
            for name in line.split(","):
                name = name.strip()
                if name:
                    fonts.add(name)
        return sorted(fonts) or ["monospace"]
    except Exception:
        return ["monospace"]


# ── Build entry point ──────────────────────────────────────────────────────────

def build(window):
    """Build and attach the full GUI to the given Gtk.ApplicationWindow."""
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    root.set_margin_top(12)
    root.set_margin_bottom(12)
    root.set_margin_start(12)
    root.set_margin_end(12)

    # Title
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

    # Load themes in background to keep the window responsive
    threading.Thread(target=_load_themes_async, args=(window,), daemon=True).start()


# ── Tab 1: Themes ──────────────────────────────────────────────────────────────

def _build_themes_tab(window):
    """Return the Themes tab widget with ListBox, swatch detail, and action buttons."""
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
    info_lbl.set_margin_bottom(6)
    outer.append(info_lbl)

    # ── Paned: theme list (left) | detail panel (right) ──────────────────────
    paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
    paned.set_vexpand(True)
    paned.set_position(320)

    # Left: scrolled ListBox
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll.set_min_content_width(300)

    listbox = Gtk.ListBox()
    listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
    listbox.add_css_class("theme-list")
    scroll.set_child(listbox)
    paned.set_start_child(scroll)

    # Right: detail panel
    detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    detail_box.set_margin_top(10)
    detail_box.set_margin_start(12)
    detail_box.set_margin_end(6)

    detail_name_lbl = _label("Select a theme", css_class="detail-name")
    detail_name_lbl.set_markup("<b>Select a theme from the list</b>")

    # Large swatch: 8 normal (top row) + 8 bright (bottom row)
    detail_rgb = {"normal": [(0.5, 0.5, 0.5)] * 8, "bright": [(0.5, 0.5, 0.5)] * 8}
    detail_area = Gtk.DrawingArea()
    detail_area.set_size_request(400, 60)

    def draw_detail(area, cr, w, h, _):
        sw = w / 8
        row_h = h / 2
        for i, (r, g, b) in enumerate(detail_rgb["normal"]):
            cr.set_source_rgb(r, g, b)
            cr.rectangle(i * sw, 0, sw, row_h)
            cr.fill()
        for i, (r, g, b) in enumerate(detail_rgb["bright"]):
            cr.set_source_rgb(r, g, b)
            cr.rectangle(i * sw, row_h, sw, row_h)
            cr.fill()

    detail_area.set_draw_func(draw_detail, None)

    btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btn_preview = Gtk.Button(label="Preview in Terminal")
    btn_apply = Gtk.Button(label="Apply Theme")
    btn_apply.add_css_class("suggested-action")
    btn_preview.set_sensitive(False)
    btn_apply.set_sensitive(False)
    btn_row.append(btn_preview)
    btn_row.append(btn_apply)

    status_lbl = _label("")

    detail_box.append(detail_name_lbl)
    detail_box.append(detail_area)
    detail_box.append(btn_row)
    detail_box.append(status_lbl)

    paned.set_end_child(detail_box)
    outer.append(paned)

    # Store current selection for button callbacks
    selected_colors = [None]

    def on_row_selected(_listbox, row):
        if row is None:
            btn_preview.set_sensitive(False)
            btn_apply.set_sensitive(False)
            detail_name_lbl.set_markup("<b>Select a theme from the list</b>")
            return
        theme_name = row.theme_name
        colors = row.theme_colors
        selected_colors[0] = colors
        detail_name_lbl.set_markup(f"<b>{GLib.markup_escape_text(theme_name)}</b>")
        detail_rgb["normal"] = themes.colors_to_rgb_list(colors, "normal")
        detail_rgb["bright"] = themes.colors_to_rgb_list(colors, "bright")
        detail_area.queue_draw()
        btn_preview.set_sensitive(True)
        btn_apply.set_sensitive(True)
        status_lbl.set_label("")

    listbox.connect("row-selected", on_row_selected)

    def on_preview(_widget):
        if selected_colors[0] is None:
            return
        status_lbl.set_label("Launching preview terminal…")
        threading.Thread(
            target=themes.preview_theme,
            args=(selected_colors[0],),
            daemon=True,
        ).start()

    def on_apply(_widget):
        if selected_colors[0] is None:
            return
        themes.apply_theme(selected_colors[0])
        status_lbl.set_label("Theme applied. Restart Alacritty to see changes.")

    btn_preview.connect("clicked", on_preview)
    btn_apply.connect("clicked", on_apply)

    # Store references for async theme loading
    window._theme_listbox = listbox
    window._theme_loading_lbl = _label("Loading themes…")
    outer.append(window._theme_loading_lbl)

    return outer


def _load_themes_async(window):
    """Load all theme files in a background thread, then populate the ListBox."""
    all_themes = themes.load_all_themes()
    GLib.idle_add(_populate_theme_list, window, all_themes)


def _populate_theme_list(window, all_themes):
    """Called on the GTK main thread to add theme rows to the ListBox."""
    listbox = window._theme_listbox
    for theme_name, colors in all_themes:
        normal_rgb = themes.colors_to_rgb_list(colors, "normal")
        row = Gtk.ListBoxRow()
        row.theme_name = theme_name
        row.theme_colors = colors

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

    window._theme_loading_lbl.set_label(f"{len(all_themes)} themes loaded")
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
    fonts = _get_monospace_fonts()

    # Font family
    font_lbl = _label("Family")
    font_list = Gtk.StringList.new(fonts)
    font_drop = Gtk.DropDown.new(font_list, None)
    font_drop.set_hexpand(True)
    if current_family in fonts:
        font_drop.set_selected(fonts.index(current_family))

    grid.attach(font_lbl, 0, 0, 1, 1)
    grid.attach(font_drop, 1, 0, 1, 1)

    # Font size
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

    # Opacity
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
        selected = font_drop.get_selected()
        family = fonts[selected] if selected < len(fonts) else "monospace"
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
    scroll_spin = Gtk.SpinButton.new_with_range(1000, 200000, 1000)
    scroll_spin.set_value(current_scrollback)

    scroll_grid.attach(scroll_lbl, 0, 0, 1, 1)
    scroll_grid.attach(scroll_spin, 1, 0, 1, 1)
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
