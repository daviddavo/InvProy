print("Module save imported")
import pickle
import gi
import gi.repository
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gdk, GdkPixbuf

gladefile = "Interface2.glade"
last = 0
asgl = 1

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
        print(fil.split(".")[-1])
        if fil.split(".")[-1] != "inv":
            print("Nombre de archivo {} no tiene extensión .inv".format(fil))
            fil += ".inv"
        last = fil
        try:
            os.remove(fil)
        except:
            pass
        print(allobjects)
        with open(fil, "wb") as output:
            pickle.dump((allobjects,cabls), output)

def load(allobjects, cabls):
    lw = loadWindow()
    fil = lw.run()
    lw.destroy()
    print(fil)
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
            print(allobj)
            print(cables)
            for obj in allobj:
                obj.load()
            for cable in cables:
                cable.load()

class loadWindow(Gtk.Window):
    def __init__(self, mode=0):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladefile)
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
            print("Saving")
            self.window.set_action(Gtk.FileChooserAction.SAVE)
            self.builder.get_object("window-filechooser_load-this").set_label("Guardar")

    def run(self):
        rs = self.window.run()
        self.window.hide()
        if rs == 1:
            rs = self.window.get_filename()
        self.window.destroy()
        return rs
    def destroy(self):
        del self
