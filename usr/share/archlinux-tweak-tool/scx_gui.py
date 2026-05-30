# ============================================================
# Authors: Erik Dubois
# ============================================================
# sched-ext / scx scheduler selector — DEV page block (interactive).
# Sits at the top of the Dev Diagnostics page. Backend logic in scx.py.

import scx


def build(self, Gtk, parent_box, fn):
    """Build the scx scheduler block and append it to the top of the DEV page."""
    fn.log_info("Building scx scheduler block (DEV page)")

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_margin_start(10)
    box.set_margin_end(10)
    box.set_margin_top(10)

    title = Gtk.Label(xalign=0)
    title.set_markup("<big><b>CPU Scheduler (sched-ext / scx)</b></big>")
    box.append(title)

    desc = Gtk.Label(xalign=0)
    desc.set_markup(
        "Switch the live CPU scheduler without a reboot, via <b>scx_loader</b>.\n"
        "Default is OFF — the kernel default (EEVDF / BORE) stays in charge until you pick a mode."
    )
    box.append(desc)

    # ── Active-scheduler readout ───────────────────────────────────────
    self.scx_status_label = Gtk.Label(xalign=0)
    box.append(self.scx_status_label)

    # ── Gate / hint note ───────────────────────────────────────────────
    self.scx_note_label = Gtk.Label(xalign=0)
    box.append(self.scx_note_label)

    # ── Package row (install-on-demand) ────────────────────────────────
    pkg_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.scx_package_label = Gtk.Label(xalign=0)
    self.scx_package_label.set_hexpand(True)
    pkg_row.append(self.scx_package_label)
    self.btn_install_scx = Gtk.Button(label="Install scx-scheds")
    pkg_row.append(self.btn_install_scx)
    box.append(pkg_row)

    # ── Mode selector ──────────────────────────────────────────────────
    ctrl_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    ctrl_label = Gtk.Label(xalign=0)
    ctrl_label.set_text("Mode:")
    ctrl_row.append(ctrl_label)

    self.scx_mode_dropdown = Gtk.DropDown.new_from_strings(scx.MODES)
    ctrl_row.append(self.scx_mode_dropdown)

    self.btn_apply_scx = Gtk.Button(label="Apply")
    ctrl_row.append(self.btn_apply_scx)

    self.btn_disable_scx = Gtk.Button(label="Back to default")
    ctrl_row.append(self.btn_disable_scx)
    box.append(ctrl_row)

    sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sep.set_hexpand(True)
    box.append(sep)

    # ── Refresh: re-read state and re-gate the controls ────────────────
    def _refresh(*_a):
        supported = scx.sched_ext_supported()
        installed = scx.scheds_installed()

        self.scx_status_label.set_markup(f"Active scheduler: <b>{scx.get_active_scheduler()}</b>")

        if not supported:
            self.scx_note_label.set_markup(
                "<span foreground='orange'>This kernel has no sched-ext support — "
                "boot linux-cachyos or linux-zen to use it.</span>"
            )
        elif not installed:
            self.scx_note_label.set_text("Install scx-scheds to switch schedulers from here.")
        else:
            self.scx_note_label.set_text("Pick a mode and Apply. 'Back to default' returns to EEVDF / BORE.")

        if installed:
            self.scx_package_label.set_markup("scx-scheds is <b>installed</b>")
        else:
            self.scx_package_label.set_text("scx-scheds is not installed")

        self.btn_install_scx.set_sensitive(supported and not installed)
        controls_live = supported and installed
        self.scx_mode_dropdown.set_sensitive(controls_live)
        self.btn_apply_scx.set_sensitive(controls_live)
        self.btn_disable_scx.set_sensitive(controls_live)

    self.btn_install_scx.connect("clicked", lambda _w: scx.install_scx(self, _w, _refresh))
    self.btn_apply_scx.connect(
        "clicked",
        lambda _w: scx.apply_mode(self, scx.MODES[self.scx_mode_dropdown.get_selected()], _refresh),
    )
    self.btn_disable_scx.connect("clicked", lambda _w: scx.disable_scx(self, _w, _refresh))

    box.connect("map", _refresh)
    _refresh()

    parent_box.append(box)
