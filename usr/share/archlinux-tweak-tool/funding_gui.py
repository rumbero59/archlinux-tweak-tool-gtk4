# ============================================================
# Authors: Erik Dubois
# ============================================================

import functools

import funding


def gui(self, Gtk, vboxstack_funding, fn):
    """Create the Support page — links to the project funding channels."""
    # On Kiro the page promotes Kiro; on any other Arch-based distro it promotes ATT.
    is_kiro = fn.get_distro_label() == "Kiro"
    project_name = "Kiro" if is_kiro else "ATT"
    title_text = "Support Kiro" if is_kiro else "Support the ATT"
    section_text = "Support the Kiro Project" if is_kiro else "Support the ATT project"

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_title_label = Gtk.Label(xalign=0)
    hbox_title_label.set_text(title_text)
    hbox_title_label.set_name("title")
    hbox_title_label.set_margin_start(10)
    hbox_title_label.set_margin_end(10)
    hbox_title.append(hbox_title_label)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox_sep.append(hseparator)

    hbox_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_section_label = Gtk.Label(xalign=0)
    hbox_section_label.set_markup(f'<span foreground="#FFA500"><b>{section_text}</b></span>')
    hbox_section_label.set_margin_start(10)
    hbox_section_label.set_margin_top(15)
    hbox_section_label.set_margin_bottom(10)
    hbox_section.append(hbox_section_label)

    hbox_intro = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox_intro_label = Gtk.Label(xalign=0)
    hbox_intro_label.set_text(
        f"{project_name} is free and open source. If it helps you, "
        "here are the ways to support its development."
    )
    hbox_intro_label.set_margin_start(20)
    hbox_intro_label.set_margin_end(10)
    hbox_intro_label.set_margin_bottom(10)
    hbox_intro.append(hbox_intro_label)

    vboxstack_funding.append(hbox_title)
    vboxstack_funding.append(hbox_sep)
    vboxstack_funding.append(hbox_section)
    vboxstack_funding.append(hbox_intro)

    fn.log_info(f"Building Support page funding links ({project_name})")
    for name, url, blurb in funding.SOURCES:
        hbox_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        lbl_row = Gtk.Label(xalign=0)
        lbl_row.set_markup(f"<b>{name}</b> — {blurb}")
        lbl_row.set_margin_start(20)
        lbl_row.set_margin_end(10)
        lbl_row.set_hexpand(True)
        btn_open = Gtk.Button(label="Open")
        btn_open.connect("clicked", functools.partial(funding.on_click_open, self, url))
        btn_open.set_margin_start(10)
        btn_open.set_margin_end(10)
        hbox_row.append(lbl_row)
        hbox_row.append(btn_open)
        vboxstack_funding.append(hbox_row)
