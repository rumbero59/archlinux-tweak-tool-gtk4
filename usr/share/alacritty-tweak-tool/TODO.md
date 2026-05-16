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

- [x] **VTE embedded terminal in Themes tab**: Vte.Terminal in right panel; colors
      update live on every selection via `vte.set_colors()`; fastfetch spawned once
      on realize then shell stays open; Preview button removed
- [x] **Copy 231 themes into data/themes/**: 936 KB, makes app independent of npm package;
      no fallback logic needed — loader reads all subdirs of data/themes/ automatically

## Next — roadmap

- [ ] **Theme Creator tab**: new fourth tab for building a custom theme from scratch.
      Two entry points feed the same color-by-color editor:
      1. **Color by color** — `Gtk.ColorButton` grid: Normal / Bright columns, 8 rows each
         (black/red/green/yellow/blue/magenta/cyan/white), plus primary fg/bg and cursor
         text/color. Live VTE preview updates on every color pick. Name field + Save button
         writes a `.toml` into `data/themes/user/` so it appears in the Themes tab.
      2. **From wallpaper** — file chooser picks an image; ImageMagick (`convert`, official
         repos) or `python-colorthief` (AUR fallback) extracts dominant colors; a
         hue-matching heuristic maps extracted colors to ANSI slots by luminance/saturation;
         result pre-populates the color grid for manual fine-tuning.
      Recommended UX: wallpaper picker sits above the grid as an optional first step —
      wallpaper → auto-populate → tweak → save. Dependency: prefer ImageMagick (in
      official repos); detect at runtime and show an install prompt if missing.

- [ ] **Option C — Full category UI**: source tabs each with Dark/Light toggle + search box
- [ ] **Dark/Light auto-split**: detect background luminance, filter button alongside search
- [x] **Current colors row**: pinned "Current theme" row at top of list; bypasses source
      filter, still matches search; shows current config colors as swatch
- [x] **Reset to defaults**: flat "Reset to defaults" button next to every Apply button;
      restores all widgets in that section to DEFAULTS dict values without writing to disk;
      user still clicks Apply to persist. Covered: Appearance, Scrolling, Padding, Cursor,
      Font Spacing, Behavior.
- [ ] **AUR integration**: third source in dropdown; install via yay
- [x] **Undo last apply**: "Undo Last Apply" button in detail panel; restores from alacritty.toml-bak
- [x] **Export theme**: name entry + Export button in detail panel; saves to data/themes/user/
      as .toml; reloads the theme list automatically after save
- [x] **Export theme — user-writable path**: currently writes to `/usr/share/alacritty-tweak-tool/data/themes/user/`
      which is root-only; fix: write to `~/.config/alacritty-tweak-tool/themes/user/` instead;
      update `load_themes_by_source()` to scan both system `data/themes/` and user
      `~/.config/alacritty-tweak-tool/themes/` so exported themes appear in the picker
- [x] **Search filter memory**: source + search persisted in ~/.config/alacritty-tweak-tool/prefs.json;
      restored on next launch via load_prefs() in `_populate_theme_list`
