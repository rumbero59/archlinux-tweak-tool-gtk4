"""Theme discovery, color swatch helpers, and preview/apply logic."""
import os
import subprocess
import tomlkit

from alacritty_config import apply_colors, read_config

SYSTEM_THEMES_DIR = "/usr/lib/node_modules/alacritty-themes/themes"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FALLBACK_THEMES_DIR = os.path.join(BASE_DIR, "data", "themes")
PREVIEW_CONFIG = "/tmp/alacritty-tweak-preview.toml"


def get_themes_dir():
    """Return the system themes dir if available, else the bundled fallback."""
    if os.path.isdir(SYSTEM_THEMES_DIR):
        return SYSTEM_THEMES_DIR
    print(f"[ATT] System themes not found at {SYSTEM_THEMES_DIR}, using bundled fallback")
    return FALLBACK_THEMES_DIR


def load_all_themes():
    """Return a sorted list of (display_name, colors_dict) tuples from the themes dir."""
    themes_dir = get_themes_dir()
    themes = []
    for fname in sorted(os.listdir(themes_dir)):
        if not fname.endswith(".toml"):
            continue
        path = os.path.join(themes_dir, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc = tomlkit.load(f)
            colors = doc.get("colors", {})
            if not colors:
                continue
            display_name = fname[:-5]
            themes.append((display_name, dict(colors)))
        except Exception as e:
            print(f"[ATT] Skipping {fname}: {e}")
    print(f"[ATT] Loaded {len(themes)} themes from {themes_dir}")
    return themes


def hex_to_rgb(hex_str):
    """Convert '#rrggbb' or '0xrrggbb' color string to (r, g, b) floats 0–1."""
    s = hex_str.strip()
    if s.startswith(("0x", "0X")):
        s = s[2:]
    elif s.startswith("#"):
        s = s[1:]
    if len(s) < 6:
        return 0.5, 0.5, 0.5
    try:
        return int(s[0:2], 16) / 255.0, int(s[2:4], 16) / 255.0, int(s[4:6], 16) / 255.0
    except ValueError:
        return 0.5, 0.5, 0.5


def colors_to_rgb_list(colors, section):
    """Return list of (r,g,b) floats for the 8 named ANSI colors in a section dict."""
    order = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    section_data = colors.get(section, {})
    result = []
    for name in order:
        val = section_data.get(name, "#808080")
        result.append(hex_to_rgb(str(val)))
    return result


def preview_theme(colors):
    """Write a temp config with the given colors and launch alacritty on it."""
    doc = read_config()
    if "colors" not in doc:
        doc.add("colors", tomlkit.table())
    for section in ("primary", "normal", "bright", "cursor"):
        if section in colors:
            doc["colors"][section] = colors[section]
    with open(PREVIEW_CONFIG, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    subprocess.Popen(
        ["alacritty", "--config-file", PREVIEW_CONFIG],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[ATT] Preview launched with {PREVIEW_CONFIG}")


def apply_theme(colors):
    """Apply the given colors to the real alacritty config (with backup)."""
    apply_colors(colors)
