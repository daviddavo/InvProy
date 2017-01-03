import pickle
import os
import gi
import gi.repository
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from invproy import main
from invproy.modules import logmod

GLADEFILE = main.GLADEFILE
last = 0
asgl = 1
logger = logmod.logging.getLogger("save")

### AUN NO FUNCIONA ###

def save(allobjects, cabls, aslc=0):
    global asgl
    global last
    if aslc | asgl:
        asgl = 0
        sw = loadWindow(mode=1)
        fil = sw.run()
        sw.destroy()
    else:
        fil = last
    if fil != 0:
        logger.debug(fil.split(".")[-1])
        if fil.split(".")[-1] != "inv":
            logger.debug("Nombre de archivo {} no tiene extensión .inv".format(fil))
            fil += ".inv"
        last = fil
        try:
            os.remove(fil)
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
        logger.debug(allobjects)
        with open(fil, "wb") as output:
            pickle.dump((allobjects,cabls), output)

def load(allobjects, cabls):
    lw = loadWindow()
    fil = lw.run()
    lw.destroy()
    logger.debug(fil)
    if fil != 0:
        global last
        global asgl
        asgl = 0
        last = fil
        while len(allobjects) > 0:
            allobjects[0].delete(pr=0)
        while len(cabls) > 0:
            cabls[0].delete()
        with open(fil, "rb") as inpt:
            allobj, cables = pickle.load(inpt)
            logger.debug(allobj)
            logger.debug(cables)
            for obj in allobj:
                obj.load()
            for cable in cables:
                cable.load()

class loadWindow(Gtk.Window):
    def __init__(self, mode=0):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADEFILE)
        self.window = self.builder.get_object("window-filechooser_load")
        filt = Gtk.FileFilter.new()
        filt.add_pattern("*.inv")
        filt.set_name("Archivos .inv")
        self.window.add_filter(filt)
        todos = Gtk.FileFilter.new()
        todos.add_pattern("*")
        todos.set_name("Todos los tipos de archivo")
        self.window.add_filter(todos)
        if mode == 1:
            logger.debug("Saving")
            self.window.set_action(Gtk.FileChooserAction.SAVE)
            self.builder.get_object("window-filechooser_load-this").set_label("Guardar")

    def run(self):
        rs = self.window.run()
        if rs == 1:
            rs = self.window.get_filename()
            if os.path.isdir(rs):
                self.window.set_current_folder("rs")
                self.run()
        self.window.hide()
        self.window.destroy()
        return rs

    def destroy(self):
        del self
