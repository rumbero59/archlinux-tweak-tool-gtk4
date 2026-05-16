#!/usr/bin/env python3
"""Alacritty Tweak Tool — GTK4 config editor for Alacritty terminal."""
import os
import subprocess
import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import alacritty_config  # noqa: E402
import alacritty_gui as gui_module  # noqa: E402
import log  # noqa: E402


def _alacritty_version():
    """Return the installed alacritty version string, or 'unknown'."""
    try:
        out = subprocess.run(["alacritty", "--version"], capture_output=True, text=True, timeout=3)
        # output is e.g. "alacritty 0.14.0"
        parts = out.stdout.strip().split()
        return parts[1] if len(parts) >= 2 else out.stdout.strip()
    except Exception:
        return "unknown"


class AlacrittyTweakApp(Gtk.Application):
    """GTK4 application entry point for alacritty-tweak-tool."""

    def __init__(self):
        super().__init__(application_id="com.kiro.alacritty-tweak-tool")
        self.connect("activate", self.on_activate)

    def on_activate(self, _app):
        window = Main(self)
        window.present()


class Main(Gtk.ApplicationWindow):
    """Main application window."""

    def __init__(self, app):
        super().__init__(application=app, title="Alacritty Tweak Tool")
        self.set_default_size(900, 580)
        self._load_css()
        self._build_headerbar()
        gui_module.build(self, _alacritty_version())
        log.log_timing("GUI built")
        log.log_section("Alacritty Tweak Tool started")
        last_theme = alacritty_config.load_prefs().get("last_theme", "")
        if last_theme:
            log.log_info(f"Current theme: {last_theme}")

    def _build_headerbar(self):
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_title_buttons(True)
        self.set_titlebar(headerbar)

    def _load_css(self):
        css_path = os.path.join(BASE_DIR, "att.css")
        if not os.path.isfile(css_path):
            return
        provider = Gtk.CssProvider()
        provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )


def main():
    """Run the application."""
    filtered_argv = sys.argv
    if "--debug" in sys.argv:
        log.DEBUG = True
        filtered_argv = [a for a in filtered_argv if a != "--debug"]
        log.log_section("Debug mode enabled")
    if "--dev" in sys.argv:
        log.DEV = True
        filtered_argv = [a for a in filtered_argv if a != "--dev"]
        log.log_section("Dev mode enabled")
    app = AlacrittyTweakApp()
    sys.exit(app.run(filtered_argv))


if __name__ == "__main__":
    main()
