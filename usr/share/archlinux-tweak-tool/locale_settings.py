# ============================================================
# Authors: Erik Dubois
# ============================================================

import os
import stat
import tempfile
import threading
import subprocess
import functions as fn
from gi.repository import GLib


def _parse_localectl():
    result = subprocess.run(["localectl", "status"], capture_output=True, text=True)
    data = {}
    for line in result.stdout.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            data[key.strip()] = val.strip()
    return data


def get_x11_variants(layout):
    result = subprocess.run(
        ["localectl", "list-x11-keymap-variants", layout],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().splitlines()
    return [""] + lines if lines else [""]


def refresh_status(self):
    status = _parse_localectl()
    lang = status.get("System Locale", "LANG=unknown").replace("LANG=", "")
    vc_keymap = status.get("VC Keymap", "unknown")
    x11_layout = status.get("X11 Layout", "unknown")
    x11_variant = status.get("X11 Variant", "")
    x11_display = x11_layout + (f" ({x11_variant})" if x11_variant else "")

    tz_result = subprocess.run(
        ["timedatectl", "show", "--property=Timezone", "--value"],
        capture_output=True, text=True
    )
    timezone = tz_result.stdout.strip()

    GLib.idle_add(self.lbl_locale_current.set_text, lang)
    GLib.idle_add(self.lbl_keymap_current.set_text, vc_keymap)
    GLib.idle_add(self.lbl_x11_current.set_text, x11_display)
    GLib.idle_add(self.lbl_timezone_current.set_text, timezone)


def on_apply_locale(self, _widget):
    fn.log_subsection("Locale - Apply System Locale")
    obj = self.locale_dropdown.get_selected_item()
    if obj is None:
        return
    locale_val = obj.get_string()
    fn.log_info(f"Setting LANG={locale_val}")
    try:
        subprocess.run(["localectl", "set-locale", f"LANG={locale_val}"], check=True)
        fn.log_success(f"System locale set to {locale_val}")
        fn.show_in_app_notification(self, f"Locale set to {locale_val}")
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set locale: {e}")
    refresh_status(self)


def on_apply_keymap(self, _widget):
    fn.log_subsection("Locale - Apply Console Keymap")
    obj = self.keymap_dropdown.get_selected_item()
    if obj is None:
        return
    keymap = obj.get_string()
    fn.log_info(f"Setting VC keymap: {keymap}")
    try:
        subprocess.run(["localectl", "set-keymap", keymap], check=True)
        fn.log_success(f"Console keymap set to {keymap}")
        fn.show_in_app_notification(self, f"Console keymap set to {keymap}")
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set keymap: {e}")
    refresh_status(self)


def on_sync_keymap(self, _widget):
    fn.log_subsection("Locale - Sync TTY keymap from X11 layout")
    status = _parse_localectl()
    x11_layout = status.get("X11 Layout", "")
    if not x11_layout:
        fn.log_warn("No X11 layout set, cannot sync")
        return
    model = self.keymap_dropdown.get_model()
    n = model.get_n_items()
    for i in range(n):
        if model.get_item(i).get_string() == x11_layout:
            self.keymap_dropdown.set_selected(i)
            break
    else:
        fn.log_warn(f"No TTY keymap exactly matching '{x11_layout}' — applying as-is")
    on_apply_keymap(self, None)


def on_apply_x11(self, _widget):
    fn.log_subsection("Locale - Apply X11 Keyboard Layout")
    layout_obj = self.x11_layout_dropdown.get_selected_item()
    if layout_obj is None:
        return
    layout = layout_obj.get_string()
    variant_obj = self.x11_variant_dropdown.get_selected_item()
    variant = variant_obj.get_string() if variant_obj else ""
    fn.log_info(f"Setting X11 layout: {layout} variant: {variant or '(none)'}")
    try:
        cmd = ["localectl", "set-x11-keymap", layout]
        if variant:
            cmd.append(variant)
        subprocess.run(cmd, check=True)
        fn.log_success(f"X11 layout set to {layout} {variant}".strip())
        fn.show_in_app_notification(self, f"X11 layout set to {layout}")
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set X11 layout: {e}")
    refresh_status(self)


def get_available_locales():
    try:
        with open("/usr/share/i18n/SUPPORTED") as f:
            lines = f.readlines()
    except OSError:
        return []
    locales = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts:
            locales.append(parts[0])
    return sorted(set(locales))


def _update_locale_gen(locale_val):
    try:
        with open("/usr/share/i18n/SUPPORTED") as f:
            supported_map = {
                parts[0]: line.strip()
                for line in f
                if (line := line.strip()) and not line.startswith("#") and (parts := line.split()) and len(parts) >= 2
            }
    except OSError:
        fn.log_error("Cannot read /usr/share/i18n/SUPPORTED")
        return False

    full_entry = supported_map.get(locale_val, locale_val)

    try:
        with open("/etc/locale.gen") as f:
            lines = f.readlines()
    except OSError:
        fn.log_error("Cannot read /etc/locale.gen")
        return False

    if any(line.strip() == full_entry for line in lines):
        fn.log_info(f"{locale_val} already enabled in /etc/locale.gen")
        return True

    new_lines = []
    uncommented = False
    for line in lines:
        stripped = line.strip()
        if stripped in (f"#{full_entry}", f"# {full_entry}"):
            new_lines.append(f"{full_entry}\n")
            uncommented = True
        else:
            new_lines.append(line)

    if not uncommented:
        new_lines.append(f"{full_entry}\n")
        fn.log_info(f"Appended {full_entry} to /etc/locale.gen")
    else:
        fn.log_info(f"Uncommented {locale_val} in /etc/locale.gen")

    try:
        with open("/etc/locale.gen", "w") as f:
            f.writelines(new_lines)
        fn.log_success("Updated /etc/locale.gen")
        return True
    except OSError as e:
        fn.log_error(f"Cannot write /etc/locale.gen: {e}")
        return False


def on_apply_generate_locale(self, _widget):
    fn.log_subsection("Locale - Generate New Locale")
    obj = self.available_locale_dropdown.get_selected_item()
    if obj is None or not obj.get_string():
        fn.log_warn("No locale selected")
        return
    locale_val = obj.get_string()
    fn.log_info(f"Generating locale: {locale_val}")

    if not _update_locale_gen(locale_val):
        return

    script = f"""#!/bin/bash
set -euo pipefail
RESET=$(tput sgr0)
CYAN=$(tput setaf 6)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
separator() {{ printf '%*s\\n' "${{COLUMNS:-80}}" '' | tr ' ' '-'; }}
header()  {{ separator; echo "${{CYAN}}>>> $*${{RESET}}"; separator; }}
success() {{ echo "${{GREEN}}[OK]  $*${{RESET}}"; }}
info()    {{ echo "      $*"; }}
warn()    {{ echo "${{YELLOW}}[!!]  $*${{RESET}}"; }}

header "Generate Locale: {locale_val}"
info "Running locale-gen..."
locale-gen
success "locale-gen completed"

header "Set System Locale"
localectl set-locale "LANG={locale_val}"
success "System locale set to {locale_val}"

read -p "Press Enter to close..."
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
        f.write(script)
        tmp_path = f.name
    os.chmod(tmp_path, stat.S_IRWXU)
    fn.show_in_app_notification(self, f"Generating locale {locale_val}...")

    def _run():
        proc = subprocess.Popen(
            ["alacritty", "-e", "bash", tmp_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        proc.wait()
        os.unlink(tmp_path)
        fn.log_success(f"Locale {locale_val} generated and set")
        GLib.idle_add(refresh_status, self)

    threading.Thread(target=_run, daemon=True).start()


def on_apply_timezone(self, _widget):
    fn.log_subsection("Locale - Apply Timezone")
    obj = self.timezone_dropdown.get_selected_item()
    if obj is None:
        return
    tz = obj.get_string()
    fn.log_info(f"Setting timezone: {tz}")
    try:
        subprocess.run(["timedatectl", "set-timezone", tz], check=True)
        fn.log_success(f"Timezone set to {tz}")
        fn.show_in_app_notification(self, f"Timezone set to {tz}")
    except subprocess.CalledProcessError as e:
        fn.log_error(f"Failed to set timezone: {e}")
    refresh_status(self)
