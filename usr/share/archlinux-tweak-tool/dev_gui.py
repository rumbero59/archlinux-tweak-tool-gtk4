# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================


def _detect_bootloader(fn):
    candidates = [
        ("/boot/efi/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/boot/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/efi/EFI/systemd/systemd-bootx64.efi", "systemd-boot"),
        ("/boot/grub/grub.cfg", "GRUB"),
        ("/boot/grub2/grub.cfg", "GRUB"),
        ("/boot/limine.cfg", "limine"),
        ("/boot/refind_linux.conf", "rEFInd"),
    ]
    for path, name in candidates:
        if fn.path.exists(path):
            return name
    return "unknown"


def gui(self, Gtk, vboxstack_dev, fn):
    fn.log_section("Dev Diagnostics")

    hbox_title = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl_title = Gtk.Label(xalign=0)
    lbl_title.set_text("Dev Diagnostics")
    lbl_title.set_name("title")
    lbl_title.set_margin_start(10)
    lbl_title.set_margin_end(10)
    hbox_title.append(lbl_title)

    hbox_sep = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hsep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hsep.set_hexpand(True)
    hbox_sep.append(hsep)

    grid = Gtk.Grid()
    grid.set_column_spacing(30)
    grid.set_row_spacing(8)
    grid.set_margin_start(10)
    grid.set_margin_end(10)
    grid.set_margin_top(10)
    grid.set_margin_bottom(10)

    row = [0]

    def _header(text):
        if row[0] > 0:
            spacer = Gtk.Label()
            spacer.set_text("")
            grid.attach(spacer, 0, row[0], 3, 1)
            row[0] += 1
        lbl = Gtk.Label(xalign=0)
        lbl.set_markup(f"<b>{text}</b>")
        grid.attach(lbl, 0, row[0], 3, 1)
        row[0] += 1

    def _row(check, value, status_markup=""):
        lbl_check = Gtk.Label(xalign=0)
        lbl_check.set_text(check)
        lbl_check.set_size_request(280, -1)

        lbl_value = Gtk.Label(xalign=0)
        lbl_value.set_text(str(value))
        lbl_value.set_size_request(200, -1)

        lbl_status = Gtk.Label(xalign=0)
        if status_markup:
            lbl_status.set_markup(status_markup)

        grid.attach(lbl_check, 0, row[0], 1, 1)
        grid.attach(lbl_value, 1, row[0], 1, 1)
        grid.attach(lbl_status, 2, row[0], 1, 1)
        row[0] += 1

    # ── Distro Detection ────────────────────────────────────────
    _header("Distro Detection")

    distr_label = fn.get_distro_label()
    distr_match = fn.distr.lower() == distr_label.lower()
    mismatch = "" if distr_match else "<span foreground='orange'>⚠ mismatch</span>"

    _row("fn.distr", fn.distr)
    _row("get_distro_label()", distr_label, mismatch)

    # ── Environment ─────────────────────────────────────────────
    _header("Environment")

    desktop = fn.desktop if fn.desktop else "(not set)"
    _row("fn.desktop  (XDG_CURRENT_DESKTOP)", desktop)
    _row("fn.sudo_username", fn.sudo_username)
    _row("fn.home", fn.home)

    # ── Repositories ─────────────────────────────────────────────
    _header("Repositories")

    chaotic = fn.check_chaotic_aur_active()
    nemesis = fn.check_nemesis_repo_active()
    _row("chaotic-AUR active", chaotic,
         "<span foreground='green'>active</span>" if chaotic else "")
    _row("nemesis repo active", nemesis,
         "<span foreground='green'>active</span>" if nemesis else "")

    # ── System ───────────────────────────────────────────────────
    _header("System")

    _row("bootloader", _detect_bootloader(fn))
    _row("initramfs", "dracut" if fn.path.exists("/usr/bin/dracut") else "mkinitcpio")
    _row("plymouth installed", fn.check_package_installed("plymouth"))
    _row("systemd PID 1", fn.path.exists("/run/systemd/private"))

    vboxstack_dev.append(hbox_title)
    vboxstack_dev.append(hbox_sep)
    vboxstack_dev.append(grid)
