#!/usr/bin/env python3
"""Alacritty Tweak Tool — GTK4 config editor for Alacritty terminal."""
import os
import sys

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

APP_VERSION = "1.0.0"

import alacritty_gui as gui_module  # noqa: E402


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
        gui_module.build(self, APP_VERSION)
        print("[ATT] Alacritty Tweak Tool started")

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
    app = AlacrittyTweakApp()
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    main()
