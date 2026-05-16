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


def _detect_display_manager(fn):
    dm_svc = "/etc/systemd/system/display-manager.service"
    if fn.path.islink(dm_svc):
        try:
            target = fn.readlink(dm_svc)
            return fn.path.basename(target).replace(".service", "")
        except OSError:
            pass
    return "unknown"


def _mkinitcpio_has_plymouth():
    try:
        for line in open("/etc/mkinitcpio.conf"):
            s = line.strip()
            if s.startswith("HOOKS=") and not s.startswith("#"):
                return "plymouth" in s
    except OSError:
        pass
    return False


def gui(self, Gtk, vboxstack_dev, fn):
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
    mismatch = "" if distr_match else "<span foreground='orange'>&#9888; mismatch</span>"

    _row("fn.distr", fn.distr)
    _row("get_distro_label()", distr_label, mismatch)

    # ── Environment ──────────────────────────────────────────────
    _header("Environment")

    desktop = fn.desktop if fn.desktop else "(not set)"
    _row("XDG_CURRENT_DESKTOP", desktop)
    _row("fn.sudo_username", fn.sudo_username)
    _row("fn.home", fn.home)

    # ── Session ──────────────────────────────────────────────────
    _header("Session")

    _session_type = "(unknown)"
    try:
        import os as _os
        _session_type = _os.getenv("XDG_SESSION_TYPE") or "(not set)"
    except Exception:
        pass

    _shell = fn.get_shell() or "(unknown)"

    _row("XDG_SESSION_TYPE", _session_type)
    _row("active shell", _shell)

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

    _bootloader = _detect_bootloader(fn)

    try:
        _kernel = fn.subprocess.run(
            ["uname", "-r"], capture_output=True, text=True
        ).stdout.strip()
    except Exception:
        _kernel = "unknown"

    _is_openrc = fn.path.exists("/run/openrc") or fn.path.exists("/sbin/openrc")
    _init_system = "OpenRC" if _is_openrc else "systemd"
    _initramfs = "dracut" if fn.path.exists("/usr/bin/dracut") else "mkinitcpio"

    _row("bootloader", _bootloader)
    _row("running kernel", _kernel)
    _row("init system", _init_system)
    _row("initramfs", _initramfs)
    _row("systemd PID 1", fn.path.exists("/run/systemd/private"))

    # ── Plymouth ─────────────────────────────────────────────────
    _header("Plymouth")

    _ply_installed = fn.check_package_installed("plymouth")
    _ply_enabled = fn.check_service_enabled("plymouth") if _ply_installed else False

    _ply_theme = "(not installed)"
    if _ply_installed:
        try:
            _ply_theme = fn.subprocess.run(
                ["plymouth-set-default-theme"],
                capture_output=True, text=True
            ).stdout.strip() or "(none)"
        except Exception:
            _ply_theme = "(error)"

    if _initramfs == "mkinitcpio":
        _ply_hooks_ok = _mkinitcpio_has_plymouth()
        _hooks_label = "HOOKS contains plymouth"
    else:
        _ply_hooks_ok = fn.path.exists("/etc/dracut.conf.d/att-plymouth.conf")
        _hooks_label = "att-plymouth.conf exists"

    _row("plymouth installed", _ply_installed,
         "<span foreground='green'>yes</span>" if _ply_installed else "")
    _row("plymouth service enabled", _ply_enabled,
         "<span foreground='green'>enabled</span>" if _ply_enabled else "")
    _row("active theme", _ply_theme)
    _row(_hooks_label, _ply_hooks_ok,
         "<span foreground='green'>yes</span>" if _ply_hooks_ok
         else ("<span foreground='orange'>missing</span>" if _ply_installed else ""))

    if _bootloader == "systemd-boot":
        _cmdline_exists = fn.path.exists("/etc/kernel/cmdline")
        _cmdline_ok = False
        if _cmdline_exists:
            try:
                tokens = open("/etc/kernel/cmdline").read().split()
                _cmdline_ok = "quiet" in tokens and "splash" in tokens
            except OSError:
                pass
        _cmdline_status = (
            "<span foreground='green'>OK</span>" if _cmdline_ok
            else ("<span foreground='orange'>missing quiet/splash</span>" if _cmdline_exists
                  else "<span foreground='orange'>file not found</span>")
        )
        _row("/etc/kernel/cmdline splash", _cmdline_ok, _cmdline_status)

    # ── Login Manager ────────────────────────────────────────────
    _header("Login Manager")

    _dm = _detect_display_manager(fn)
    _sddm_installed = fn.check_package_installed("sddm")
    _sddm_enabled = fn.check_service_enabled("sddm") if _sddm_installed else False
    _plasma_login = fn.check_service_enabled("plasma-login")

    _row("active display manager", _dm)
    _row("sddm installed", _sddm_installed,
         "<span foreground='green'>yes</span>" if _sddm_installed else "")
    _row("sddm enabled", _sddm_enabled,
         "<span foreground='green'>yes</span>" if _sddm_enabled else "")
    _row("plasma-login enabled (hides SDDM tab)", _plasma_login,
         "<span foreground='orange'>yes — SDDM tab hidden</span>" if _plasma_login else "")

    vboxstack_dev.append(hbox_title)
    vboxstack_dev.append(hbox_sep)
    vboxstack_dev.append(grid)
