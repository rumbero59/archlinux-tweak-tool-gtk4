"""Theme discovery, color swatch helpers, and preview/apply logic."""
import os
import shutil
import subprocess
import tomlkit

from alacritty_config import apply_colors, read_config

SYSTEM_THEMES_DIR = "/usr/lib/node_modules/alacritty-themes/themes"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FALLBACK_THEMES_DIR = os.path.join(BASE_DIR, "data", "themes")
PREVIEW_CONFIG = "/tmp/alacritty-tweak-preview.toml"


def _load_from_dir(directory):
    """Load all valid .toml theme files from directory; return [(name, colors_dict)]."""
    result = []
    if not os.path.isdir(directory):
        return result
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".toml"):
            continue
        path = os.path.join(directory, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                doc = tomlkit.load(f)
            colors = doc.get("colors", {})
            if colors:
                result.append((fname[:-5], dict(colors)))
        except Exception as e:
            print(f"[ATT] Skipping {fname}: {e}")
    return result


def load_themes_by_source():
    """Return ordered dict of source_label -> [(display_name, colors_dict)].

    Sources are discovered at runtime:
      - 'alacritty-themes' from the npm system package if installed
      - 'Bundled' from the app's own data/themes/ directory
    """
    sources = {}
    system = _load_from_dir(SYSTEM_THEMES_DIR)
    if system:
        sources["alacritty-themes"] = system
        print(f"[ATT] {len(system)} themes from alacritty-themes")
    bundled = _load_from_dir(FALLBACK_THEMES_DIR)
    if bundled:
        sources["Bundled"] = bundled
        print(f"[ATT] {len(bundled)} bundled themes")
    return sources


def load_all_themes():
    """Return flat list of (display_name, colors_dict) across all sources."""
    all_themes = []
    for items in load_themes_by_source().values():
        all_themes.extend(items)
    return all_themes


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
    return [hex_to_rgb(str(section_data.get(name, "#808080"))) for name in order]


def preview_theme(colors):
    """Write a temp config and launch alacritty showing fastfetch if available."""
    doc = read_config()
    if "colors" not in doc:
        doc.add("colors", tomlkit.table())
    for section in ("primary", "normal", "bright", "cursor"):
        if section in colors:
            doc["colors"][section] = colors[section]
    with open(PREVIEW_CONFIG, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))

    if shutil.which("fastfetch"):
        cmd = ["alacritty", "--config-file", PREVIEW_CONFIG,
               "-e", "bash", "-c", "fastfetch; read -p 'Press Enter to close...' _"]
    else:
        cmd = ["alacritty", "--config-file", PREVIEW_CONFIG]

    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[ATT] Preview launched: {PREVIEW_CONFIG}")


def apply_theme(colors):
    """Apply the given colors to the real alacritty config (with backup)."""
    apply_colors(colors)
