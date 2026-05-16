"""TOML config read, write, and backup for alacritty-tweak-tool."""
import os
import shutil
import tomlkit

CONFIG_PATH = os.path.expanduser("~/.config/alacritty/alacritty.toml")
BACKUP_PATH = os.path.expanduser("~/.config/alacritty/alacritty.toml-bak")


def read_config():
    """Read and return the alacritty config as a tomlkit document."""
    if not os.path.isfile(CONFIG_PATH):
        print("[ATT] No config found — returning empty document")
        return tomlkit.document()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return tomlkit.load(f)


def backup_config():
    """Copy the current config to alacritty.toml-bak before any write."""
    if os.path.isfile(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
        print(f"[ATT] Backup created: {BACKUP_PATH}")


def write_config(doc):
    """Write a tomlkit document back to the config file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    print(f"[ATT] Config written: {CONFIG_PATH}")


def apply_colors(colors):
    """Backup config and update only primary/normal/bright/cursor color sections."""
    backup_config()
    doc = read_config()
    if "colors" not in doc:
        doc.add("colors", tomlkit.table())
    for section in ("primary", "normal", "bright", "cursor"):
        if section in colors:
            doc["colors"][section] = colors[section]
    write_config(doc)
    print("[ATT] Colors applied")


def apply_appearance(font_family, font_size, opacity):
    """Backup config and update font family/size and window opacity."""
    backup_config()
    doc = read_config()
    if "font" not in doc:
        doc.add("font", tomlkit.table())
    doc["font"]["size"] = font_size
    for style in ("normal", "bold", "italic", "bold_italic"):
        if style not in doc["font"]:
            doc["font"][style] = tomlkit.table()
        doc["font"][style]["family"] = font_family
    if "window" not in doc:
        doc.add("window", tomlkit.table())
    doc["window"]["opacity"] = round(opacity, 2)
    write_config(doc)
    print(f"[ATT] Appearance applied: font={font_family} size={font_size} opacity={opacity}")


def apply_advanced(scrollback, cursor_shape, cursor_blink):
    """Backup config and update scrollback history and cursor settings."""
    backup_config()
    doc = read_config()
    if "scrolling" not in doc:
        doc.add("scrolling", tomlkit.table())
    doc["scrolling"]["history"] = scrollback
    if "cursor" not in doc:
        doc.add("cursor", tomlkit.table())
    if "style" not in doc["cursor"]:
        doc["cursor"]["style"] = tomlkit.table()
    doc["cursor"]["style"]["shape"] = cursor_shape
    doc["cursor"]["style"]["blinking"] = "Always" if cursor_blink else "Never"
    write_config(doc)
    print(f"[ATT] Advanced applied: scrollback={scrollback} shape={cursor_shape} blink={cursor_blink}")


def get_current_font():
    """Return (family, size) from the current config, with sensible defaults."""
    doc = read_config()
    font = doc.get("font", {})
    family = font.get("normal", {}).get("family", "monospace")
    size = float(font.get("size", 14.0))
    return family, size


def get_current_opacity():
    """Return window opacity from config, defaulting to 1.0."""
    doc = read_config()
    return float(doc.get("window", {}).get("opacity", 1.0))


def get_current_scrollback():
    """Return scrollback history from config, defaulting to 10000."""
    doc = read_config()
    return int(doc.get("scrolling", {}).get("history", 10000))


def get_current_cursor():
    """Return (shape, blink_bool) from config, defaulting to Block/False."""
    doc = read_config()
    style = doc.get("cursor", {}).get("style", {})
    shape = style.get("shape", "Block")
    blink = style.get("blinking", "Never") == "Always"
    return shape, blink
