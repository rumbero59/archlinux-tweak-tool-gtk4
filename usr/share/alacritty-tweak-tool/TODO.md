# Alacritty Tweak Tool — Roadmap

## Done

- [x] Three-tab GTK4 app (Themes / Appearance / Advanced)
- [x] 231 themes from alacritty-themes npm package + 12 bundled fallback
- [x] Color swatches via Cairo DrawingArea
- [x] Preview: launches `alacritty --config-file /tmp/...` with fastfetch
- [x] Apply: writes colors with tomlkit (preserves comments)
- [x] Backup to alacritty.toml-bak before every write
- [x] Appearance: reads current config on launch, pre-populates font/opacity controls
- [x] Advanced: reads current config on launch, pre-populates scrollback/cursor controls
- [x] Source dropdown to switch between theme sources (Option A)
- [x] Live search bar to filter themes by name

## Next

- [ ] **Option C — Full category UI**: source tabs each with Dark/Light toggle + search box
      (currently Option A: source dropdown + search bar)
- [ ] **Dark/Light auto-split**: detect background luminance, add Dark/Light filter button
      alongside search bar; threshold ~50% relative luminance
- [ ] **Current colors preview row**: show a "Your current colors" row at top of theme list
      so you can see where you are before browsing
- [ ] **AUR integration**: third source in the dropdown fetching themes from AUR;
      install via `yay -S <alacritty-theme-package>`
- [ ] **Move all 231 themes into the project** (data/themes/) for full independence
      from the npm package — 936 KB, negligible
- [ ] **Search filter memory**: remember last search and source selection across sessions
      (write to a small JSON prefs file in ~/.config/alacritty-tweak-tool/)
- [ ] **Undo last apply**: restore from alacritty.toml-bak with one click
- [ ] **Export theme**: save current colors as a named .toml file into data/themes/
