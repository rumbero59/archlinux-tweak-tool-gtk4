# Alacritty Tweak Tool — Roadmap

## Done

- [x] Three-tab GTK4 app (Themes / Appearance / Advanced)
- [x] 231 themes from alacritty-themes npm package + 12 bundled fallback
- [x] Color swatches via Cairo DrawingArea per theme row
- [x] Source dropdown splits themes by origin (alacritty-themes · 231 / Bundled · 12)
- [x] Live search bar filters theme list by name
- [x] Preview: launches `alacritty --config-file /tmp/...` running fastfetch inside
- [x] Apply: writes colors with tomlkit (preserves comments including ohmychadwm marker)
- [x] Backup to alacritty.toml-bak before every write
- [x] Appearance tab: reads current config on launch, pre-populates all controls
- [x] Font family: searchable text entry — type to filter mono fonts, click row to select
- [x] Font size: SpinButton pre-filled from current config
- [x] Window opacity: Scale pre-filled from current config
- [x] Advanced tab: reads current config on launch, pre-populates all controls
- [x] Scrollback: SpinButton 0–999999 (0 disables; no true unlimited in Alacritty)
- [x] Cursor shape + blink: DropDown + Switch pre-filled from current config
- [x] HeaderBar with Quit button top-right

## Next — immediate

- [ ] **VTE embedded terminal in Themes tab**: replace separate alacritty preview window
      with a VTE widget inside the right panel; colors update live on selection,
      fastfetch runs inside it; VTE 2.91 confirmed installed
- [ ] **Copy 231 themes into data/themes/**: 936 KB, makes app independent of npm package;
      update SYSTEM_THEMES_DIR fallback logic accordingly

## Next — roadmap

- [ ] **Option C — Full category UI**: source tabs each with Dark/Light toggle + search box
- [ ] **Dark/Light auto-split**: detect background luminance, filter button alongside search
- [ ] **Current colors row**: "Your current colors" at top of theme list as reference point
- [ ] **AUR integration**: third source in dropdown; install via yay
- [ ] **Undo last apply**: restore from alacritty.toml-bak with one click in the UI
- [ ] **Export theme**: save current alacritty colors as a named .toml into data/themes/
- [ ] **Search filter memory**: persist last source + search across sessions
      (~/.config/alacritty-tweak-tool/prefs.json)
