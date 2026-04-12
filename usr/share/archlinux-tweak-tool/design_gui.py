# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0103,


def gui(self, Gtk, vboxstack24, design, fn):
    """create a gui"""
    hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    lbl1 = Gtk.Label(xalign=0)
    lbl1.set_text("Design")
    lbl1.set_name("title")
    hbox3.append(lbl1)

    hbox4 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    hseparator.set_hexpand(True)
    hseparator.set_vexpand(False)
    hbox4.append(hseparator)

    # ==========================================================
    #                     DESIGN
    # ==========================================================

    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

    vboxstack1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    vboxstack4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

    stack = Gtk.Stack()
    stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
    stack.set_transition_duration(350)
    stack.set_hhomogeneous(False)
    stack.set_vhomogeneous(False)

    stack_switcher = Gtk.StackSwitcher()
    stack_switcher.set_orientation(Gtk.Orientation.HORIZONTAL)
    stack_switcher.set_stack(stack)

    # ==================================================================
    #                       THEMES TAB
    # ==================================================================

    hbox10 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox10_label = Gtk.Label(xalign=0)
    hbox10_label.set_text(
        "Select the packages you want to install or remove, then click the appropriate button."
    )
    hbox10_label.set_margin_start(10)
    hbox10_label.set_margin_end(10)
    hbox10.append(hbox10_label)

    hbox12 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    self.adapta_gtk_theme = Gtk.CheckButton(label="adapta-gtk-theme")
    self.arc_darkest_theme_git = Gtk.CheckButton(label="arc-darkest-theme-git")
    self.arc_gtk_theme = Gtk.CheckButton(label="arc-gtk-theme")
    self.arcolinux_arc_kde = Gtk.CheckButton(label="arcolinux-arc-kde")
    self.arcolinux_sweet_mars_git = Gtk.CheckButton(label="arcolinux-sweet-mars-git")
    self.ayu_theme = Gtk.CheckButton(label="ayu-theme")
    self.breeze = Gtk.CheckButton(label="breeze")
    self.dracula_gtk_theme = Gtk.CheckButton(label="dracula-gtk-theme")
    self.fluent_gtk_theme = Gtk.CheckButton(label="fluent-gtk-theme")
    self.fluent_kde_theme_git = Gtk.CheckButton(label="fluent-kde-theme-git")
    self.graphite_gtk_theme_git = Gtk.CheckButton(label="graphite-gtk-theme_git")
    self.kripton_theme_git = Gtk.CheckButton(label="kripton-theme-git")
    self.kvantum_theme_materia = Gtk.CheckButton(label="kvantum-theme-materia")
    self.kvantum_theme_qogir_git = Gtk.CheckButton(label="kvantum-theme-qogir-git")
    self.layan_gtk_theme_git = Gtk.CheckButton(label="layan-gtk-theme-git")
    self.layan_kde_git = Gtk.CheckButton(label="layan-kde-git")
    self.materia_gtk_theme = Gtk.CheckButton(label="materia-gtk-theme")
    self.materia_kde = Gtk.CheckButton(label="materia-kde")
    self.numix_gtk_theme_git = Gtk.CheckButton(label="numix-gtk-theme-git")
    self.openbox_themes_pambudi_git = Gtk.CheckButton(
        label="openbox-themes-pambudi-git"
    )
    self.orchis_kde_theme_git = Gtk.CheckButton(label="orchis-kde-theme-git")
    self.orchis_theme_git = Gtk.CheckButton(label="orchis-theme-git")
    self.qogir_gtk_theme_git = Gtk.CheckButton(label="qogir-gtk-theme-git")
    self.sweet_theme_git = Gtk.CheckButton(label="sweet-theme-git")
    self.sweet_gtk_theme_dark = Gtk.CheckButton(label="sweet-gtk-theme-dark")

    flowbox_themes = Gtk.FlowBox()
    flowbox_themes.set_valign(Gtk.Align.START)
    flowbox_themes.set_max_children_per_line(10)
    flowbox_themes.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox_themes.append(self.adapta_gtk_theme)
    flowbox_themes.append(self.arc_darkest_theme_git)
    flowbox_themes.append(self.arc_gtk_theme)
    flowbox_themes.append(self.arcolinux_arc_kde)
    flowbox_themes.append(self.arcolinux_sweet_mars_git)
    flowbox_themes.append(self.ayu_theme)
    flowbox_themes.append(self.breeze)
    flowbox_themes.append(self.dracula_gtk_theme)
    flowbox_themes.append(self.fluent_gtk_theme)
    flowbox_themes.append(self.fluent_kde_theme_git)
    flowbox_themes.append(self.graphite_gtk_theme_git)
    flowbox_themes.append(self.kripton_theme_git)
    flowbox_themes.append(self.kvantum_theme_materia)
    flowbox_themes.append(self.kvantum_theme_qogir_git)
    flowbox_themes.append(self.layan_gtk_theme_git)
    flowbox_themes.append(self.layan_kde_git)
    flowbox_themes.append(self.materia_gtk_theme)
    flowbox_themes.append(self.materia_kde)
    flowbox_themes.append(self.numix_gtk_theme_git)
    flowbox_themes.append(self.openbox_themes_pambudi_git)
    flowbox_themes.append(self.orchis_kde_theme_git)
    flowbox_themes.append(self.orchis_theme_git)
    flowbox_themes.append(self.qogir_gtk_theme_git)
    flowbox_themes.append(self.sweet_theme_git)
    flowbox_themes.append(self.sweet_gtk_theme_dark)

    flowbox_themes.set_hexpand(True)
    flowbox_themes.set_vexpand(True)
    flowbox_themes.set_margin_start(10)
    flowbox_themes.set_margin_end(10)
    hbox12.append(flowbox_themes)

    hbox13 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    label13 = Gtk.Label()
    label13.set_text("Choose what to select with a button")
    btn_all_selection = Gtk.Button(label="All")
    btn_all_selection.connect("clicked", self.on_click_theming_all_selection)
    btn_normal_selection = Gtk.Button(label="Normal")
    btn_normal_selection.connect("clicked", self.on_click_theming_normal_selection)
    btn_small_selection = Gtk.Button(label="Minimal")
    btn_small_selection.connect("clicked", self.on_click_theming_minimal_selection)
    btn_none_selection = Gtk.Button(label="None")
    btn_none_selection.connect("clicked", self.on_click_theming_none_selection)
    label13.set_margin_start(10)
    label13.set_margin_end(10)
    label13.set_hexpand(True)
    hbox13.append(label13)
    btn_all_selection.set_margin_start(10)
    btn_all_selection.set_margin_end(10)
    hbox13.append(btn_all_selection)  # pack_end
    btn_normal_selection.set_margin_start(10)
    btn_normal_selection.set_margin_end(10)
    hbox13.append(btn_normal_selection)  # pack_end
    btn_small_selection.set_margin_start(10)
    btn_small_selection.set_margin_end(10)
    hbox13.append(btn_small_selection)  # pack_end
    btn_none_selection.set_margin_start(10)
    btn_none_selection.set_margin_end(10)
    hbox13.append(btn_none_selection)  # pack_end

    # at bottom
    hbox19 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_install_themes = Gtk.Button(label="Install the selected themes")
    button_install_themes.connect("clicked", self.on_install_themes_clicked)
    button_find_themes = Gtk.Button(label="Show the installed themes")
    button_find_themes.connect("clicked", self.on_find_themes_clicked)
    button_remove_themes = Gtk.Button(label="Uninstall the selected themes")
    button_remove_themes.connect("clicked", self.on_remove_themes_clicked)

    button_remove_themes.set_margin_start(10)
    button_remove_themes.set_margin_end(10)
    button_remove_themes.set_hexpand(True)
    hbox19.append(button_remove_themes)
    button_find_themes.set_margin_start(10)
    button_find_themes.set_margin_end(10)
    hbox19.append(button_find_themes)
    button_install_themes.set_margin_start(10)
    button_install_themes.set_margin_end(10)
    hbox19.append(button_install_themes)  # pack_end

    # ==================================================================
    #                       ICONS TAB
    # ==================================================================

    hbox20 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox20_label = Gtk.Label(xalign=0)
    hbox20_label.set_text(
        "Select the packages you want to install or remove, then click the appropriate button."
    )
    hbox20_label.set_margin_start(10)
    hbox20_label.set_margin_end(10)
    hbox20.append(hbox20_label)

    hbox21 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    self.arc_icon_theme = Gtk.CheckButton(label="arc-icon-theme")
    self.breeze_icons = Gtk.CheckButton(label="breeze-icons")
    self.dracula_icons_git = Gtk.CheckButton(label="dracula-icons-git")
    self.faba_icon_theme_git = Gtk.CheckButton(label="faba-icon-theme-git")
    self.faba_mono_icons_git = Gtk.CheckButton(label="faba-mono-icons-git")
    self.flat_remix_git = Gtk.CheckButton(label="flat-remix-git")
    self.fluent_icon_theme_git = Gtk.CheckButton(label="fluent-icon-theme-git")
    self.halo_icons_git = Gtk.CheckButton(label="halo-icons-git")
    self.la_capitaine_icon_theme_git = Gtk.CheckButton(
        label="la-capitaine-icon-theme-git"
    )
    self.luna_icon_theme_git = Gtk.CheckButton(label="luna-icon-theme-git")
    self.moka_icon_theme_git = Gtk.CheckButton(label="moka-icon-theme-git")
    self.nordzy_icon_theme_git = Gtk.CheckButton(label="nordzy-icon-theme-git")
    self.numix_circle_arc_icons_git = Gtk.CheckButton(
        label="numix-circle-arc-icons-git"
    )
    self.numix_circle_icon_theme_git = Gtk.CheckButton(
        label="numix-circle-icon-theme-git"
    )
    self.obsidian_icon_theme = Gtk.CheckButton(label="obsidian-icon-theme")
    self.oranchelo_icon_theme_git = Gtk.CheckButton(label="oranchelo-icon-theme-git")
    self.paper_icon_theme = Gtk.CheckButton(label="paper-icon-theme")
    self.papirus_folders_git = Gtk.CheckButton(label="papirus-folders-git")
    self.papirus_folders_gui_bin = Gtk.CheckButton(label="papirus-folders-gui-bin")
    self.papirus_folders_nordic = Gtk.CheckButton(label="papirus-folders-nordic")
    self.papirus_icon_theme = Gtk.CheckButton(label="papirus-icon-theme")
    self.papirus_nord = Gtk.CheckButton(label="papirus-nord")
    self.qogir_icon_theme = Gtk.CheckButton(label="qogir-icon-theme")
    self.tela_circle_icon_theme_git = Gtk.CheckButton(
        label="tela-circle-icon-theme-git"
    )
    self.vimix_icon_theme_git = Gtk.CheckButton(label="vimix-icon-theme-git")
    self.we10x_icon_theme_git = Gtk.CheckButton(label="we10x-icon-theme-git")
    self.whitesur_icon_theme_git = Gtk.CheckButton(label="whitesur-icon-theme-git")
    self.zafiro_icon_theme = Gtk.CheckButton(label="zafiro-icon-theme")

    flowbox_icons = Gtk.FlowBox()
    flowbox_icons.set_valign(Gtk.Align.START)
    flowbox_icons.set_max_children_per_line(10)
    flowbox_icons.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox_icons.append(self.arc_icon_theme)
    flowbox_icons.append(self.breeze_icons)
    flowbox_icons.append(self.dracula_icons_git)
    flowbox_icons.append(self.faba_icon_theme_git)
    flowbox_icons.append(self.faba_mono_icons_git)
    flowbox_icons.append(self.flat_remix_git)
    flowbox_icons.append(self.fluent_icon_theme_git)
    flowbox_icons.append(self.halo_icons_git)
    flowbox_icons.append(self.la_capitaine_icon_theme_git)
    flowbox_icons.append(self.luna_icon_theme_git)
    flowbox_icons.append(self.moka_icon_theme_git)
    flowbox_icons.append(self.nordzy_icon_theme_git)
    flowbox_icons.append(self.numix_circle_arc_icons_git)
    flowbox_icons.append(self.numix_circle_icon_theme_git)
    flowbox_icons.append(self.obsidian_icon_theme)
    flowbox_icons.append(self.oranchelo_icon_theme_git)
    flowbox_icons.append(self.paper_icon_theme)
    flowbox_icons.append(self.papirus_folders_git)
    flowbox_icons.append(self.papirus_folders_gui_bin)
    flowbox_icons.append(self.papirus_folders_nordic)
    flowbox_icons.append(self.papirus_icon_theme)
    flowbox_icons.append(self.papirus_nord)
    flowbox_icons.append(self.qogir_icon_theme)
    flowbox_icons.append(self.tela_circle_icon_theme_git)
    flowbox_icons.append(self.vimix_icon_theme_git)
    flowbox_icons.append(self.we10x_icon_theme_git)
    flowbox_icons.append(self.whitesur_icon_theme_git)
    flowbox_icons.append(self.zafiro_icon_theme)

    flowbox_icons.set_hexpand(True)
    flowbox_icons.set_vexpand(True)
    flowbox_icons.set_margin_start(10)
    flowbox_icons.set_margin_end(10)
    hbox21.append(flowbox_icons)

    hbox22 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    label13 = Gtk.Label()
    label13.set_text("Choose what to select with a button")
    btn_all_selection = Gtk.Button(label="All")
    btn_all_selection.connect("clicked", self.on_click_icon_theming_all_selection)
    btn_normal_selection = Gtk.Button(label="Normal")
    btn_normal_selection.connect("clicked", self.on_click_icon_theming_normal_selection)
    btn_small_selection = Gtk.Button(label="Minimal")
    btn_small_selection.connect("clicked", self.on_click_icon_theming_minimal_selection)
    btn_none_selection = Gtk.Button(label="None")
    btn_none_selection.connect("clicked", self.on_click_icon_theming_none_selection)
    label13.set_margin_start(10)
    label13.set_margin_end(10)
    label13.set_hexpand(True)
    hbox22.append(label13)
    btn_all_selection.set_margin_start(10)
    btn_all_selection.set_margin_end(10)
    hbox22.append(btn_all_selection)  # pack_end
    btn_normal_selection.set_margin_start(10)
    btn_normal_selection.set_margin_end(10)
    hbox22.append(btn_normal_selection)  # pack_end
    btn_small_selection.set_margin_start(10)
    btn_small_selection.set_margin_end(10)
    hbox22.append(btn_small_selection)  # pack_end
    btn_none_selection.set_margin_start(10)
    btn_none_selection.set_margin_end(10)
    hbox22.append(btn_none_selection)  # pack_end

    hbox29 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_install_themes = Gtk.Button(label="Install the selected icon themes")
    button_install_themes.connect("clicked", self.on_install_icon_themes_clicked)
    button_find_themes = Gtk.Button(label="Show the installed icon themes")
    button_find_themes.connect("clicked", self.on_find_icon_themes_clicked)
    button_remove_themes = Gtk.Button(label="Uninstall the selected icon themes")
    button_remove_themes.connect("clicked", self.on_remove_icon_themes_clicked)
    button_remove_themes.set_margin_start(10)
    button_remove_themes.set_margin_end(10)
    button_remove_themes.set_hexpand(True)
    hbox29.append(button_remove_themes)
    button_find_themes.set_margin_start(10)
    button_find_themes.set_margin_end(10)
    hbox29.append(button_find_themes)
    button_install_themes.set_margin_start(10)
    button_install_themes.set_margin_end(10)
    hbox29.append(button_install_themes)  # pack_end

    # ==================================================================
    #                       CURSORS TAB
    # ==================================================================

    hbox30 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox30_label = Gtk.Label(xalign=0)
    hbox30_label.set_text(
        "Select the packages you want to install or remove, then click the appropriate button.\n\
Icon themes provide cursors too"
    )
    hbox30_label.set_margin_start(10)
    hbox30_label.set_margin_end(10)
    hbox30.append(hbox30_label)

    hbox31 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    self.bibata_cursor_theme_bin = Gtk.CheckButton(label="bibata-cursor-theme-bin")
    self.bibata_cursor_translucent = Gtk.CheckButton(label="bibata-cursor-translucent")
    self.bibata_extra_cursor_theme = Gtk.CheckButton(label="bibata-extra-cursor-theme")
    self.bibata_rainbow_cursor_theme = Gtk.CheckButton(
        label="bibata-rainbow-cursor-theme"
    )
    self.capitaine_cursors = Gtk.CheckButton(label="capitaine-cursors")
    self.catppuccin_cursors_git = Gtk.CheckButton(label="catppuccin-cursors-git")
    self.dracula_cursors_git = Gtk.CheckButton(label="dracula-cursors-git")
    self.layan_cursor_theme_git = Gtk.CheckButton(label="layan-cursor-theme-git")
    self.oxy_neon = Gtk.CheckButton(label="oxy-neon")
    self.sweet_cursor_theme_git = Gtk.CheckButton(label="sweet-cursor-theme-git")
    self.vimix_cursors = Gtk.CheckButton(label="vimix-cursors")
    self.xcursor_arch_cursor_complete = Gtk.CheckButton(
        label="xcursor-arch-cursor-complete"
    )
    self.xcursor_breeze = Gtk.CheckButton(label="xcursor-breeze")
    self.xcursor_comix = Gtk.CheckButton(label="xcursor-comix")
    self.xcursor_flatbed = Gtk.CheckButton(label="xcursor-flatbed")
    self.xcursor_neutral = Gtk.CheckButton(label="xcursor-neutral")
    self.xcursor_premium = Gtk.CheckButton(label="xcursor-premium")
    self.xcursor_simpleandsoft = Gtk.CheckButton(label="xcursor-simpleandsoft")

    flowbox_cursor = Gtk.FlowBox()
    flowbox_cursor.set_valign(Gtk.Align.START)
    flowbox_cursor.set_max_children_per_line(10)
    flowbox_cursor.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox_cursor.append(self.bibata_cursor_theme_bin)
    flowbox_cursor.append(self.bibata_cursor_translucent)
    flowbox_cursor.append(self.bibata_extra_cursor_theme)
    flowbox_cursor.append(self.bibata_rainbow_cursor_theme)
    flowbox_cursor.append(self.capitaine_cursors)
    flowbox_cursor.append(self.catppuccin_cursors_git)
    flowbox_cursor.append(self.dracula_cursors_git)
    flowbox_cursor.append(self.layan_cursor_theme_git)
    flowbox_cursor.append(self.oxy_neon)
    flowbox_cursor.append(self.sweet_cursor_theme_git)
    flowbox_cursor.append(self.vimix_cursors)
    flowbox_cursor.append(self.xcursor_arch_cursor_complete)
    flowbox_cursor.append(self.xcursor_breeze)
    flowbox_cursor.append(self.xcursor_comix)
    flowbox_cursor.append(self.xcursor_flatbed)
    flowbox_cursor.append(self.xcursor_neutral)
    flowbox_cursor.append(self.xcursor_premium)
    flowbox_cursor.append(self.xcursor_simpleandsoft)

    flowbox_cursor.set_hexpand(True)
    flowbox_cursor.set_vexpand(True)
    flowbox_cursor.set_margin_start(10)
    flowbox_cursor.set_margin_end(10)
    hbox31.append(flowbox_cursor)

    hbox32 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    label32 = Gtk.Label()
    label32.set_text("Choose what to select with a button")
    btn_all_selection_cursors = Gtk.Button(label="All")
    btn_all_selection_cursors.connect(
        "clicked", self.on_click_cursor_theming_all_selection
    )
    btn_normal_selection_cursors = Gtk.Button(label="Normal")
    btn_normal_selection_cursors.connect(
        "clicked", self.on_click_cursor_theming_normal_selection
    )
    btn_small_selection_cursors = Gtk.Button(label="Minimal")
    btn_small_selection_cursors.connect(
        "clicked", self.on_click_cursor_theming_minimal_selection
    )
    btn_none_selection_cursors = Gtk.Button(label="None")
    btn_none_selection_cursors.connect(
        "clicked", self.on_click_cursor_theming_none_selection
    )
    label32.set_margin_start(10)
    label32.set_margin_end(10)
    label32.set_hexpand(True)
    hbox32.append(label32)
    btn_all_selection_cursors.set_margin_start(10)
    btn_all_selection_cursors.set_margin_end(10)
    hbox32.append(btn_all_selection_cursors)  # pack_end
    btn_normal_selection_cursors.set_margin_start(10)
    btn_normal_selection_cursors.set_margin_end(10)
    hbox32.append(btn_normal_selection_cursors)  # pack_end
    btn_small_selection_cursors.set_margin_start(10)
    btn_small_selection_cursors.set_margin_end(10)
    hbox32.append(btn_small_selection_cursors)  # pack_end
    btn_none_selection_cursors.set_margin_start(10)
    btn_none_selection_cursors.set_margin_end(10)
    hbox32.append(btn_none_selection_cursors)  # pack_end

    hbox39 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_install_cursors = Gtk.Button(label="Install the selected cursor themes")
    button_install_cursors.connect("clicked", self.on_install_cursor_themes_clicked)
    button_find_cursors = Gtk.Button(label="Show the installed cursor themes")
    button_find_cursors.connect("clicked", self.on_find_cursor_themes_clicked)
    button_remove_cursors = Gtk.Button(label="Uninstall the selected cursor themes")
    button_remove_cursors.connect("clicked", self.on_remove_cursor_themes_clicked)
    button_remove_cursors.set_margin_start(10)
    button_remove_cursors.set_margin_end(10)
    button_remove_cursors.set_hexpand(True)
    hbox39.append(button_remove_cursors)
    button_find_cursors.set_margin_start(10)
    button_find_cursors.set_margin_end(10)
    hbox39.append(button_find_cursors)
    button_install_cursors.set_margin_start(10)
    button_install_cursors.set_margin_end(10)
    hbox39.append(button_install_cursors)  # pack_end

    # ==================================================================
    #                       FONTS TAB
    # ==================================================================

    hbox40 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    hbox40_label = Gtk.Label(xalign=0)
    hbox40_label.set_text(
        "Select the packages you want to install or remove, then click the appropriate button."
    )
    hbox40_label.set_margin_start(10)
    hbox40_label.set_margin_end(10)
    hbox40.append(hbox40_label)

    hbox41 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

    self.adobe_source_sans_fonts = Gtk.CheckButton(label="adobe-source-sans-fonts")
    self.awesome_terminal_fonts = Gtk.CheckButton(label="awesome-terminal-fonts")
    self.nerd_fonts_source_code_pro = Gtk.CheckButton(
        label="nerd-fonts-source-code-pro"
    )
    self.noto_fonts = Gtk.CheckButton(label="noto-fonts")
    self.ttf_anonymous_pro = Gtk.CheckButton(label="ttf-anonymous-pro")
    self.ttf_bitstream_vera = Gtk.CheckButton(label="ttf-bitstream-vera")
    self.ttf_caladea = Gtk.CheckButton(label="ttf-caladea")
    self.ttf_carlito = Gtk.CheckButton(label="ttf-carlito")
    self.ttf_cascadia_code = Gtk.CheckButton(label="ttf-cascadia-code")
    self.ttf_cormorant = Gtk.CheckButton(label="ttf-cormorant")
    self.ttf_croscore = Gtk.CheckButton(label="ttf-croscore")
    self.ttf_dejavu = Gtk.CheckButton(label="ttf-dejavu")
    self.ttf_droid = Gtk.CheckButton(label="ttf-droid")
    self.ttf_eurof = Gtk.CheckButton(label="ttf-eurof")
    self.ttf_fantasque_sans_mono = Gtk.CheckButton(label="ttf-fantasque-sans-mono")
    self.ttf_fira_code = Gtk.CheckButton(label="ttf-fira-code")
    self.ttf_fira_mono = Gtk.CheckButton(label="ttf-fira-mono")
    self.ttf_fira_sans = Gtk.CheckButton(label="ttf-fira-sans")
    self.ttf_font_awesome = Gtk.CheckButton(label="ttf-font-awesome")
    self.ttf_hack = Gtk.CheckButton(label="ttf-hack")
    self.ttf_hactor = Gtk.CheckButton(label="ttf-hactor")
    self.ttf_hellvetica = Gtk.CheckButton(label="ttf-hellvetica")
    self.ttf_ibm_plex = Gtk.CheckButton(label="ttf-ibm-plex")
    self.ttf_inconsolata = Gtk.CheckButton(label="ttf-inconsolata")
    self.ttf_iosevka_nerd = Gtk.CheckButton(label="ttf-iosevka-nerd")
    self.ttf_jetbrains_mono = Gtk.CheckButton(label="ttf-jetbrains-mono")
    self.ttf_joypixels = Gtk.CheckButton(label="ttf-joypixels")
    self.ttf_lato = Gtk.CheckButton(label="ttf-lato")
    self.ttf_liberation = Gtk.CheckButton(label="ttf-liberation")
    self.ttf_linux_libertine = Gtk.CheckButton(label="ttf-linux-libertine")
    self.ttf_linux_libertine_g = Gtk.CheckButton(label="ttf-linux-libertine-g")
    self.ttf_material_design_iconic_font = Gtk.CheckButton(
        label="ttf-material-design-iconic-font"
    )
    self.ttf_meslo_nerd_font_powerlevel10k = Gtk.CheckButton(
        label="ttf-meslo-nerd-font-powerlevel10k"
    )
    self.ttf_monofur = Gtk.CheckButton(label="ttf-monofur")
    self.ttf_ms_fonts = Gtk.CheckButton(label="ttf-ms-fonts")
    self.ttf_nerd_fonts_symbols = Gtk.CheckButton(label="ttf-nerd-fonts-symbols")
    self.ttf_nerd_fonts_symbols_mono = Gtk.CheckButton(
        label="ttf-nerd-fonts-symbols-mono"
    )
    self.ttf_opensans = Gtk.CheckButton(label="ttf-opensans")
    self.ttf_proggy_clean = Gtk.CheckButton(label="ttf-proggy-clean")
    self.ttf_roboto = Gtk.CheckButton(label="ttf-roboto")
    self.ttf_roboto_mono = Gtk.CheckButton(label="ttf-roboto-mono")
    self.ttf_ubuntu_font_family = Gtk.CheckButton(label="ttf-ubuntu-font-family")

    flowbox_font = Gtk.FlowBox()
    flowbox_font.set_valign(Gtk.Align.START)
    flowbox_font.set_max_children_per_line(10)
    flowbox_font.set_selection_mode(Gtk.SelectionMode.NONE)

    flowbox_font.append(self.adobe_source_sans_fonts)
    flowbox_font.append(self.awesome_terminal_fonts)
    flowbox_font.append(self.nerd_fonts_source_code_pro)
    flowbox_font.append(self.noto_fonts)
    flowbox_font.append(self.ttf_anonymous_pro)
    flowbox_font.append(self.ttf_bitstream_vera)
    flowbox_font.append(self.ttf_caladea)
    flowbox_font.append(self.ttf_carlito)
    flowbox_font.append(self.ttf_cascadia_code)
    flowbox_font.append(self.ttf_cormorant)
    flowbox_font.append(self.ttf_croscore)
    flowbox_font.append(self.ttf_dejavu)
    flowbox_font.append(self.ttf_droid)
    flowbox_font.append(self.ttf_eurof)
    flowbox_font.append(self.ttf_fantasque_sans_mono)
    flowbox_font.append(self.ttf_fira_code)
    flowbox_font.append(self.ttf_fira_mono)
    flowbox_font.append(self.ttf_fira_sans)
    flowbox_font.append(self.ttf_font_awesome)
    flowbox_font.append(self.ttf_hack)
    flowbox_font.append(self.ttf_hactor)
    flowbox_font.append(self.ttf_hellvetica)
    flowbox_font.append(self.ttf_ibm_plex)
    flowbox_font.append(self.ttf_inconsolata)
    flowbox_font.append(self.ttf_iosevka_nerd)
    flowbox_font.append(self.ttf_jetbrains_mono)
    flowbox_font.append(self.ttf_joypixels)
    flowbox_font.append(self.ttf_lato)
    flowbox_font.append(self.ttf_liberation)
    flowbox_font.append(self.ttf_linux_libertine)
    flowbox_font.append(self.ttf_linux_libertine_g)
    flowbox_font.append(self.ttf_material_design_iconic_font)
    flowbox_font.append(self.ttf_meslo_nerd_font_powerlevel10k)
    flowbox_font.append(self.ttf_monofur)
    flowbox_font.append(self.ttf_ms_fonts)
    flowbox_font.append(self.ttf_nerd_fonts_symbols)
    flowbox_font.append(self.ttf_nerd_fonts_symbols_mono)
    flowbox_font.append(self.ttf_opensans)
    flowbox_font.append(self.ttf_proggy_clean)
    flowbox_font.append(self.ttf_roboto)
    flowbox_font.append(self.ttf_roboto_mono)
    flowbox_font.append(self.ttf_ubuntu_font_family)

    flowbox_font.set_hexpand(True)
    flowbox_font.set_vexpand(True)
    flowbox_font.set_margin_start(10)
    flowbox_font.set_margin_end(10)
    hbox41.append(flowbox_font)

    hbox42 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
    lbl_hbox42 = Gtk.Label()
    lbl_hbox42.set_text("Choose what to select with a button")
    btn_all_selection_fonts = Gtk.Button(label="All")
    btn_all_selection_fonts.connect("clicked", self.on_click_font_theming_all_selection)
    btn_normal_selection_fonts = Gtk.Button(label="Normal")
    btn_normal_selection_fonts.connect(
        "clicked", self.on_click_font_theming_normal_selection
    )
    btn_small_selection_fonts = Gtk.Button(label="Minimal")
    btn_small_selection_fonts.connect(
        "clicked", self.on_click_font_theming_minimal_selection
    )
    btn_none_selection_fonts = Gtk.Button(label="None")
    btn_none_selection_fonts.connect(
        "clicked", self.on_click_font_theming_none_selection
    )
    lbl_hbox42.set_margin_start(10)
    lbl_hbox42.set_margin_end(10)
    lbl_hbox42.set_hexpand(True)
    hbox42.append(lbl_hbox42)
    btn_all_selection_fonts.set_margin_start(10)
    btn_all_selection_fonts.set_margin_end(10)
    hbox42.append(btn_all_selection_fonts)  # pack_end
    btn_normal_selection_fonts.set_margin_start(10)
    btn_normal_selection_fonts.set_margin_end(10)
    hbox42.append(btn_normal_selection_fonts)  # pack_end
    btn_small_selection_fonts.set_margin_start(10)
    btn_small_selection_fonts.set_margin_end(10)
    hbox42.append(btn_small_selection_fonts)  # pack_end
    btn_none_selection_fonts.set_margin_start(10)
    btn_none_selection_fonts.set_margin_end(10)
    hbox42.append(btn_none_selection_fonts)  # pack_end

    hbox49 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
    button_install_fonts = Gtk.Button(label="Install the selected fonts")
    button_install_fonts.connect("clicked", self.on_install_fonts_clicked)
    button_find_fonts = Gtk.Button(label="Show the installed fonts")
    button_find_fonts.connect("clicked", self.on_find_fonts_clicked)
    button_remove_fonts = Gtk.Button(label="Uninstall the selected fonts")
    button_remove_fonts.connect("clicked", self.on_remove_fonts_clicked)
    button_remove_fonts.set_margin_start(10)
    button_remove_fonts.set_margin_end(10)
    button_remove_fonts.set_hexpand(True)
    hbox49.append(button_remove_fonts)
    button_find_fonts.set_margin_start(10)
    button_find_fonts.set_margin_end(10)
    hbox49.append(button_find_fonts)
    button_install_fonts.set_margin_start(10)
    button_install_fonts.set_margin_end(10)
    hbox49.append(button_install_fonts)  # pack_end

    # ====================================================================
    #                       STACK
    # ====================================================================

    # themes
    hbox10.set_margin_start(10)
    hbox10.set_margin_end(10)
    vboxstack1.append(hbox10)
    hbox12.set_margin_start(10)
    hbox12.set_margin_end(10)
    vboxstack1.append(hbox12)
    hbox13.set_margin_start(10)
    hbox13.set_margin_end(10)
    vboxstack1.append(hbox13)
    vboxstack1.append(hbox19)

    # icons
    hbox20.set_margin_start(10)
    hbox20.set_margin_end(10)
    vboxstack2.append(hbox20)
    hbox21.set_margin_start(10)
    hbox21.set_margin_end(10)
    vboxstack2.append(hbox21)
    hbox22.set_margin_start(10)
    hbox22.set_margin_end(10)
    vboxstack2.append(hbox22)
    vboxstack2.append(hbox29)

    # cursors
    hbox30.set_margin_start(10)
    hbox30.set_margin_end(10)
    vboxstack3.append(hbox30)
    hbox31.set_margin_start(10)
    hbox31.set_margin_end(10)
    vboxstack3.append(hbox31)
    hbox32.set_margin_start(10)
    hbox32.set_margin_end(10)
    vboxstack3.append(hbox32)
    vboxstack3.append(hbox39)

    # fonts
    hbox40.set_margin_start(10)
    hbox40.set_margin_end(10)
    vboxstack4.append(hbox40)
    hbox41.set_margin_start(10)
    hbox41.set_margin_end(10)
    vboxstack4.append(hbox41)
    hbox42.set_margin_start(10)
    hbox42.set_margin_end(10)
    vboxstack4.append(hbox42)
    vboxstack4.append(hbox49)

    # ==================================================================
    #                       PACK TO STACK
    # ==================================================================
    stack.add_titled(vboxstack1, "stack1", "Themes")
    stack.add_titled(vboxstack2, "stack2", "Icons")
    stack.add_titled(vboxstack3, "stack3", "Cursors")
    stack.add_titled(vboxstack4, "stack4", "Fonts")

    vbox.append(stack_switcher)
    stack.set_hexpand(True)
    stack.set_vexpand(True)
    vbox.append(stack)

    vboxstack24.append(hbox3)
    vboxstack24.append(hbox4)
    vbox.set_hexpand(True)
    vbox.set_vexpand(True)
    vboxstack24.append(vbox)
