# -*- coding: utf-8 -*-
#!/usr/bin/env python3

'''
    InvProy - Simulador de Redes / Proyecto de Investigación
    https://github.com/daviddavo/InvProy
    Copyright (C) 2016  David Davó Laviña  david@ddavo.me  http://ddavo.me

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    /////////////////////////////

    Este programa es código libre: Puedes redistribuirlo y/o modificarlo
    bajo los términos de la licencia GNU General Public License tal y como
    publicado por la Free Software Foundation, ya sea la versión 3 de layout
    licencia o la más reciente.

    Este programa es distribuido con la esperanza de que sea útil, pero
    SIN NINGUNA GARANTÍA; sin siquiera la garantía implícita de COMERCIABILIDAD
    o de la APTITUD DE LA MISMA PARA UN PROPÓSITO PARTICULAR. Ver la GNU General
    Public License para más detalles.

    Debes haber recibido una copia de la GNU General Public License con
    este programa, si no es así, ver <http://www.gnu.org/licenses/>.
'''
import configparser, os, sys, time, random, math
from datetime import datetime
startTime = datetime.now()

import xml.etree.ElementTree as xmltree
from ipaddress import ip_address
from random import choice

__home__ = os.path.expanduser("~/.invproy")
from invproy.modules import logmod
logger = logmod.logging.getLogger("main")

os.system("clear")
print("\033[91m##############################\033[00m")

print("InvProy  Copyright (C) 2016  David Davó Laviña\ndavid@ddavo.me   <http://ddavo.me>\n\
This program comes with ABSOLUTELY NO WARRANTY; for details go to 'Ayuda > Acerca de'\n\
This is free software, and you are welcome to redistribute it\n\
under certain conditions\n")

logger.info("Start loading time: " + time.strftime("%H:%M:%S"))

try:
    #Importando las dependencias de la interfaz
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
except ImportError:
    print("Por favor, instala PyGObject en tu ordenador. \n\
      En ubuntu suele ser 'apt-get install python3-gi'\n\
      En Archlinux es 'pacman -S python-gobject'")
    sys.exit()

try:
    import cairo
except ImportError:
    print("Necesitas tener instalado cairo")
    print("Como es lógico, pon 'pacman -S python-cairo' en Archlinux")
    sys.exit()

#Definiendo un par de cosillas necesarias

maindir, this_filename = os.path.split(__file__)
GLADEFILE = maindir + "/Interface2.glade"
from invproy.modules import save
gtk = Gtk
config      = configparser.RawConfigParser()

config.read(maindir + "/Config.ini")
allobjects = []

def digitsnumber(number, digits):
    """Funcion que convierte un numero a una str con [digits] cifras"""
    if len(str(number)) == digits:
        return str(number)
    elif len(str(number)) < digits:
        return  "0" * ( digits - len(str(number)) ) + str(number)
    else:
        return "-1"

def hex_to_rgba(value):
    """Convierte hexadecimal a RGBA tal y como Gdk lo requiere"""
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join([v*2 for v in list(value)])
    (r1, g1, b1, a1)=tuple(int(value[i:i+2], 16) for i in range(0, 6, 2))+(1, )
    (r1, g1, b1, a1)=(r1/255.00000, g1/255.00000, b1/255.00000, a1)

    return (r1, g1, b1, a1)

def checkres(recurdir):
    """Comprueba la integridad del pack de recursos"""
    files = ["Cable.png", "Router.png", "Switch.png", "Computer.png", "Hub.png"]
    cnt = 0
    ss = []
    for i in files:
        if os.path.isfile(recurdir + i):
            cnt += 1
        else:
            ss.append(i)

    if not (cnt == len(files)):
        logger.error("Faltan archivos en "+recurdir)
        sys.exit()
    else:
        logger.info("No falta ningún archivo")

logger.info(os.listdir( os.path.abspath(os.path.join(maindir, os.pardir ))))
logger.info(os.listdir(maindir))
logger.info(os.listdir(maindir + "/resources"))
checkres(maindir + "/" + config.get("DIRS", "respack"))

contador = 0
def push_elemento(texto):
    """Envia a la Statusbar informacion."""
    global contador
    varra1 = builder.get_object("barra1")
    data = varra1.get_context_id("Ejemplocontextid")
    testo = time.strftime("%H:%M:%S") + " | " + texto
    contador = contador + 1
    varra1.push(data, testo)

def bformat(num, fix):
    """Retorna un entero en formato de bin fixed"""
    if isinstance(num, int):
        return str(("{0:0" + str(fix) + "b}").format(num))
    else:
        return "ERR0R"


try:
    builder = Gtk.Builder()
    builder.add_from_file(GLADEFILE)
    logger.info("Interfaz cargada\n\t>Cargados un total de " + str(len(builder.get_objects())) + " objetos")
    xmlroot = xmltree.parse(GLADEFILE).getroot()
    logger.info("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0")
    logger.info(" | Usando Gtk+ "+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
except Exception as e:
    logger.error("Error: No se ha podido cargar la interfaz.")
    if "required" in str(e):
        xmlroot = xmltree.parse(GLADEFILE).getroot()
        logger.error("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0", end="\n")
        logger.error(">Estas usando Gtk+"+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
    else:
        logger.error("Debug: %s", e)
    sys.exit()

#Intenta crear el archivo del log

#CONFIGS

WRES, HRES  = int(config.get("GRAPHICS", "WRES")), int(config.get("GRAPHICS", "HRES"))
resdir      = maindir + "/" + config.get("DIRS", "respack")

logger.info("Resdir: %r", resdir)

#CLASSES

allkeys = set()
cables = []
clicked = 0
bttnclicked = 0
areweputtingcable = 0

class MainClase(Gtk.Window):
    def __init__(self):
        self.ventana = builder.get_object("window1")
        self.ventana.connect("key-press-event", self.on_key_press_event)
        self.ventana.connect("key-release-event", self.on_key_release_event)
        self.ventana.set_default_size(WRES, HRES)
        self.ventana.set_keep_above(bool(config.getboolean("GRAPHICS", "window-set-keep-above")))

        builder.get_object("Revealer1").set_reveal_child(bool(config.getboolean("GRAPHICS", "revealer-show-default")))

        i = int(config.get('GRAPHICS', 'toolbutton-size'))

        #Probablemente estas dos variables se puedan coger del builder de alguna manera, pero no se cómo.
        start = 3
        end   = 8
        jlist = ["Router.png", "Switch.png", "Cable.png", "Computer.png", "Hub.png"]
        for j in range(start, end):
            objtmp = builder.get_object("toolbutton" + str(j))
            objtmp.connect("clicked", self.toolbutton_clicked)
            objtmp.set_icon_widget(Gtk.Image.new_from_pixbuf(
                Gtk.Image.new_from_file(resdir + jlist[j-start]).get_pixbuf().scale_simple(i, i, GdkPixbuf.InterpType.BILINEAR)))
            objtmp.set_tooltip_text(jlist[j - start].replace(".png", ""))

        builder.get_object("imagemenuitem9").connect("activate", self.showcfgwindow)
        builder.get_object("imagemenuitem1").connect("activate", self.new)
        builder.get_object("imagemenuitem3").connect("activate", self.save)
        builder.get_object("imagemenuitem4").connect("activate", self.save)
        builder.get_object("imagemenuitem2").connect("activate", self.load)
        builder.get_object("imagemenuitem10").connect("activate", about().show)
        builder.get_object("show_grid").connect("toggled", self.togglegrid)

        ### EVENT HANDLERS###

        handlers = {
        "onDeleteWindow":             exiting,
        "onExitPress":                exiting,
        "onRestartPress":             restart,

        }
        builder.connect_signals(handlers)

        builder.get_object("toolbutton1").connect("clicked", objlst.show)

        self.ventana.show_all()

    class ObjLst():
        def __init__(self):
            self.view = builder.get_object("objetos_treeview")
            self.tree = Gtk.TreeStore(str, str)
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn("Objetos", renderer, text=0)
            self.view.append_column(column)
            column.set_sort_column_id(0)

            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn("Valor", renderer, text=1)
            column.set_sort_column_id(1)
            self.view.append_column(column)
            self.view.set_model(self.tree)
            self.view.show_all()

            self.revealer = builder.get_object("Revealer1")
            self.panpos = 100

        def append(self, obj, otherdata=None):
            '''SI OBJ YA ESTÁ, QUE AÑADA ATRIBUTOS A LA LISTA.'''
            if otherdata == None: otherdata = []
            it1 = self.tree.append(None, row=[obj.name, obj.objectype])
            it2 = self.tree.append(it1, row=["MAC", str(obj.macdir)])
            itc = self.tree.append(it1, row=["Conexiones", "{}/{}".format(
                len(obj.connections), obj.max_connections)])
            for i in otherdata:
                self.tree.append(it1, row=i)

            obj.trdic = {"MAC":it2, "Connections":itc}

            return it1

        def update(self, obj, thing, val):
            if thing in obj.trdic.keys():
                self.tree.set_value(obj.trdic[thing], 1, val)
            else:
                it = self.tree.append(obj.trlst, row=[thing, val])
                obj.trdic[thing] = it

        def upcon(self, obj):
            if not hasattr(obj, "trcondic"):
                obj.trcondic = {}
            #objlst.tree.append(self.trdic["Connections"], row=[self.name, self.objectype])
            self.tree.set_value(obj.trdic["Connections"], 1, "{}/{}".format(
                len(obj.connections), obj.max_connections))
            for i in obj.connections:
                if i in obj.trcondic.keys():
                    self.tree.set_value(obj.trcondic[i], 0, i.name)
                else:
                    r = self.tree.append(obj.trdic["Connections"], row=[i.name, ""])
                    obj.trcondic[i] = r

        def show(self, *args):
            rev = self.revealer.get_reveal_child()
            if rev:
                self.panpos = builder.get_object("paned1").get_position()

            builder.get_object("paned1").set_position(-1)
            self.revealer.set_reveal_child(not self.revealer.get_reveal_child())

        def set_value(self, *args):
            self.tree.set_value(*args)

        def delete(self, obj):
            self.tree.remove(obj.trlst)

    def showcfgwindow(self, *args):
        if not hasattr(self, "configWindow"):
            self.configWindow = cfgWindow()
        self.configWindow.show()

    #24/06 Eliminada startCable(), incluida en toolbutton_clicked

    @staticmethod
    def togglegrid(*widget):
        widget = widget[0]
        #global TheGrid #There is no need to use global
        obj = TheGrid.backgr_lay
        if widget.get_active() != True and obj.is_visible():
            obj.hide()
        else:
            obj.show()

    #Una función para gobernarlos a todos.
    @staticmethod
    def toolbutton_clicked(objeto):
        global clicked
        global bttnclicked
        global areweputtingcable
        if areweputtingcable != 0:
            areweputtingcable = 0
            push_elemento("Cancelada acción de poner un cable")

        if objeto.props.label == "toolbutton5":
            logger.debug("Y ahora deberiamos poner un cable")
            push_elemento("Ahora pulsa en dos objetos")
            areweputtingcable = "True"

        object_name = objeto.props.label
        clicked = True
        bttnclicked = object_name

    def on_key_press_event(self, widget, event):
        """ Lo que hace al pulsar una tecla """
        keyname = Gdk.keyval_name(event.keyval).upper() #El upper es por si está BLOQ MAYUS activado.
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            logger.debug("Key %s (%d) pulsada", keyname, event.keyval)
            logger.debug("Todas las teclas: %s", allkeys)
        if not keyname in allkeys:
            allkeys.add(keyname)
        if ("CONTROL_L" in allkeys) and ("Q" in allkeys):
            exiting(1)
        if ("CONTROL_L" in allkeys) and ("R" in allkeys):
            restart()
        if ("CONTROL_L" in allkeys) and ("U" in allkeys):
            logger.warning("HARD UPDATE")
            logger.info(allobjects)
            for obj in allobjects:
                obj.update()

        if ("CONTROL_L" in allkeys) and ("S" in allkeys):
            MainClase.save()
        if ("CONTROL_L" in allkeys) and ("L" in allkeys):
            MainClase.load()
            allkeys.discard("CONTROL_L")
            allkeys.discard("L")

        #Para no tener que hacer click continuamente
        if ("Q" in allkeys):
            self.toolbutton_clicked(builder.get_object("toolbutton3"))
        if "W" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton4"))
        if "E" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton5"))
        if "R" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton6"))
        if "T" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton7"))
        return keyname

    @staticmethod
    def on_key_release_event(widget, event):
        """Al dejar de pulsar la tecla deshace lo anterior."""
        keynameb = Gdk.keyval_name(event.keyval).upper()
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            logger.debug("Key %s (%d) released", keynameb, event.keyval)
        allkeys.discard(keynameb)

    @staticmethod
    def has_ip(objeto):
        """Comprueba si el objeto tiene una ip asignada"""
        return bool(objeto.IP != None)

    @staticmethod
    def save(widget=None):
        #global cables #There is no need to globalize it if you are only
        #global allobjects #reading it
        if widget == None:
            lscl = 0
        elif widget.get_label() == "gtk-save-as":
            logger.info("Guardando como")
            lscl = 1
        save.save(allobjects, cables, aslc=lscl)
        push_elemento("Guardando...")

    @staticmethod
    def load(*_):
        save.load(allobjects, cables)
        push_elemento("Cargando...")

    @staticmethod
    def new(*_):
        save.last = 0
        while len(allobjects) > 0:
            allobjects[0].delete(pr=0)
        while len(cables) > 0:
            cables[0].delete()

    #def new(*args):
    #    global cables
    #    global allobjects
    #    while len(allobjects) > 0:
    #        allobjects[0].delete(pr=0)

class YesOrNoWindow(Gtk.Dialog):
    """ Esta clase no es mas que un prompt que pide 'Si' o 'No' """
    def __init__(self, text, *args, Yest="Sí", Not="No"):

        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADEFILE)

        self.yesornowindow = self.builder.get_object("YesOrNoWindow")
        self.labeldialog = self.builder.get_object("YoN_label")
        self.nobutton = self.builder.get_object("YoN_No")
        self.yesbutton = self.builder.get_object("YoN_Yes")

        self.nobutton.connect("clicked", self.on_button_clicked)
        self.yesbutton.connect("clicked", self.on_button_clicked)

        self.labeldialog.set_text(text)
        self.yesbutton.set_label(Yest)
        self.nobutton.set_label(Not)

        self = self.yesornowindow

    def on_button_clicked(self, widget):
        pass

    def run(self):
        return self.yesornowindow.run()

    def destroy(self):
        self.yesornowindow.destroy()

objetocable1 = None

class Grid():
    """ Donde se visualizan los objetos """
    def __init__(self):
        #16/06/16 MAINPORT PASA A SER VARIAS LAYERS
        self.overlay    = builder.get_object("overlay1")
        self.mainport   = Gtk.Layout.new()
        self.cables_lay = Gtk.Layout.new()
        self.backgr_lay = Gtk.Layout.new()
        self.select_lay = Gtk.Layout.new() #Aparecer un fondo naranja en la cuadricula cuando se selcciona un objeto
        self.animat_lay = Gtk.Layout.new() #La capa de las animaciones de los cables
        self.overlay.add_overlay(self.backgr_lay)
        self.overlay.add_overlay(self.select_lay)
        self.overlay.add_overlay(self.cables_lay)
        self.overlay.add_overlay(self.animat_lay)
        self.overlay.add_overlay(self.mainport)

        self.viewport   = builder.get_object("viewport1")
        self.eventbox   = builder.get_object("eventbox1")
        self.eventbox.connect("button-press-event", self.clicked_on_grid)
        #self.viewport.get_hadjustment().set_value(800)

        self.wres = config.getint("GRAPHICS", "viewport-wres")
        self.hres = config.getint("GRAPHICS", "viewport-hres")
        self.sqres = config.getint("GRAPHICS", "viewport-sqres")
        self.overlay.set_size_request(self.wres*self.sqres, self.hres*self.sqres)

        #Modifica el color de fondo del viewport
        clr = hex_to_rgba(config.get("GRAPHICS", "viewport-background-color"))
        logger.info("CLR: %s", clr)
        self.viewport.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*clr))

        #13/07/16 Ahora esto va por cairo, mejooor.
        ### INICIO CAIRO

        width, height, sq = self.wres*self.sqres, self.hres*self.sqres, self.sqres
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.close_path ()
        ctx.set_source_rgba(0, 0,0, 1)
        ctx.set_line_width(1)

        for i in range(self.wres):
            ctx.move_to(i*sq, 0)
            ctx.line_to(i*sq, height)
        for i in range(self.hres):
            ctx.move_to(0, i*sq)
            ctx.line_to(width, i*sq)


        ctx.stroke()
        self.image = Gtk.Image.new_from_surface(surface)
        ### FINAL DE LO DE CAIRO

        self.backgr_lay.put(self.image, 0, 0)

        def subshow(widget):
            """Para que la posición inicial no sea arriba a la izquierda"""
            scrolled = builder.get_object("scrolledwindow1")
            scrolled.get_vadjustment().set_value(height/3)
            scrolled.get_hadjustment().set_value(width/3)

        if config.getboolean("GRAPHICS", "start-centered"):
            builder.get_object("window1").connect("show", subshow)
        self.overlay.show_all()
        self.contadorback = 0

    def moveto(self, image, x, y, *args, layout=None):
        if x < self.wres and y < self.hres:
            if layout == None:
                layout = self.mainport
            elif str(layout.__class__.__name__) == "Layout":
                layout = layout
            else:
                logger.info("layout.__class__.__name__ %s", layout.__class__.__name__)
            if image in layout.get_children():
                layout.move(image, x*self.sqres, y*self.sqres)
            else:
                layout.put(image, x*self.sqres, y*self.sqres)
        else:
            logger.debug("\033[31mError: Las coordenadas se salen del grid\033[00m")

    def clicked_on_grid(self, widget, event, *args):
        global clicked
        global bttnclicked
        global areweputtingcable
        self.contadorback += 1

        push_elemento("Clicked on grid @" + str(self.gridparser(event.x,
            self.wres)) + ", " + str(self.gridparser(event.y, self.hres)))

        if self.searchforobject(self.gridparser(event.x, self.wres),
            self.gridparser(event.y, self.hres)) == False:
            if clicked == 1:
                push_elemento(" ".join(["Clicked:", str(clicked), "bttnclicked:", str(bttnclicked)]))
                if bttnclicked == "Router":
                    Router(self.gridparser(event.x, self.wres),
                        self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto router")
                elif bttnclicked == "toolbutton4":
                    Switch(self.gridparser(event.x, self.wres),
                        self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto switch")
                elif bttnclicked == "toolbutton6":
                    Computador(self.gridparser(event.x, self.wres),
                        self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto Computador")
                elif bttnclicked == "toolbutton7":
                    Hub(self.gridparser(event.x, self.wres),
                        self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto Hub")

        elif self.searchforobject(self.gridparser(event.x, self.wres),
            self.gridparser(event.y, self.hres)) != False:
            push_elemento("Ahí ya hay un objeto, por favor selecciona otro sitio")
        else:
            logger.error("Error inesperado en la función searchforobject")
        clicked = 0
        bttnclicked = 0

        #Button: 1== Lclick, 2== Mclick
        #Para comprobar si es doble o triple click: if event.type == gtk.gdk.BUTTON_PRESS, o gtk.gdk_2_BUTTON_PRESS
        if event.button == 3:
            rclick_Object = self.searchforobject(self.gridparser(event.x,
                self.wres), self.gridparser(event.y, self.hres))
            if rclick_Object != False:
                rclick_Object.rclick(event)

        if areweputtingcable != 0:
            objeto = self.searchforobject(self.gridparser(event.x, self.wres),
                self.gridparser(event.y, self.hres))
            if objeto == False:
                push_elemento("Selecciona un objeto por favor")
            elif objeto != False:
                if len(objeto.connections) < objeto.max_connections:
                    if areweputtingcable == "True":
                        push_elemento("Ahora selecciona otro más")
                        areweputtingcable = "Secondstep"
                        global objetocable1
                        objetocable1 = objeto
                    elif areweputtingcable == "Secondstep":
                        push_elemento("Poniendo cable")
                        areweputtingcable = 0
                        global objetocable1
                        cable = Cable(objetocable1, objeto)
                        objeto.connect(objetocable1, cable)
                        objetocable1 = 0

                else:
                    push_elemento("Número máximo de conexiones alcanzado")

    def gridparser(self, coord, cuadrados, mode=0):
        """ Convertir coordenadas en pixeles a cuadrados """
        #TODO: Que no sea necesario llamarlo dos veces
        if mode == 0:
            partcoord = coord / self.sqres
            for i in range(cuadrados + 1):
                if partcoord < i: return i
        if mode == 1:
            return coord * self.sqres

    def resizetogrid(self, image):
        #Image debe ser una imagen gtk del tipo gtk.Image
        pixbuf = image.get_pixbuf()
        pixbuf = pixbuf.scale_simple(self.sqres, self.sqres,
            GdkPixbuf.InterpType.BILINEAR)
        image.set_from_pixbuf(pixbuf)

    #Una función para encontrarlos,
    @staticmethod #Actualizado 16/12/30
    def searchforobject(x, y): #Estoy llorando de lo bello que es ahora
        for i in allobjects:
            if i.x == x and i.y == y: return i
        return False

TheGrid = Grid()

#Clases de los distintos objetos. Para no escribir demasiado tenemos la clase ObjetoBase
#De la que heredaran las demas funciones
cnt_objects = 1
cnt_rows = 2
objlst = MainClase.ObjLst()

import uuid

class ObjetoBase():
    allobjects = []
    cnt = 0
    #Una función para atraerlos a todos y atarlos en las tinieblas
    def __init__(self, x, y, objtype, *args, name="Default", maxconnections=4, ip=None):
        global cnt_objects

        #IMPORTANTE: GENERAR UUID PARA CADA OBJETO
        #La v4 crea un UUID de forma aleatoria
        self.uuid = uuid.uuid4()
        logger.info("\033[96mUUID:\033[00m %s", self.uuid)
        self.build()

        allobjects.append(self)

        self.realx = x * TheGrid.sqres
        self.realy = y * TheGrid.sqres
        self.x = x -1
        self.y = y -1
        self.connections = []
        self.cables      = []
        self.max_connections = maxconnections

        #Algún día pasaré todos los algoritmos a algoritmos de busqueda binaria
        for f in os.listdir(resdir):
            if f.startswith(objtype) and ( f.endswith(".jpg") or f.endswith(".png") ):
                self.imgdir = resdir + f
                break

        self.image = gtk.Image.new_from_file(self.imgdir)
        self.resizetogrid(self.image)
        if name == "Default" or name == None:
            self.name = self.objectype + " " + str(self.__class__.cnt)
        else:
            self.name = name
        cnt_objects += 1
        self.__class__.cnt += 1

        TheGrid.moveto(self.image, self.x, self.y)
        self.image.show()

        self.macdir = mac()

        logger.debug("MAC: %s, %s, %s", str(self.macdir), int(self.macdir), "{0:b}".format(int(self.macdir)))
        if ip == None:
            logger.debug("No ip definida")
            self.ipstr = "None"

        #Ahora vamos con lo de aparecer en la lista de la izquierda,
        #aunque en realidad es un grid
        lista = objlst
        self.trlst = lista.append(self)
        self.image.set_tooltip_text("".join([self.name, " (", str(len(self.connections)),
            "/", str(self.max_connections), ")\n", self.ipstr]))

        self.window_changethings = w_changethings(self)
        self.builder.get_object("grid_rclick-name").connect("activate",
            self.window_changethings.show)

        self.cnt = 0 #Se me olvido que hace esta cosa

    def build(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADEFILE)
        self.menuemergente = self.builder.get_object("grid_rclick")
        self.builder.get_object("grid_rclick-disconnect_all").connect("activate", self.disconnect)
        self.builder.get_object("grid_rclick-delete").connect("activate", self.delete)
        self.builder.get_object("grid_rclick-debug").connect("activate", self.debug)

    def load(self):
        global cnt_objects
        self.build()
        self.connections = []
        self.cables = []
        cnt_objects += 1
        self.__class__.cnt += 1
        allobjects.append(self)
        self.image = gtk.Image.new_from_file(self.imgdir)
        self.resizetogrid(self.image)
        TheGrid.moveto(self.image, self.x-1, self.y-1)
        self.image.show()

        self.trlst = objlst.append(self)

        self.image.set_tooltip_text("".join([self.name, " (", len(self.connections),
            "/", self.max_connections, ")\n", self.ipstr]))
        self.window_changethings = w_changethings(self)
        self.builder.get_object("grid_rclick-name").connect("activate", self.window_changethings.show)

        logger.debug("CABLES %s", self.cables)

    #Esta funcion retorna una str cuando se usa el objeto. En lugar de <0xXXXXXXXX object>
    def __str__(self):
        return "".join(["<Tipo: ", self.objectype, " | Name: ", self.name, " | Pos: ", str(self.x), ", ", str(self.y), ">"])

    def debug(self, *args):
        logger.debug("DEBUG")
        logger.debug("MAC: %s, %s", self.macdir, int(self.macdir))

    def rclick(self, event):

        logger.debug("rclick en %s, %s, %s\n\t>Connections: %s",
            self.objectype, self.x, self.y, self.connections)
        self.rmenu = self.menuemergente
        if self.objectype == "Computer" and len(self.compcon()) > 0:
            self.builder.get_object("grid_rclick-sendpkg").show()
        else:
            self.builder.get_object("grid_rclick-sendpkg").hide()
        if len(self.connections) > 0:
            self.builder.get_object("grid_rclick-disconnect").show_all()
        else:
            self.builder.get_object("grid_rclick-disconnect").hide()
        self.rmenu.popup(None, None, None, None, event.button, event.time)

    @staticmethod
    def resizetogrid(image, *args):
        #Ver resizetogrid en Grid (clase)
        TheGrid.resizetogrid(image)

    def clickado(self, widget, event):
        logger.debug("Clickado en objeto %s@%s, %s", self, self.x, self.y)

    #Esta fucnión se encarga de comprobar a que ordenador(es) está conectado
    #en total, pasando por routers, hubs y switches.

    #Nota, hacer que compruebe que ordenadores tienen IP, y cuales no.
    def compcon(self, *args):
        passedyet = []
        comps     = []
        reself    = self

        def subcompcon(notself, *args):
            nonlocal passedyet
            nonlocal reself
            subcomps = []

            iterc = notself.connections
            #logger.debug(notself, "connections:", iterc)
            #next(iterc)

            for con in iterc:
                if con.uuid != reself.uuid and con.uuid not in [obj.uuid for obj in passedyet]:
                    passedyet.append(con)
                    #logger.debug(con)
                    if con.objectype == "Computer":
                        subcomps.append(con)
                    elif con.objectype == "Switch" or con.objectype == "Hub":
                        subcomps.extend(subcompcon(con))
                    else:
                        logger.debug("Saltado %s", con)
                #passedyet.append(con)

            #logger.debug("passedyet", passedyet)
            return subcomps

        comps.extend(subcompcon(self))

        if args == 1 or "Gtk" in str(args):
            logger.debug("Comps: %s", comps)
            logger.debug("\nCompsname: %s", [x.name for x in comps])

        return comps

    def isconnected(self, objeto):
        """Comprueba si un objeto está conectado a otro."""
        return bool(objeto in compcon(self))

    #TODO: Para no tener que actualizar todo, que compruebe el que cambió
    #TODO: !! Hacer que modifique el menu_emergente (Hecho a medias xds)
    #Nota !!: No puedes buscar un objeto en una lista, debes buscar sus atr.
    def update(self):
        logger.debug("\033[95m>>Updating\033[00m %s", self)
        logger.debug(self.builder.get_object("grid_rclick-disconnect"))
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")")
        objlst.set_value(self.trlst, 0, self.name)

        objlst.update(self, "MAC", str(self.macdir))
        for child in self.builder.get_object("grid_rclick-disconnect").get_submenu().get_children():
            if child.props.label.upper() != "TODOS":
                if child.link.uuid not in [x.uuid for x in self.connections]:
                    #logger.debug("Object", child.link.__repr__(), "in connections", self.connections)
                    child.hide()
                    child.destroy()
                else:
                    #logger.debug("Object", child.link.__repr__(), "in self.connections", self.connections)
                    pass

        objlst.upcon(self)

        logger.debug("\033[95m<<\033[00m")

    def connect(self, objeto, cable):
        tmp = Gtk.MenuItem.new_with_label(objeto.name)
        self.builder.get_object("grid_rclick-disconnect").get_submenu().append(tmp)
        tmp.show()
        tmp.connect("activate", self.disconnect)
        #link es un objeto vinculado al widget, luego es útil.
        tmp.link = objeto
        tmp2 = Gtk.MenuItem.new_with_label(objeto.name)

        if self.__class__.__name__ != "Switch" and self.__class__.__name__ != "Hub":
            tmp2.connect("activate", self.send_pck)
            tmp2.show()
        tmp2.link = objeto

        tmp = Gtk.MenuItem.new_with_label(self.name)
        objeto.builder.get_object("grid_rclick-disconnect").get_submenu().append(tmp)
        tmp.show()
        tmp.connect("activate", objeto.disconnect)
        tmp.link = self
        tmp2 = Gtk.MenuItem.new_with_label(self.name)

        if objeto.__class__.__name__ != "Switch" and objeto.__class__.__name__ != "Hub":
            tmp2.show()
            tmp2.connect("activate", objeto.send_pck)
        tmp2.link = self

        self.connections.append(objeto)
        self.cables.append(cable)
        #objlst.tree.append(self.trdic["Connections"], row=[objeto.name, objeto.objectype])

        objeto.connections.append(self)
        objeto.cables.append(cable)
        #objlst.tree.append(objeto.trdic["Connections"], row=[self.name, self.objectype])

        self.update()
        objeto.update()

        if objeto.__class__.__name__ == "Switch":
            logger.debug("Connecting {} to {}".format(objeto, self))
            objeto.connectport(self)
        if self.__class__.__name__ == "Switch":
            logger.debug("Connecting {} to {}".format(objeto, self))
            self.connectport(objeto)

    def disconnect(self, widget, *args, de=None):
        logger.debug("Cables: %s", self.cables)
        #QUICKFIX
        try:
            if widget.props.label.upper() == "TODOS" and de == None:
                de = "All"
            elif de == None:
                de = widget.link
        except AttributeError:
            logger.error("NO WIDGET AT DISCONNECT()")

        if de == "All":
            while len(self.connections) > 0:
                self.disconnect(widget, de=self.connections[0])

        else:
            objlst.tree.remove(self.trcondic[de])
            del self.trcondic[de]
            objlst.tree.remove(de.trcondic[self])
            del de.trcondic[self]

            de.connections.remove(self)
            self.connections.remove(de)

            iterc = iter(self.builder.get_object("grid_rclick-disconnect").get_submenu().get_children())
            next(iterc)
            logger.debug("\033[91mLinks\033[00m %s", [x.link for x in iterc])

            for cable in self.cables:
                if cable.fromobj == self or cable.toobj == self:
                    cable.delete()
                    break

            de.update()

            if self.__class__.__name__ == "Switch":
                self.disconnectport(de)
            elif de.__class__.__name__ == "Switch":
                de.disconnectport(self)

        self.update()

    def delete(self, *widget, pr=1):
        if pr == 1:
            yonW = YesOrNoWindow("¿Estás seguro de que quieres eliminar " + self.name + " definitivamente? El objeto será imposible de recuperar y te hechará de menos.")
            yonR = yonW.run()
            yonW.destroy()
        else:
            yonR = 1
        if yonR:
            self.disconnect(0, de="All")
            objlst.delete(self)
            self.image.destroy()
            allobjects.remove(self)

    def packet_received(self, pck, *args):
        """ La variable port será útil algún día """
        logger.debug("Hola, soy {} y he recibido un paquete, pero no sé que hacer con él".format(self.name))
        if config.getboolean("DEBUG", "packet-received"):
            logger.debug(">Pck: %s", pck)
            if pck.frame != None:
                logger.debug("\033[91m>>Atributos del paquete\033[00m")
                totalen = pck.lenght + 14*8
                wfr = bformat(pck.frame, (totalen+14)*8)
                logger.debug(">Wfr: %s", wfr)
                mac1 = "{0:0111b}".format(pck.frame)[0:6*8]
                logger.debug(">Mac: %s", int(mac1, 2))
                readmac = str(hex(int(mac1, 2))).strip("0x")
                logger.debug(":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])]).upper())

                logger.debug("<<Fin de los atributos")

class mac():
    def __init__(self, *args, macaddr=None, bits=48):
        #ToDo: Check that the MAC doesn't exist alredy
        if macaddr == None:
            tmp = self.genmac(bits=bits)

            self.int = tmp[0]
            self.str = tmp[1]
            self.bin = ("{0:0"+str(bits)+"b}").format(self.int)

    @staticmethod
    def genmac(bits=48, mode=None):
        """Por defecto se usa mac 48, o lo que es lo mismo, la de toa la vida"""
        #Nota, falta un comprobador de que la mac no se repita
        realmac = int("11" + str("{0:0"+ str(bits-2) +"b}").format(random.getrandbits(bits-2)), 2)
        readmac = str(hex(realmac)).upper().replace("0X", "")
        readmac = ":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])])
        if mode == 0:
            return realmac
        if mode == 1:
            return readmac
        else:
            return [realmac, readmac]

    def __str__(self):
        readmac = str(hex(self.int)).upper().replace("0X", "")
        return ":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])])

    def __bytes__(self):
        return Object.__bytes__(self)

    def __int__(self):
        return self.int
    def __index__(self):
        return self.int
    def list(self):
        return self.str.split(":")

npack = 0

class Router(ObjetoBase):
    cnt = 1
    def __init__(self, x, y, *args, name="Default"):
        self.objectype = "Router"
        push_elemento("Creado Objeto Router")

        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y

    def __del__(self, *args):
        push_elemento("Eliminado objeto")
        del self

### ESTO ERA NESTED DE SWITHC ###

class Port():
    def __init__(self, switch):
        self.id = switch.portid
        self.dic = switch.pdic
        self.all = switch.pall
        self.switch = switch
        self.connection = None
        self.all[self.id] = self
        self.dic[self.id] = self.connection
    def connect(self, connection):
        self.connection = connection
        self.dic[self.id] = self.connection
    def disconnect(self):
        self.connection = None
        self.dic[self.id] = self.connection
    def is_available(self):
        if self.connection == None:
            return True
        return False

class w_switch_table(Gtk.ApplicationWindow):
    def __init__(self, switch):
        self.link = switch
        builder = switch.builder
        builder.get_object("window_switch-table_button").connect("clicked", self.hide)
        builder.get_object("window_switch-table").connect("delete-event", self.hide)
        self.store = Gtk.ListStore(str, int, int, int)

        self.view = builder.get_object("window_switch-table-TreeView")
        self.view.set_model(self.store)
        for i, column_title in enumerate(["MAC", "Puerto", "TTL (s)"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            column.set_sort_column_id(i)
            self.view.append_column(column)
        self.ticking = False
        builder.get_object("window_switch-table").set_keep_above(True)

    def show(self, *a):
        self.ticking = True
        GObject.timeout_add(1001, self.tick)
        for row in self.store:
            row[2] = row[3] - time.time()
        self.link.builder.get_object("window_switch-table").show_all()

    def hide(self, window, *event):
        self.link.builder.get_object("window_switch-table").hide()
        self.ticking = False
        return True
    def append(self, lst):
        lst.append(lst[2])
        for row in self.store:
            row[2] = row[3] - time.time()
        logger.debug(lst)
        row = self.store.append(lst)
        logger.debug(self.view.get_property("visible"))
        if self.view.get_property("visible") == True:
            self.ticking = True
            GObject.timeout_add(1001, self.tick)

    def tick(self):
        for row in self.store:
            row[2] = row[3] - time.time()
            if row[2] <= 0:
                try:
                    self.store.remove(row.iter)
                    self.link.table.remove(row)
                except:
                    pass
        if len(self.store) == 0:
            self.ticking = False
        return self.ticking
    def remove(self, lst):
        for row in self.store:
            if row == lst:
                self.store.remove(row.iter)
                #self.link.table #<--- ???
                break

class Switch(ObjetoBase):
    cnt = 1
    #El objeto puerto

    def __init__(self, x, y, *args, name="Default", maxconnections=int(config.get("SWITCH", "def-max-connections"))):
        self.objectype = "Switch"
        self.portid = 0
        self.pdic = {}
        self.pall = {}

        push_elemento("Creado objeto Switch")
        self.imgdir = resdir + "Switch.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name, maxconnections=maxconnections)
        self.x = x
        self.y = y
        self.timeout = config.getint("SWITCH", "routing-ttl") #Segundos

        while self.portid < self.max_connections:
            self.portid += 1
            Port(self)

        self.table = [
        #[MAC, port, expiration]
        ]
        self.wtable = w_switch_table(self)
        child = Gtk.MenuItem.new_with_label("Routing Table")
        self.builder.get_object("grid_rclick").append(child)
        child.connect("activate", self.wtable.show)
        child.show()

        self.ch = child

    def load(self):
        ObjetoBase.load(self)
        del self.wtable
        self.table = []
        self.wtable = w_switch_table(self)

        del self.ch
        child = Gtk.MenuItem.new_with_label("Routing Table")
        self.builder.get_object("grid_rclick").append(child)
        child.connect("activate", self.wtable.show)
        child.show()

        self.ch = child

    def update(self):
        ObjetoBase.update(self)
        self.timeout = config.getint("SWITCH", "routing-ttl")


    def connectport(self, objeto):
        for port in self.pall:
            if self.pall[port].is_available():
                self.pall[port].connect(objeto)
                break
        logger.debug("Port dic: %s", self.pdic)

    def disconnectport(self, objeto):
        for p in self.pdic:
            logger.debug("i: {}, idx: {}".format(p, self.pdic[p]))
            if objeto == self.pdic[p]:
                self.pall[p].disconnect()
                break
        logger.debug(self.pdic)

    def packet_received(self, pck, *args, port=None):
        macd = "{0:0112b}".format(pck.frame)[0:6*8]
        macs = "{0:0112b}".format(pck.frame)[6*8+1:6*16+1]

        #LO PRIMERO: AÑADIRLO A LA TABLA
        readmac = str(hex(int(macs, 2))).upper().replace("0X", "")
        readmac = ":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])])

        for tab in self.table:
            if tab[2] <= time.time():
                logger.debug("Ha llegado tu hora")
                self.table.remove(tab)
                self.wtable.remove(tab)
            if tab[0] == int(macd, 2):
                logger.debug("TAB[0] == mcd")
                tab[2] = int(time.time()+self.timeout)
                for row in self.wtable.store:
                    logger.debug("%s, %s", row[0], tab[0])
                    if int(row[0].replace(":", ""), 16) == tab[0]:
                        row[3] = int(time.time()+self.timeout)
        if int(macs, 2) not in [x[0] for x in self.table]:
            tmp = [int(macs, 2), port, int(time.time()+self.timeout)]
            self.table.append(tmp)
            tmp = [readmac, port, int(time.time()+self.timeout)]
            self.wtable.append(tmp)

        ################################

        #ObjetoBase.packet_received(self, pck)

        ttl  = int(pck.str[64:72], 2)
        ttlnew = "{0:08b}".format(ttl-1)
        pck.str = "".join(( pck.str[:64], ttlnew, pck.str[72:] ))


        logger.debug("Soy {} y mi deber es entregar el paquete a {}".format(self.name, int(macd, 2)))
        logger.debug("El paquete llegó por el puerto  {}".format(port))
        dic = {}
        for i in self.connections:
            dic[int(i.macdir)] = i
        logger.debug("Connections MAC's: %s", dic)

        #Cambiamos los bits de macs
        #Si macd en conn, enviarle el paquete
        #Si existe una tabla de enrutamiento que contiene una ruta para macd, enviar por ahi
        #Si no, enviar al siguiente, y así
        logger.debug(">MAAAC: %s", int(macd, 2))
        if int(macd, 2) in dic and ttl > 0:
            pck.animate(self, dic[int(macd, 2)])

        elif int(macd, 2) in [x[0] for x in self.table] and ttl >= 0:
            for x in self.table:
                if x[0] == int(macd, 2):
                    pck.animate(self, self.pdic[x[1]])

        elif "Switch" in [x.objectype for x in self.connections] and ttl >= 0:
            logger.debug("Ahora lo enviamos al siguiente router")
            tmplst = self.connections[:] #Crea una nueva copia de la lista
            logger.debug(tmplst)
            for i in tmplst:
                if int(macs, 2) == int(i.macdir):
                    logger.debug("REMOVING %s", i)
                    tmplst.remove(i)
            try:
                tmplst.remove(*[x for x in tmplst if x.objectype == "Computer"])
            except TypeError:
                pass
            logger.debug("Tmplst: %s", tmplst)
            obj = choice(tmplst)
            logger.debug("Sending to: {}".format( obj))
            pck.animate(self, obj)

    def debug(self, *args):
        logger.debug(self.pdic)
        logger.debug("MyMac: {}".format( self.macdir))
        row_format ="{:>20}" * 3
        logger.debug(row_format.format("MAC", "NXT", "EXP s"))
        for row in self.table:
            if row[1] == None:
                row[1] = "None"
            if int(row[2]-time.time()) <= 0:
                self.table.remove(row)
            logger.debug(row_format.format(row[0], row[1], int(row[2]-int(time.time()))))

#¿Tengo permisos de escritura?, no se si tendré permisos
#Update: Si los tenía
class Hub(ObjetoBase):
    cnt = 1
    def __init__(self, x, y, *args, name="Default", maxconnections=4, ip=None):
        self.objectype = "Hub"
        push_elemento("Creado objeto Hub")
        self.imgdir = resdir + "Hub.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name,
            maxconnections=maxconnections, ip=ip)
        self.x = x
        self.y = y

    def packet_received(self, pck, *args): #, port=None):
        ttl  = int(pck.str[64:72], 2)
        #macs = "{0:0112b}".format(pck.frame)[6*8+1:6*16+1]
        ttlnew = "{0:08b}".format(ttl-1)
        pck.str = "".join(( pck.str[:64], ttlnew, pck.str[72:] ))
        if ttl >= 0:
            for obj in self.connections:
                pck.animate(self, obj)

class Computador(ObjetoBase):
    cnt = 1
    def __init__(self, x, y, *args, name="Default", maxconnections=1, ip=None):
        self.objectype = "Computer"

        push_elemento("Creado objeto Computador")
        self.img = resdir + "Comp.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y
        self.max_connections = maxconnections
        self.IP = ip

        self.pingwin = PingWin(self)
        self.builder.get_object("grid_rclick-sendpkg").connect("activate", self.pingwin.show)

        self.update()

    def load(self):
        ObjetoBase.load(self)
        self.pingwin = PingWin(self)
        self.builder.get_object("grid_rclick-sendpkg").connect("activate", self.pingwin.show)

    class ip():
        def __init__(self, *args, ipstr="None"):
            self.str = ipstr

        def __str__(self):
            return self.str

        def set_str(self, string):
            self.str = string
            self.parser(string, 0)

        def set_bin(self, binar):
            t = binar
            if "0b" not in str(t) and "." in str(t):
                self.bins = t
            elif "0b" in str(bin(t)) and "." not in str(bin(t)):
                self.bin = t
            else:
                logger.debug("Error: {}".format( t))
            self.parser(t, 1)

        #ip2p stands 4 'ip to parse'
        def parser(self, ip2p, mode):
            #mode 0: str2b
            if mode == 0:
                tmplst = ip2p.split(".")
                toreturn = []
                for i in tmplst:
                    i = int(i)
                    toreturn.append("{0:08b}".format(i))
                self.bins = ".".join(toreturn)
                self.bin = int(self.bins.replace(".", ""), base=2)
                return self.bins

            #mode 1: b2str
            elif mode == 1:
                if "0b" not in str(ip2p):
                    self.bin = bin(int(ip2p.replace(".", ""), base=2))
                    self.str = ".".join([str(int(i, base=2)) for i in ip2p.split(".")])
                elif "0b" in str(ip2p):
                    logger.debug("La ip %s es bin", ip2p)
                    tmp = str(ip2p).replace("0b", "")
                    n = 8
                    self.bins = ".".join([tmp[i * n:i * n+n] for i, blah in enumerate(tmp[::n])])
                    self.str = ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i, blah in enumerate(tmp[::n])])
            else:
                logger.debug("Debug: {}".format( mode))

    def update(self):
        ObjetoBase.update(self)
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")\n" + str(self.IP))
        #submenu1 = self.builder.get_object("grid_rclick-sendpkg").get_submenu() #If you need to update the submenu

        if self.IP != None:
            objlst.update(self, "IP", str(self.IP))

    #Ahora es cuando viene la parte de haber estudiado.
    #SÓLO ENVÍA PINGS, (ICMP)
    sub_N = 0
    def send_pck(self, *widget, to=None):
        global npack
        Sub_N = Computador.sub_N
        #nonlocal sub_N
        #de = self #Not used
        logger.debug("Widget: %s", widget)
        if to == None:
            to = widget[0].link

        logger.debug("fnc send_pck from {} to {}".format(self.name, to.name))

        if MainClase.has_ip(self) and MainClase.has_ip(to):
            pass
        else:
            logger.warning("Un objeto no tiene IP")
            yonW = YesOrNoWindow("Uno o los dos objetos no tienen dirección IP", Yest="OK", Not="Ok también")
            yonW.run()
            yonW.destroy()
            raise Exception("Un objeto no tiene IP") #Raise sólo para que no continúe con la función
        #Ambos deben tener direccion ip
        #def __init__(self, header, payload, trailer, cabel=None):
        ping = Ping.create(0, self.IP, to.IP)
        Sub_N += 1
        npack += 1

        logger.debug("PCK ICMP HEADER: {}".format( "{0:064b}".format(ping.icmp_header)))
        logger.debug("PCK IPHEADER: {}".format( "{0:0160b}".format(ping.ip_header)))

        logger.debug("MAC's: from: {}, to: {}".format( self.macdir, to.macdir))
        frame = eth(int(to.macdir), int(self.macdir), ping)
        frame.applytopack(ping)
        logger.debug("Pck frame: {}".format( ping.frame))

        ping.animate(self, self.connections[0])

        msg = "{} >Enviado ping a {}".format(time.strftime("%H:%M:%S"), str(to.IP))
        self.pingwin.statusbar.push(self.pingwin.statusbar.get_context_id(msg), msg)

    #Ver routing: https://en.wikipedia.org/wiki/IP_forwarding
    def packet_received(self, pck, *args, port=None):
        logger.debug("Hola, soy {} y he recibido un paquete en {}, tal vez tenga que responder".format( self.name, port ))
        #Si el tipo de ping es x, responder, si es y imprimir info
        if config.getboolean("DEBUG", "packet-received"):
            logger.debug(">Pck: {}".format(pck))
            if pck.frame != None:
                frame="{0:0111b}".format(pck.frame)
                logger.debug("\033[91m>>Atributos del paquete\033[00m")
                #totalen = pck.lenght + 14*8
                logger.debug("Frame: {}".format( bin(pck.frame)))
                mac1 = "{0:0111b}".format(pck.frame)[0:6*8]
                readmac = str(hex(int(mac1, 2))).strip("0x")
                logger.debug(">Mac1: {}".format( ":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])]).upper()))
                readmac = str(hex(int( "{0:011b}".format(pck.frame)[6*8+1:6*16+1] ,2))).strip("0x")
                logger.debug(">Mac2: {}".format( ":".join([readmac[i * 2:i * 2 + 2] for i, bl in enumerate(readmac[::2])]).upper()))
                logger.debug("EtherType: {}".format( int(frame[12*8+1:8*14+1], 2)))
                logger.debug("Resto==Bits: {}".format( int(frame[8*14+1::], 2)==pck.bits))
                logger.debug(pck.str)

                n, tmp = 8, pck.str[96:128]
                logger.debug("IPs: {}".format( ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i, blah in enumerate(tmp[::n])])))
                tmp = pck.str[128:160]
                logger.debug("IPd: {}".format( ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i, blah in enumerate(tmp[::n])])))

                logger.debug("<<Fin de los atributos")
        n, tmp = 8, pck.str[128:160]
        tmp = pck.str[128:160]
        #logger.debug(int(tmp, 2), int(self.IP))
        if int(tmp, 2) == int(self.IP):
            ty = int("{0:064b}".format(pck.icmp_header)[:8], 2)
            if ty == 8:
                logger.info("El paquete era para mí, voy a responder un gracias :D")
                ping = Ping.create(1, self.IP, int(pck.str[96:128], 2))
                frame = eth(int("{0:0112b}".format(pck.frame)[6*8+1:6*16+1], 2), int(self.macdir), ping)
                frame.applytopack(ping)

                ping.animate(self, self.connections[0])
            elif ty == 0:
                logger.info("De nada")
            else:
                logger.debug("ty es: {}".format( ty))

            msg = "{} >Recibido ping de {}".format(time.strftime("%H:%M:%S"), ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i, blah in enumerate(tmp[::n])]))
            self.pingwin.statusbar.push(self.pingwin.statusbar.get_context_id(msg), msg)

class Servidor(Computador):
    def __init__(self, x, y, *args, name="Default", maxconnections=1, ip=None):
        self.objectype = "Servidor"

        push_elemento("Creado objeto {}".format(self.objectype))
        self.img = resdir + "Server.*"
        Computador.__init__(self, x, y, self.objectype, name=name, maxconnections=maxconnections, ip=ip)
        self.x = x
        self.y = y
        self.max_connections = maxconnections
        self.IP = self.ip()

class Cable():
    """La clase para los objetos cable"""
    def __init__(self, fromo, to, *color):
        self.objectype = "Wire"
        self.fromobj = fromo
        self.toobj = to
        self.fromx = TheGrid.gridparser(fromo.x, TheGrid.wres, 1)
        self.fromy = TheGrid.gridparser(fromo.y, TheGrid.hres, 1)
        self.tox = TheGrid.gridparser(to.x, TheGrid.wres, 1)
        self.toy = TheGrid.gridparser(to.y, TheGrid.hres, 1)
        self.w   = max(abs(fromo.realx - to.realx), 3)
        self.h   = max(abs(fromo.realy - to.realy), 3)

        self.cair()

        self.x, self.y = min(fromo.x, to.x)-0.5, min(fromo.y, to.y)-0.5

        TheGrid.moveto(self.image, self.x, self.y, layout=TheGrid.cables_lay)
        logger.debug("Puesto cable en: %s;%s", self.x, self.y)

        self.image.show()

        cables.append(self)
        logger.debug("Todos los cables: %s", cables)

    def load(self):
        self.cair()
        self.image.show()
        cables.append(self)

        self.fromobj.connect(self.toobj, self)

    def cair(self):
        fromo = self.fromobj
        to    = self.toobj
        width, height = max(abs(self.fromobj.realx - self.toobj.realx), 3), max(abs(self.fromobj.realy - self.toobj.realy), 3)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        #ctx.scale(width, height)

        ctx.close_path ()

        if config.getboolean("DEBUG", "show-cable-rectangle"):
            ctx.set_source_rgba(0, 0, 1, 0.1) # Solid color
            ctx.rectangle(0, 0,width, height)
            ctx.fill()


        ctx.set_line_width(1.5)
        ctx.set_source_rgb(1, 0,0)
        if (fromo.x < to.x and fromo.y < to.y) or (fromo.x > to.x and fromo.y > to.y):
            ctx.move_to(0, 0)
            ctx.line_to(width, height)
        elif fromo.x == to.x:
            ctx.move_to(width/2, 0)
            ctx.line_to(width/2, height)
        elif fromo.y == to.y:
            ctx.move_to(0, height/2)
            ctx.line_to(width, height/2)
        else:
            ctx.move_to(0, height)
            ctx.line_to(width, 0)

        ctx.stroke()

        self.image = gtk.Image.new_from_surface(surface)
        self.x, self.y = min(fromo.x, to.x)-0.5, min(fromo.y, to.y)-0.5

        TheGrid.moveto(self.image, self.x, self.y, layout=TheGrid.cables_lay)

    def delete(self):
        cables.remove(self)

        self.fromobj.cables.remove(self)
        self.toobj.cables.remove(self)

        self.image.hide()
        logger.debug("\033[96mCable\033[00m %s\033[96mdeleted\033[00m", self)
        del self

save.classes = [ObjetoBase, Switch, Hub, Computador, Servidor, Cable]

#De momento sólo soportará el protocolo IPv4
class packet():
    def __init__(self, header, trailer, payload, cabel=None):
        logger.debug("Creado paquete de red")
        self.header = header
        self.payload = payload
        self.trailer = trailer
        #self.packet = header + payload + trailer

    def new_from_total(self, bits):
        logger.debug("Length (bits): {}".format( int(bin(bits)[18:33], 2)*8))
        logger.debug("Real length: {}".format( int(len(bin(bits))-2 )))
        self.bits = bits
        self.lenght = int(bin(bits)[18:33], 2)
        self.str = str("{0:0"+str(int(int(bin(bits)[18:33], 2)*8 ))+"b}").format(self.bits)
        logger.debug(self.str)

    def send(self, de):
        ##SIN TERMINAR##
        ##FALTA AÑADIR TODO LO DEL FRAME##
        if de.objectype == "Computador":
            to = de.connections[1]
        self.animate(de, to)

    #Siendo t=fps/s, v=px/s, v default = 84
    def animate(self, start, end, fps=30, v=200, color=None, port=None):
        if color == None:
            if self.color != None:
                color = self.color
            else:
                color = "#673AB7"
        from math import sqrt, pi
        #Long del cable
        try:
            cable = start.cables[[x.toobj for x in start.cables].index(end)]
        except ValueError:
            cable = start.cables[[x.fromobj for x in start.cables].index(end)]
        w, h = cable.w + TheGrid.sqres, cable.h + TheGrid.sqres
        x, y = cable.x*TheGrid.sqres-TheGrid.sqres/2, cable.y*TheGrid.sqres-TheGrid.sqres/2
        xi, yi = (start.x-0.5)*TheGrid.sqres-x, (start.y-0.5)*TheGrid.sqres-y
        r = sqrt(cable.w**2+cable.h**2) #Pixeles totales
        t=r/v #Tiempo en segundos que durara la animacion
        tf = int(fps*t) #Fotogramas totales
        spf = 1/fps #Segundos por fotograma

        sq = 12
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)
        ctx.close_path()
        ctx.set_source_rgba(0, 1,1, 1)
        ctx.arc(-sq/2, -sq/2, sq/2, 0,2*pi)
        ctx.fill()
        ctx.stroke()
        ctx.close_path()

        image = gtk.Image.new_from_surface(surface)
        TheGrid.animat_lay.put(image, x,y)
        TheGrid.animat_lay.show_all()

        f = 0
        x, y = xi, yi
        sx, sy = (w-TheGrid.sqres)/tf, (h-TheGrid.sqres)/tf
        if start.x > end.x:
            sx = -sx
        if start.y > end.y:
            sy = -sy

        def iteration():
            nonlocal f
            nonlocal x
            nonlocal y
            nonlocal ctx
            nonlocal surface
            nonlocal port
            if f <= tf:
                #Do things
                x += sx
                y += sy

                del ctx
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
                ctx=cairo.Context(surface)
                ctx.set_source_rgba(*hex_to_rgba(color))
                ctx.arc(x, y,sq/2, 0,2*pi)
                ctx.fill()
                image.set_from_surface(surface)

                f += 1
                return True
            else:
                del ctx
                image.destroy()
                del surface
                if end.__class__.__name__ == "Switch":
                    for p in end.pall:
                        if end.pall[p].connection == start:
                            port = p
                            break
                    logger.debug("PORT: {}".format( port))
                    end.packet_received(self, port=port)
                    return False
                end.packet_received(self, port=port)
                return False

        GObject.timeout_add(spf*1000, iteration)


        return True

    def __str__(self):
        return "<" + str(packet) + ">"

# ETHERNET LAYER #
#Usando DIX, más comun en IP
#Al ser emulado no es necesario CRC Checksum
#SIEMPRE 112 longitud (48*2+16)
class eth(packet):
    #Se crea el header
    def __init__(self, destmac, sourcemac, *pack, EtherType=0x0800):
        def corrector(mac):
            if isinstance(mac, str):
                mac2 = 0
                for x in mac.split(":"):
                    mac2 = mac2 << 8 | int(x, 16)
                return mac2
            elif isinstance(mac, int):
                return mac
            else:
                raise Exception("MAC ERROR")

        destmac = corrector(destmac)
        sourcemac = corrector(sourcemac)
        logger.debug("Destmac {0:048b}".format(destmac))

        self.macheader = (destmac << (6*8+1) | sourcemac) << 16 | EtherType
        logger.debug(int("{0:0111b}".format(self.macheader)[0:6*8], 2))

    #Se le añade la payload al frame
    def applytopack(self, pack):
        self.pack = pack
        logger.debug(">Mach: {}".format( bin(self.macheader).replace("0b", "")))
        logger.debug(">Pck: {}".format( pack))
        logger.debug("Pack.lenght: %s", pack.lenght)
        ret = (self.macheader << pack.lenght*8) | pack.bits
        pack.frame = ret
        pack.framesrt = None
        logger.debug("pack.len: {}, bits len: {}".format(pack.lenght*8, len(bin(pack.bits).strip("0b"))))
        logger.debug(">Ret: {}".format( bin(ret).replace("0b", "")))
        logger.debug(int("{0:0111b}".format(self.macheader)[0:6*8], 2))
        return ret

    def __str__(self):
        return str( bin(self.macheader) )

#Internet Layer
class icmp(packet):
    def __init__(self, ipheader, icmpheader, payload):
        logger.debug("Len: {}".format( int(bin(ipheader)[18:33], 2)-28))
        self.bits = (ipheader << 8*8 | icmpheader) << ( (int(bin(ipheader)[18:33], 2) -28) * 8) | payload #BITS 16a31 - 28
        packet.new_from_total(self, self.bits)

    def __str__(self):
        return self.str


### Application layer ###

#Estos paquetes pueden ser Request o Reply.
#El header es de 20 bytes, la payload es de 8 + datos opcionales, pero el estándar es 64 bits.
#Tipo de mensaje es 8 para request y 0 para reply. El ICMP es siempre 0.
class Ping(icmp):
    identifi = 0
    def __init__(self):
        pass

    def create(r, sourceip, desti_ip, *n, payload=int( 4.3*10**19 ) << 6 | 42, \
        flags=0b010, ttl=32):
        self = Ping()
        if r == 0:
            Type = 8
            self.color = "#4CAF50"
        if r == 1:
            Type = 0
            self.color = "#F44336"

        self.payload = payload

        vihltos   = 0b0100010100000000
        #20 Ipheader + 8 ICMPHEader + Payload
        lenght    = int( 20 + 8 + ( int(math.log(payload, 2))+1)/8 ) #In Bytes
        frag_off  = 0b0000000000000
        protocol  = 1
        checksum  = 0 #No es necesario porque no hay cables
        sourceip  = int(sourceip)
        desti_ip  = int(desti_ip)
        identific = Ping.identifi
        Ping.identifi += 1

        self.ip_header = (((((((((vihltos << 16 | lenght)<<16 | identific) << 3 | flags) << 13 | frag_off) \
        << 8 | ttl) << 8 | protocol) << 16 | checksum) << 32 | sourceip) << 32 | desti_ip)

        identifier = 1*2**15 + 42 * 2**8 + 42
        Code = 0
        self.icmp_header = ((((((((Type << 8) | Code)<< 16) | checksum) << 16) | identifier) << 16) | identific)
        self.pck = icmp(self.ip_header, self.icmp_header, self.payload)

        self.str = self.pck.str
        self.lenght = self.pck.lenght
        self.bits = self.pck.bits

        return self



#Ventana para configurar las variables de Config.ini
#Nota: Por terminar
class cfgWindow(MainClase):#MainClase):
    def __init__(self, *args):
        push_elemento("Invocada ventana de configuracion")
        logger.debug("Has invocado a la GRAN VENTANA DE CONFIGURACION <--- Boss")
        self.cfgventana = builder.get_object("cfgwindow")
        self.cfgventana.connect("key-press-event", self.on_key_press_event)
        self.cfgventana.connect("key-release-event", self.on_key_release_event)
        self.cfgventana.connect("delete-event", self.hidewindow)

        builder.get_object("button2").connect("clicked", self.save)

        self.eraselogs = builder.get_object("eraselogs")
        self.eraselogs.connect("clicked", self.borrarlogs)

        self.cfgbttn1 = builder.get_object("checkbutton1")
        self.cfgbttn1.connect("toggled", self.bttntoggled)
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            self.cfgbttn1.set_active(True)
        else:
            self.cfgbttn1.set_active(False)

        #booleans = {"print-key-pressed": "print-key-pressed"}

        #Todos los spinbuttons necesarios
        self.spinbuttons = [
            #[label, cfgsect, cfgkey, rangef, ranget, incrementf, increment],
            ["Win del wres", "GRAPHICS", "wres", 450, 1600, 5, 10],
            ["Win del hres", "GRAPHICS", "hres", 450, 1600, 5, 10],
            ["Wres del grid", "GRAPHICS", "viewport-wres", 20, 100, 1, 5],
            ["Hres del grid", "GRAPHICS", "viewport-hres", 15, 100, 1, 5],
            ["Res de los sq", "GRAPHICS", "viewport-sqres", 32, 128, 5, 10],
            ["Max logs", "DIRS", "Maxlogs", 3, 1000, 1, 5],
        ]
        self.createdspinbuttons = []

        self.spinnergrid = builder.get_object("graph")

        def forspin(spinner):
            spinbutton = Gtk.SpinButton.new(None, 0, 0)
            tmplst = spinner
            label = Gtk.Label.new(tmplst[0])

            self.spinnergrid.insert_row(1)

            #spinbutton.set_digits(0)
            spinbutton.set_numeric(True)
            spinbutton.set_range(tmplst[3], tmplst[4])
            spinbutton.set_increments(tmplst[5], tmplst[6])
            spinbutton.set_value(config.getfloat(tmplst[1], tmplst[2]))

            #attach(child, left, top, width, height)
            self.spinnergrid.attach(label, 0, 1, 1, 1)
            self.spinnergrid.attach(spinbutton, 1, 1, 1, 1)

            self.createdspinbuttons.append(spinbutton)

        for spinner in self.spinbuttons:
            forspin(spinner)

        #self.cfgventana.show_all()

    def show(self, *args):
        self.cfgventana.show_all()

    def on_key_press_event(self, widget, event):
        #global allkeys
        MainClase.on_key_press_event(self, widget, event)
        if "ESCAPE" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.cfgventana.hide()

        if ("CONTROL_L" in allkeys) and ("S" in allkeys):
            self.save()
        logger.debug(MainClase.on_key_press_event(self, widget, event))

    @staticmethod
    def on_key_release_event(widget, event):
        MainClase.on_key_release_event(widget, event)

    def bttntoggled(self, *args):
        if self.cfgbttn1.get_active() == True:
            push_elemento("print-key-pressed set True")
            config.set("BOOLEANS", "print-key-pressed", "True")
        if self.cfgbttn1.get_active() == False:
            push_elemento("print-key-pressed set False")
            config.set("BOOLEANS", "print-key-pressed", "False")

    @staticmethod
    def borrarlogs(*lala):
        #prompt = YesOrNoWindow("Seguro que quieres borrar los logs?")
        #if prompt.on_button_clicked(0) == True:
        push_elemento("Borrando logs")
        for the_file in os.listdir("logfiles/"):
            file_path = os.path.join("logfiles/", the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except e:
                logger.debug(e)

    def save(self, *args):
        #[label, cfgsect, cfgkey, rangef, ranget, incrementf, increment],
        logger.debug(self.createdspinbuttons)
        for i in range(len(self.createdspinbuttons)):
            tmplst = self.spinbuttons[i]
            config.set(tmplst[1], tmplst[2], int(self.createdspinbuttons[i].get_value()))

        push_elemento("Configuracion guardada")
        with open(configdir, 'w') as cfgfile:
            logger.debug("Guardando archivo de configuracion")
            try:
                config.write(cfgfile)
            except:
                logger.debug("Error al guardar la configuracion")

    @staticmethod
    def hidewindow(window, *event):
        window.hide()
        return True

class w_changethings(): #Oie tú, pedazo de subnormal, que cada objeto debe tener una...
    #O tal vez no sea necesario... A la hora de llamar a la función, espera ¿Con quien estoy hablando?
    #Nota, ver notas escritas en la mesa
    def __init__(self, objeto):
        self.window = objeto.builder.get_object("changethings")
        self.name_entry = objeto.builder.get_object("changethings_name-entry")
        self.imagebutton = objeto.builder.get_object("changethings_imagebutton")
        self.applybutton = objeto.builder.get_object("chg_apply")
        self.applybutton.connect("clicked", self.apply)
        self.cancelbutton = objeto.builder.get_object("chg_cancel")
        self.cancelbutton.connect("clicked", self.cancel)
        self.window.connect("delete-event", self.hidewindow)
        self.window.connect("key-press-event", self.on_key_press_event)
        self.window.connect("key-release-event", self.on_key_release_event)
        objeto.builder.get_object("chg_MAC-regen").connect("clicked", self.regenclicked)
        objeto.builder.get_object("chg_MAC-regen").set_image(gtk.Image.new_from_stock("gtk-refresh", 1))

        self.link = objeto
        self.image = Gtk.Image.new_from_pixbuf(objeto.image.get_pixbuf())

        def filter_ip(entry):
            PingWin.filter_ip(entry)

        def filter_numshex(widget):
            text = widget.get_text().strip()
            widget.set_text("".join([i for i in text if i in "0123456789ABCDEFabcdef"]))

        objeto.builder.get_object("changethings_entry-IP").connect("changed", filter_ip)

        for i in ["chg_MAC-entry" + str(x) for x in range(0, 5)]:
            objeto.builder.get_object(i).connect("changed", filter_numshex)

        if objeto.objectype != "Computer":
            objeto.builder.get_object("changethings_box-IP").destroy()
            objeto.builder.get_object("grid_label-IP").destroy()
        if objeto.objectype == "Switch" or objeto.objectype == "Hub":
            self.portspinner = Gtk.SpinButton.new_with_range(1, 20, 1)

        #self.applybutton.connect("clicked", self.apply)
        #self.cancelbutton.connect("clicked", self.cancel)

    def show(self, *widget):
        logger.debug("widget: {}".format( self.link))
        self.window.show_all()
        self.imagebutton.set_image(self.image)
        self.name_entry.set_text(self.link.name)
        tmplst = self.link.macdir.list()
        for i in tmplst:
            tmpentry = self.link.builder.get_object("chg_MAC-entry" + str(tmplst.index(i)))
            tmpentry.set_text(i)

        #Hacer que muestre/oculte los campos de "IP"
        if self.link.objectype == "Computer":
            try:
                self.link.builder.get_object("changethings_entry-IP").set_text(str(self.link.IP))
            except AttributeError: #Cuando no tiene una str definida
                raise
            except TypeError:
                raise
            except:
                raise
        else:
            pass

        if self.link.objectype == "Switch":
            self.portspinner.set_range(self.pall, 128)


    def apply(self, *_):
        #acuerdate tambien de terminar esto <<< ???
        #ToDo: Hacer que compruebe nombres de una banlist, por ejemplo "TODOS"
        yonR = None

        self.link.name = self.name_entry.get_text()
        logger.debug("MAC lst to apply: %s", [ self.link.builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(0, 6)] ])
        self.link.macdir.str = ":".join( [ self.link.builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(6)] ])
        self.link.macdir.int = int(self.link.macdir.str.replace(":", ""), 16)
        self.link.macdir.bin = "{0:048b}".format(self.link.macdir.int)
        if self.link.objectype == "Computer":
            try:
                iptemp = self.link.builder.get_object("changethings_entry-IP").get_text()
                if iptemp == "":
                    pass
                elif self.link.builder.get_object("changethings_entry-IP").tmp == 2:
                    self.link.IP = ip_address(iptemp)
                else:
                    yonW = YesOrNoWindow("{} no es una IP válida, por favor, introduzca una IP válida".format(iptemp), Yest="OK", Not="Ok también")
                    yonR = yonW.run()
                    yonW.destroy()
            except:
                logger.error(Exception)
                raise
        if self.link.objectype == "Hub" or self.link.objectype == "Switch":
            portspinner.set_range(len(self.link.objectype.connections), 128)

        logger.debug("self.link.name: %s", self.link.name)

        #self.link.image.set_tooltip_text(self.link.name + " (" + str(self.link.connections) + "/" + str(self.link.max_connections) + ")")
        self.link.update()
        self.window.hide()
        if yonR != None:
            self.show()

    def cancel(self):
        self.window.hide()

    @staticmethod
    def hidewindow(window, *event):
        window.hide()
        return True

    def on_key_press_event(self, widget, event):
        #global allkeys
        MainClase.on_key_press_event(self, widget, event)
        if "ESCAPE" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.window.hide()

    @staticmethod
    def on_key_release_event(widget, event):
        MainClase.on_key_release_event(widget, event)

    def regenclicked(self, widget):
        t = mac.genmac()[1].split(":")
        for i in t:
            tmpentry = self.link.builder.get_object("chg_MAC-entry" + str(t.index(i)))
            tmpentry.set_text(i)
            tmpentry.show()

class PingWin(Gtk.ApplicationWindow):
    def __init__(self, obj):
        self.link = obj
        builder  = obj.builder
        self.win = builder.get_object("PingWin")
        self.statusbar = builder.get_object("PingWin_Statusbar")
        self.entry = builder.get_object("PingWin_entry")
        self.entry.set_placeholder_text("192.168.1.XXX")
        self.ping = builder.get_object("PingWin_Button")

        self.ping.connect("clicked", self.do_ping)

        self.entry.connect("changed", self.filter_ip)
        self.win.connect("delete-event", self.destroy)

    @staticmethod
    def filter_ip(entry):
        if entry.get_text().strip("") == "":
            entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*hex_to_rgba("#E57373")))
        else:
            entry.tmp = 0
            text = entry.get_text().strip()
            entry.set_text("".join([i for i in text if i in "0123456789."]))
            if max( [len(x) for x in entry.get_text().split(".") ] ) > 3:
                entry.tmp = 1
            try:
                if max( [int(x) for x in entry.get_text().split(".") if x != ""]) > 254:
                    entry.tmp = 1
            except ValueError:
                pass
            except:
                raise
            if len([x for x in entry.get_text().split(".") if x != ""]) == 4 and entry.tmp==0:
                entry.tmp = 2
                entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*hex_to_rgba("#9CCC65")))

            if entry.tmp == 1:
                entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*hex_to_rgba("#E57373")))
            elif entry.tmp == 0:
                entry.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*hex_to_rgba("#FFA726")))

    def do_ping(self, widget):
        ip = self.entry.get_text()
        if self.entry.tmp == 2:
            logger.debug("Compcon: %s", self.link.compcon())
            to = None
            for x in self.link.compcon():
                if ip == str(x.IP):
                    to = x
                    logger.debug("IP: {} from {} in compcon {}".format(ip, to, self.link.compcon()))
                    Computador.send_pck(self.link, to=to)
                    break
            if to == None:
                yonW = YesOrNoWindow("La IP {} no se ha encontrado".format(ip), Yest="OK", Not="Ok también")
                yonW.run()
                yonW.destroy()

        else:
            yonW = YesOrNoWindow("{} no es una IP válida, por favor, introduzca una IP válida".format(ip), Yest="OK", Not="Ok también")
            yonW.run()
            yonW.destroy()

    def show(self, widget):
        self.win.show()
    @staticmethod
    def destroy(window, event):
        window.hide()
        return True

class about(Gtk.AboutDialog):
    def __init__(self):
        self.win = builder.get_object("AboutWindow")
        self.win.connect("delete-event", self.destroy)
        self.win.connect("response", self.destroy)
        self.win.add_credit_section("Tutores", ["Julio Sánchez"])
        #self.win.add_credit_section("Contribuidores", [""])
    def show(self, *args):
        self.win.show()
    def destroy(self, *args):
        self.win.hide()
        return True


#Esta clase te permitirá deshacer acciones, algún día de un futuro lejano.
class Undo():
    def __init__(self):
        self.lastactions = []

#Esta la pongo fuera porque lo mismo la necesito en otra clase

def exiting(self, *ahfjah):
    logger.debug("End time: " + time.strftime("%H:%M:%S"))
    logger.debug("Window closed, exiting program")
    Gtk.main_quit()

def restart(*args):
    logger.info("End time: " + time.strftime("%H:%M%S"))
    logger.info("Restarting program")
    logger.info("\033[92m##############################\033[00m")
    os.execl(sys.executable, sys.executable, *sys.argv)

def leppard():
    print("Gunter glieben glauchen globen")

MainClase()

logger.info("Actual time: " + time.strftime("%H:%M:%S"))
logger.info("Complete load time: " + str(datetime.now() - startTime))
push_elemento("Parece que esta cosa ha arrancado en tan solo " + str(datetime.now() - startTime))
Gtk.main()

print("\033[92m##############################\033[00m")
