import gi
import cairo
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf

GLADEFILE = "interface.glade"

class MainWindow(Gtk.Window):
    self.builder = Gtk.Builder()
    self.builder.add_from_file(GLADEFILE)