# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================


def gui(self, Gtk, vboxstack3, fn):
    """create a gui"""
    hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl1 = Gtk.Label(xalign=0)
    lbl1.set_text("Privacy/Security")
    lbl1.set_name("title")
    hbox3.append(lbl1)

    hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(True)
    hbox4.append(hseparator)

    # ==========================================================
    #                       HBLOCK
    # ==========================================================

    hbox7 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox8 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox11 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    label_top = Gtk.Label()
    label_top.set_markup(
        "Improve your <b>security</b> and <b>privacy</b> \
by blocking ads, tracking and malware domains"
    )
    label_top.set_margin_start(10)
    label_top.set_margin_end(10)
    hbox8.append(label_top)

    instructions = Gtk.Label()
    instructions.set_markup(
        "To update your hblock hosts file, please disable and enable hblock"
    )
    instructions.set_margin_start(10)
    instructions.set_margin_end(10)
    hbox11.append(instructions)

    label_hblock = Gtk.Label()
    label_hblock.set_text(
        "Enable/install hblock - Your orignal /etc/hosts file can be found in /etc/hosts.bak"
    )

    self.label7 = Gtk.Label(xalign=0)
    self.progress = Gtk.ProgressBar()
    self.progress.set_pulse_step(0.2)

    state = fn.hblock_get_state(self)

    self.hbswich = Gtk.Switch()
    self.hbswich.connect("notify::active", self.set_hblock)
    self.hbswich.set_active(state)

    label_hblock.set_margin_start(10)
    label_hblock.set_margin_end(10)
    label_hblock.set_hexpand(True)
    hbox7.append(label_hblock)
    self.hbswich.set_margin_start(10)
    self.hbswich.set_margin_end(10)
    hbox7.append(self.hbswich)  # pack_end

    # ==========================================================
    #                       FIREFOX
    # ==========================================================

    hbox9 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox10 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    label_firefox = Gtk.Label()
    label_firefox.set_markup("Install extra <b>Firefox</b> extensions")
    label_firefox.set_margin_start(10)
    label_firefox.set_margin_end(10)
    hbox9.append(label_firefox)

    label_firefox_ublock = Gtk.Label()
    label_firefox_ublock.set_markup("Install/remove uBlock Origin")
    label_firefox_ublock.set_margin_start(30)

    state = fn.ublock_get_state(self)

    self.firefox_ublock_switch = Gtk.Switch()
    self.firefox_ublock_switch.connect("notify::active", self.set_ublock_firefox)
    self.firefox_ublock_switch.set_active(state)

    # if state:
    #         self.label7.set_text("uBlock Origin active")
    # else:
    #     self.label7.set_text("UBlock Origin inactive")

    label_firefox_ublock.set_margin_start(10)
    label_firefox_ublock.set_margin_end(10)
    label_firefox_ublock.set_hexpand(True)
    hbox10.append(label_firefox_ublock)
    self.firefox_ublock_switch.set_margin_start(10)
    self.firefox_ublock_switch.set_margin_end(10)
    hbox10.append(self.firefox_ublock_switch)  # pack_end

    # ==========================================================
    #                      VSTACK
    # ==========================================================

    vboxstack3.append(hbox3)
    vboxstack3.append(hbox4)
    vboxstack3.append(hbox8)
    vboxstack3.append(hbox11)
    vboxstack3.append(hbox7)
    vboxstack3.append(hbox9)
    vboxstack3.append(hbox10)

    vboxstack3.append(self.label7)  # pack_end
    vboxstack3.append(self.progress)  # pack_end
