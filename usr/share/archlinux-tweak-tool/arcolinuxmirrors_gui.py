# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================


def gui(self, Gtk, vboxstack1):
    """ArcoLinux mirrorlist"""
    hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl1 = Gtk.Label(xalign=0)
    lbl1.set_text("ArcoLinux Mirrorlist")
    lbl1.set_name("title")
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(True)
    hbox4.append(hseparator)
    hbox3.append(lbl1)

    # ==========================================================
    #                   GLOBALS
    # ==========================================================

    hboxstack4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack7 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack10 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack11 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack12 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack14 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack15 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack16 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack17 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack18 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    hboxstack19 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

    # ========================================================
    #               ARCO REPOS
    # ========================================================

    frame3 = Gtk.Frame(label="")
    frame3lbl = frame3.get_label_widget()
    frame3lbl.set_markup("<b>ArcoLinux Mirrorlist</b>")

    # seedhost
    self.aseed_button = Gtk.Switch()
    self.aseed_button.connect("notify::active", self.on_mirror_seed_repo_toggle)
    label5 = Gtk.Label(xalign=0)
    label5.set_markup(
        "Only github.com is a possible repo - type 'narcomirrorlist' in a terminal to see it"
    )
    seedhost_sync = Gtk.Label(xalign=0)
    label5.set_margin_start(10)
    label5.set_margin_end(10)
    hboxstack7.append(label5)
    #hboxstack7.pack_end(self.aseed_button, False, False, 20)
    seedhost_sync.set_margin_start(10)
    seedhost_sync.set_margin_end(10)
    hboxstack7.append(seedhost_sync)

    # gitlab
    self.agitlab_button = Gtk.Switch()
    self.agitlab_button.connect("notify::active", self.on_mirror_gitlab_repo_toggle)
    label_gitlab = Gtk.Label(xalign=0)
    label_gitlab.set_markup(
        "Enable Gitlab repo - free bandwidth - United States - Always up-to-date"
    )
    gitlab_sync = Gtk.Label(xalign=0)
    label_gitlab.set_margin_start(10)
    label_gitlab.set_margin_end(10)
    label_gitlab.set_hexpand(True)
    hboxstack16.append(label_gitlab)
    self.agitlab_button.set_margin_start(20)
    self.agitlab_button.set_margin_end(20)
    hboxstack16.append(self.agitlab_button)  # pack_end
    gitlab_sync.set_margin_start(10)
    gitlab_sync.set_margin_end(10)
    hboxstack16.append(gitlab_sync)

    # belnet
    self.abelnet_button = Gtk.Switch()
    self.abelnet_button.connect("notify::active", self.on_mirror_belnet_repo_toggle)
    label6 = Gtk.Label(xalign=0)
    label6.set_markup(
        "Enable Belnet repo - free bandwidth - Belgium - Belnet syncs twice per day"
    )
    belnet_sync = Gtk.Label(xalign=0)
    label6.set_margin_start(10)
    label6.set_margin_end(10)
    label6.set_hexpand(True)
    hboxstack14.append(label6)
    self.abelnet_button.set_margin_start(20)
    self.abelnet_button.set_margin_end(20)
    hboxstack14.append(self.abelnet_button)  # pack_end
    belnet_sync.set_margin_start(10)
    belnet_sync.set_margin_end(10)
    hboxstack14.append(belnet_sync)

    # funami
    self.afunami_button = Gtk.Switch()
    self.afunami_button.connect("notify::active", self.on_mirror_funami_repo_toggle)
    labelfunami = Gtk.Label(xalign=0)
    labelfunami.set_markup(
        "Enable Funami repo - free bandwidth - South Korea - Funami syncs once per day"
    )
    funami_sync = Gtk.Label(xalign=0)
    labelfunami.set_margin_start(10)
    labelfunami.set_margin_end(10)
    labelfunami.set_hexpand(True)
    hboxstack18.append(labelfunami)
    self.afunami_button.set_margin_start(20)
    self.afunami_button.set_margin_end(20)
    hboxstack18.append(self.afunami_button)  # pack_end
    funami_sync.set_margin_start(10)
    funami_sync.set_margin_end(10)
    hboxstack18.append(funami_sync)

    # jingk
    self.ajingk_button = Gtk.Switch()
    self.ajingk_button.connect("notify::active", self.on_mirror_jingk_repo_toggle)
    labeljingk = Gtk.Label(xalign=0)
    labeljingk.set_markup(
        "Enable Jingk repo - free bandwidth - Singapore - Jingk syncs twice per day"
    )
    jingk_sync = Gtk.Label(xalign=0)
    labeljingk.set_margin_start(10)
    labeljingk.set_margin_end(10)
    labeljingk.set_hexpand(True)
    hboxstack19.append(labeljingk)
    self.ajingk_button.set_margin_start(20)
    self.ajingk_button.set_margin_end(20)
    hboxstack19.append(self.ajingk_button)  # pack_end
    jingk_sync.set_margin_start(10)
    jingk_sync.set_margin_end(10)
    hboxstack19.append(jingk_sync)

    # accum
    self.aaccum_button = Gtk.Switch()
    self.aaccum_button.connect("notify::active", self.on_mirror_accum_repo_toggle)
    labelaaccum = Gtk.Label(xalign=0)
    labelaaccum.set_markup(
        "Enable Accum repo - free bandwidth - Sweden - Accum syncs twice per day"
    )
    accum_sync = Gtk.Label(xalign=0)
    labelaaccum.set_margin_start(10)
    labelaaccum.set_margin_end(10)
    labelaaccum.set_hexpand(True)
    hboxstack17.append(labelaaccum)
    self.aaccum_button.set_margin_start(20)
    self.aaccum_button.set_margin_end(20)
    hboxstack17.append(self.aaccum_button)  # pack_end
    accum_sync.set_margin_start(10)
    accum_sync.set_margin_end(10)
    hboxstack17.append(accum_sync)

    # github - always there as fallback - no extra large repo on github
    # self.agithub_button = Gtk.Switch()
    # self.agithub_button.connect("notify::active", self.on_mirror_github_repo_toggle)
    # label7 = Gtk.Label(xalign=0)
    # label7.set_markup("Enable Github repo - free bandwidth")
    # hboxstack9.pack_start(label7, False, True, 10)
    # hboxstack9.pack_end(self.agithub_button, False, False, 20)

    # aarnet
    self.aarnet_button = Gtk.Switch()
    self.aarnet_button.connect("notify::active", self.on_mirror_aarnet_repo_toggle)
    label8 = Gtk.Label(xalign=0)
    label8.set_markup(
        "Enable Aarnet repo - free bandwidth - Australia - Aarnet syncs daily"
    )
    aarnet_sync = Gtk.Label(xalign=0)
    # aarnet_sync.set_markup("     Aarnet syncs once per day")
    label8.set_margin_start(10)
    label8.set_margin_end(10)
    label8.set_hexpand(True)
    hboxstack10.append(label8)
    self.aarnet_button.set_margin_start(20)
    self.aarnet_button.set_margin_end(20)
    hboxstack10.append(self.aarnet_button)  # pack_end
    aarnet_sync.set_margin_start(10)
    aarnet_sync.set_margin_end(10)
    hboxstack10.append(aarnet_sync)

    warning = Gtk.Label(xalign=0)
    warning.set_markup(
        "There is just one source - github.com"
    )
    warning2 = Gtk.Label(xalign=0)
    warning2.set_markup("Your mirrorlist has been updated to reflect this")
    warning.set_margin_start(10)
    warning.set_margin_end(10)
    hboxstack11.append(warning)
    warning2.set_margin_start(10)
    warning2.set_margin_end(10)
    hboxstack12.append(warning2)

    frame4 = Gtk.Frame(label="")
    frame4.set_margin_top(10)
    frame4lbl = frame4.get_label_widget()
    frame4lbl.set_markup("<b>Other mirrorlists</b>")

    pace_label = Gtk.Label(xalign=0)
    pace_label.set_margin_top(0)
    pace_label.set_markup(
        "We use the <b>pace</b> application to set the mirrors of other \
repositories.\nYou save the settings in pace by clicking on preview and save. \
Pace will change the orginal layout."
    )
    launch_pace_btn = Gtk.Button(label="Install/launch pace")
    launch_pace_btn.connect("clicked", self.on_click_launch_pace)

    pace_label.set_margin_start(10)
    pace_label.set_margin_end(10)
    hboxstack15.append(pace_label)
    launch_pace_btn.set_margin_start(10)
    launch_pace_btn.set_margin_end(10)
    hboxstack15.append(launch_pace_btn)

    # ========================================================
    #               FOOTER
    # ========================================================

    reset_mirror = Gtk.Button(label="Reset ArcoLinux Mirrorlist")
    reset_mirror.connect("clicked", self.on_click_reset_arcolinux_mirrorlist)
    hboxstack4.append(reset_mirror)  # pack_end

    # ========================================================
    #               VBOX - FRAME
    # ========================================================

    vbox3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    # message
    #vbox3.pack_start(hboxstack11, False, False, 0)
    #vbox3.pack_start(hboxstack12, False, False, 0)
    # gitlab
    #vbox3.pack_start(hboxstack16, False, False, 0)
    # sweden
    #vbox3.pack_start(hboxstack17, False, False, 0)
    # belnet
    #vbox3.pack_start(hboxstack14, False, False, 0)
    # aarnet
    #vbox3.pack_start(hboxstack10, False, False, 0)
    # funami
    # vbox3.pack_start(hboxstack18, False, False, 0)
    # jingk
    # vbox3.pack_start(hboxstack19, False, False, 0)
    # seedhost
    vbox3.append(hboxstack7)

    frame3.set_child(vbox3)

    vbox4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    # message
    #vbox4.pack_start(hboxstack15, False, False, 0)
    #frame4.set_child(vbox4)

    # ========================================================
    #               PACK TO WINDOW
    # ========================================================

    vboxstack1.append(hbox3)
    #vboxstack1.pack_start(hbox4, False, False, 0)
    frame3.set_margin_start(10)
    frame3.set_margin_end(10)
    vboxstack1.append(frame3)
    #vboxstack1.pack_start(frame4, False, False, 10)
    #vboxstack1.pack_end(hboxstack4, False, False, 0)
