"""TOML config read, write, and backup for alacritty-tweak-tool."""
import json
import os
import shutil
import tomlkit

import log

CONFIG_PATH = os.path.expanduser("~/.config/alacritty/alacritty.toml")
BACKUP_PATH = os.path.expanduser("~/.config/alacritty/alacritty.toml-bak")
PREFS_PATH = os.path.expanduser("~/.config/alacritty-tweak-tool/prefs.json")

DEFAULTS = {
    "font_family": "monospace",
    "font_size": 14.0,
    "opacity": 1.0,
    "decorations": "Full",
    "dynamic_title": True,
    "startup_mode": "Windowed",
    "blur": False,
    "scroll_history": 10000,
    "scroll_multiplier": 3,
    "pad_x": 0,
    "pad_y": 0,
    "cursor_shape": "Block",
    "cursor_blink": False,
    "cursor_thickness": 0.15,
    "blink_timeout": 5,
    "unfocused_hollow": True,
    "font_offset_x": 0,
    "font_offset_y": 0,
    "save_to_clipboard": False,
    "hide_when_typing": False,
    "live_config_reload": True,
}


def read_config():
    """Read and return the alacritty config as a tomlkit document."""
    if not os.path.isfile(CONFIG_PATH):
        log.log_warn("No config found — returning empty document")
        return tomlkit.document()
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return tomlkit.load(f)


def backup_config():
    """Copy the current config to alacritty.toml-bak before any write."""
    if os.path.isfile(CONFIG_PATH):
        shutil.copy2(CONFIG_PATH, BACKUP_PATH)
        log.log_info(f"Backup created: {BACKUP_PATH}")


def write_config(doc):
    """Write a tomlkit document back to the config file."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(tomlkit.dumps(doc))
    log.log_info(f"Config written: {CONFIG_PATH}")


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
    log.log_success("Colors applied")


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
    log.log_success(f"Appearance applied: font={font_family} size={font_size} opacity={opacity}")


def apply_scrolling(history, multiplier):
    """Backup config and update scrollback history and scroll multiplier."""
    backup_config()
    doc = read_config()
    if "scrolling" not in doc:
        doc.add("scrolling", tomlkit.table())
    doc["scrolling"]["history"] = history
    doc["scrolling"]["multiplier"] = multiplier
    write_config(doc)
    log.log_success(f"Scrolling applied: history={history} multiplier={multiplier}")


def apply_window_padding(x, y):
    """Backup config and update window padding."""
    backup_config()
    doc = read_config()
    if "window" not in doc:
        doc.add("window", tomlkit.table())
    if "padding" not in doc["window"]:
        doc["window"]["padding"] = tomlkit.table()
    doc["window"]["padding"]["x"] = x
    doc["window"]["padding"]["y"] = y
    write_config(doc)
    log.log_success(f"Window padding applied: x={x} y={y}")


def apply_cursor_full(shape, blink, thickness, blink_timeout, unfocused_hollow):
    """Backup config and update all cursor settings."""
    backup_config()
    doc = read_config()
    if "cursor" not in doc:
        doc.add("cursor", tomlkit.table())
    if "style" not in doc["cursor"]:
        doc["cursor"]["style"] = tomlkit.table()
    doc["cursor"]["style"]["shape"] = shape
    doc["cursor"]["style"]["blinking"] = "Always" if blink else "Never"
    doc["cursor"]["thickness"] = round(thickness, 2)
    doc["cursor"]["blink_timeout"] = blink_timeout
    doc["cursor"]["unfocused_hollow"] = unfocused_hollow
    write_config(doc)
    log.log_success(f"Cursor applied: shape={shape} blink={blink} thickness={thickness} "
                    f"blink_timeout={blink_timeout} hollow={unfocused_hollow}")


def apply_font_offset(x, y):
    """Backup config and update font glyph offset (character and line spacing)."""
    backup_config()
    doc = read_config()
    if "font" not in doc:
        doc.add("font", tomlkit.table())
    if "offset" not in doc["font"]:
        doc["font"]["offset"] = tomlkit.table()
    doc["font"]["offset"]["x"] = x
    doc["font"]["offset"]["y"] = y
    write_config(doc)
    log.log_success(f"Font offset applied: x={x} y={y}")


def apply_window_style(decorations, dynamic_title, startup_mode, blur):
    """Backup config and update window decorations, title, startup mode, and blur."""
    backup_config()
    doc = read_config()
    if "window" not in doc:
        doc.add("window", tomlkit.table())
    doc["window"]["decorations"] = decorations
    doc["window"]["dynamic_title"] = dynamic_title
    doc["window"]["startup_mode"] = startup_mode
    doc["window"]["blur"] = blur
    write_config(doc)
    log.log_success(f"Window style applied: decorations={decorations} dynamic_title={dynamic_title} "
                    f"startup_mode={startup_mode} blur={blur}")


def apply_behavior(save_to_clipboard, hide_when_typing, live_config_reload):
    """Backup config and update selection, mouse, and general behavior settings."""
    backup_config()
    doc = read_config()
    if "selection" not in doc:
        doc.add("selection", tomlkit.table())
    doc["selection"]["save_to_clipboard"] = save_to_clipboard
    if "mouse" not in doc:
        doc.add("mouse", tomlkit.table())
    doc["mouse"]["hide_when_typing"] = hide_when_typing
    if "general" not in doc:
        doc.add("general", tomlkit.table())
    doc["general"]["live_config_reload"] = live_config_reload
    write_config(doc)
    log.log_success(f"Behavior applied: save_to_clipboard={save_to_clipboard} "
                    f"hide_when_typing={hide_when_typing} live_config_reload={live_config_reload}")


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


def get_current_padding():
    """Return (x, y) window padding from config, defaulting to (0, 0)."""
    doc = read_config()
    padding = doc.get("window", {}).get("padding", {})
    return int(padding.get("x", 0)), int(padding.get("y", 0))


def get_current_scroll_multiplier():
    """Return scroll multiplier from config, defaulting to 3."""
    doc = read_config()
    return int(doc.get("scrolling", {}).get("multiplier", 3))


def get_current_cursor_extras():
    """Return (thickness, blink_timeout, unfocused_hollow) from config."""
    doc = read_config()
    cursor = doc.get("cursor", {})
    thickness = float(cursor.get("thickness", 0.15))
    blink_timeout = int(cursor.get("blink_timeout", 5))
    unfocused_hollow = bool(cursor.get("unfocused_hollow", True))
    return thickness, blink_timeout, unfocused_hollow


def get_current_font_offset():
    """Return (x, y) font glyph offset from config, defaulting to (0, 0)."""
    doc = read_config()
    offset = doc.get("font", {}).get("offset", {})
    return int(offset.get("x", 0)), int(offset.get("y", 0))


def get_current_window_style():
    """Return (decorations, dynamic_title, startup_mode, blur) from config."""
    doc = read_config()
    window = doc.get("window", {})
    decorations = str(window.get("decorations", "Full"))
    dynamic_title = bool(window.get("dynamic_title", True))
    startup_mode = str(window.get("startup_mode", "Windowed"))
    blur = bool(window.get("blur", False))
    return decorations, dynamic_title, startup_mode, blur


def get_current_behavior():
    """Return (save_to_clipboard, hide_when_typing, live_config_reload) from config."""
    doc = read_config()
    save_to_clipboard = bool(doc.get("selection", {}).get("save_to_clipboard", False))
    hide_when_typing = bool(doc.get("mouse", {}).get("hide_when_typing", False))
    live_config_reload = bool(doc.get("general", {}).get("live_config_reload", True))
    return save_to_clipboard, hide_when_typing, live_config_reload


def get_current_colors():
    """Return the colors dict from the current config, or empty dict if none."""
    return dict(read_config().get("colors", {}))


def restore_backup():
    """Restore config from alacritty.toml-bak; return True if backup existed."""
    if not os.path.isfile(BACKUP_PATH):
        log.log_warn("No backup found — nothing to restore")
        return False
    shutil.copy2(BACKUP_PATH, CONFIG_PATH)
    log.log_success(f"Restored from backup: {BACKUP_PATH}")
    return True


def load_prefs():
    """Return UI preferences dict from prefs.json, or empty dict if missing/invalid."""
    if not os.path.isfile(PREFS_PATH):
        return {}
    try:
        with open(PREFS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_prefs(prefs):
    """Write UI preferences dict to prefs.json."""
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    with open(PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2)
