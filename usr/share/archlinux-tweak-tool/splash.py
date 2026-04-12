# ============================================================
# Authors: Brad Heffernan - Erik Dubois - Cameron Percival
# ============================================================
# pylint:disable=C0115,I1101

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GdkPixbuf
import functions as fn


base_dir = fn.path.dirname(fn.path.realpath(__file__))


class SplashScreen(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(500, 250)

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
        self.set_child(main_vbox)

        self.image = Gtk.Image()
        pimage = GdkPixbuf.Pixbuf.new_from_file_at_size(
            base_dir + "/images/splash.png", 600, 400
        )
        self.image.set_from_pixbuf(pimage)

        main_vbox.append(self.image)

        self.present()
