"""Theme discovery, color swatch helpers, and apply logic."""
import json
import os
import tomlkit

from alacritty_config import apply_colors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THEMES_BASE_DIR = os.path.join(BASE_DIR, "data", "themes")


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


def _source_label(subdir_path, folder_name):
    """Return display label for a theme source directory.

    Reads label from source.json if present, otherwise uses the folder name.
    """
    source_json = os.path.join(subdir_path, "source.json")
    if os.path.isfile(source_json):
        try:
            with open(source_json, "r", encoding="utf-8") as f:
                return json.load(f).get("label", folder_name)
        except Exception:
            pass
    return folder_name


def load_themes_by_source():
    """Return ordered dict of source_label -> [(display_name, colors_dict)].

    Each subdirectory of data/themes/ is one source. A source.json file inside
    the subdirectory provides the display label and package metadata.
    Adding a new source is as simple as creating a new subdirectory.
    """
    sources = {}
    if not os.path.isdir(THEMES_BASE_DIR):
        return sources
    for entry in sorted(os.scandir(THEMES_BASE_DIR), key=lambda e: e.name):
        if not entry.is_dir():
            continue
        label = _source_label(entry.path, entry.name)
        items = _load_from_dir(entry.path)
        if items:
            sources[label] = items
            print(f"[ATT] {len(items)} themes from '{label}' ({entry.name}/)")
    return sources


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


def theme_luminance(colors):
    """Return relative luminance (0–1) of the theme's primary background color."""
    bg = str(colors.get("primary", {}).get("background", "#000000"))
    r, g, b = hex_to_rgb(bg)

    def _lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def colors_to_rgb_list(colors, section):
    """Return list of (r,g,b) floats for the 8 named ANSI colors in a section dict."""
    order = ("black", "red", "green", "yellow", "blue", "magenta", "cyan", "white")
    section_data = colors.get(section, {})
    return [hex_to_rgb(str(section_data.get(name, "#808080"))) for name in order]


def apply_theme(colors):
    """Apply the given colors to the real alacritty config (with backup)."""
    apply_colors(colors)


def export_theme(name, colors):
    """Save colors as a named .toml into data/themes/user/; return the written path."""
    user_dir = os.path.join(BASE_DIR, "data", "themes", "user")
    os.makedirs(user_dir, exist_ok=True)
    source_json = os.path.join(user_dir, "source.json")
    if not os.path.isfile(source_json):
        with open(source_json, "w", encoding="utf-8") as f:
            json.dump({"label": "My Themes"}, f)
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in name).strip() or "custom"
    path = os.path.join(user_dir, f"{safe_name}.toml")
    doc = tomlkit.document()
    doc.add("colors", colors)
    with open(path, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    print(f"[ATT] Theme exported: {path}")
    return path
