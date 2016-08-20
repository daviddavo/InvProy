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
from datetime import datetime
startTime = datetime.now()

import configparser, os, csv, sys, time, random, math
import xml.etree.ElementTree as xmltree
from ipaddress import ip_address
from random import choice

#Esto hace que el programa se pueda ejecutar fuera de la carpeta.
startcwd = os.getcwd()

try:
    os.chdir(os.path.dirname(sys.argv[0]))
except:
    pass

os.system("clear")
print("\033[91m##############################\033[00m")

print("InvProy  Copyright (C) 2016  David Davó Laviña\ndavid@ddavo.me   <http://ddavo.me>\n\
This program comes with ABSOLUTELY NO WARRANTY; for details go to 'Ayuda > Acerca de'\n\
This is free software, and you are welcome to redistribute it\n\
under certain conditions\n")

try: #Intenta importar los modulos necesarios
    #sys.path.append("Modules/")
    import Modules.Test
except:
    print("Error: No se han podido importar los modulos...")
    sys.exit()

#Aqui importamos los modulos del programa que necesitamos...

from Modules.logmod import *
from Modules import save

def lprint(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    print(*objects, sep=sep, end=end, file=file, flush=flush)
    thing=str()
    for i in objects:
        thing += str(i) + sep
    writeonlog(thing)

lprint("Start loading time: " + time.strftime("%H:%M:%S"))

try:
    #Importando las dependencias de la interfaz
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
except:
    lprint("Por favor, instala PyGObject en tu ordenador. \n  En ubuntu suele ser 'apt-get install python3-gi'\n  En Archlinux es 'pacman -S python-gobject'")
    sys.exit()

try:
    import cairo
except:
    print("Necesitas tener instalado cairo")
    print("Como es lógico, pon 'pacman -S python-cairo' en Archlinux")
    sys.exit()

#Definiendo un par de cosillas necesarias

gtk = Gtk
config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)
allobjects = []

#Funcion que convierte un numero a una str con [digits] cifras
def digitsnumber(number, digits):
    if len(str(number)) == digits:
        return str(number)
    elif len(str(number)) < digits:
        return  "0" * ( digits - len(str(number)) ) + str(number)
    else:
        return "-1"

#Convierte hexadecimal a RGBA tal y como Gdk lo requiere
def hex_to_rgba(value):
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join([v*2 for v in list(value)])
    (r1,g1,b1,a1)=tuple(int(value[i:i+2], 16) for i in range(0, 6, 2))+(1,)
    (r1,g1,b1,a1)=(r1/255.00000,g1/255.00000,b1/255.00000,a1)

    return (r1,g1,b1,a1)

print("#42FF37", hex_to_rgba("#42FF37"))

#Comprueba la integridad del pack de recursos
def checkres(recurdir):
    files = ["Cable.png", "Router.png", "Switch.png", "Computer.png", "Hub.png"]
    cnt = 0
    ss = []
    for i in files:
        if os.path.isfile(recurdir + i):
            cnt += 1
        else:
            ss.append(i)

    if not (cnt == len(files)):
        lprint("WARNING!!!!!111!!!11!!")
        lprint("Faltan archivos en resources/"+recurdir)
        lprint(ss)
        sys.exit()
    else:
        lprint("Estan todos los archivos")

checkres(config.get("DIRS", "respack"))

#Envia a la Statusbar informacion.
contador = 0
def push_elemento(texto):
    global contador
    varra1 = builder.get_object("barra1")
    data = varra1.get_context_id("Ejemplocontextid")
    testo = time.strftime("%H:%M:%S") + " | " + texto
    contador = contador + 1
    varra1.push(data, testo)
    writeonlog(texto)

#Retorna un entero en formato de bin fixed
def bformat(num, fix):
    if type(num) == int:
        return str(("{0:0" + str(fix) + "b}").format(num))
    else:
        return "ERR0R"

gladefile = "Interface2.glade"

try:
    builder = Gtk.Builder()
    builder.add_from_file(gladefile)
    writeonlog("Cargando interfaz")
    lprint("Interfaz cargada\nCargados un total de " + str(len(builder.get_objects())) + " objetos")
    xmlroot = xmltree.parse(gladefile).getroot()
    lprint("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0", end="")
    lprint(" | Usando Gtk+ "+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
except Exception as e:
    lprint("Error: No se ha podido cargar la interfaz.")
    if "required" in str(e):
        xmlroot = xmltree.parse(gladefile).getroot()
        lprint("Necesario Gtk+ "+ xmlroot[0].attrib["version"]+".0", end="\n")
        lprint(">Estas usando Gtk+"+str(Gtk.get_major_version())+"."+str(Gtk.get_minor_version())+"."+str(Gtk.get_micro_version()))
    else:
        lprint("Debug:", e)
    sys.exit()

#Intenta crear el archivo del log
createlogfile()

#CONFIGS

WRES, HRES  = int(config.get("GRAPHICS", "WRES")), int(config.get("GRAPHICS", "HRES"))
resdir      = config.get("DIRS", "respack")

lprint(resdir)

#CLASSES

allkeys = set()
cables = []
clickedobjects = set() #Creamos una cosa para meter los ultimos 10 objetos clickados. (EN DESUSO)
clicked = 0
bttnclicked = 0
areweputtingcable = 0

#Función a medias, esto añadirá un objeto a la cola de ultimos objetos clickados, por si luego queremos deshacerlo o algo.
def appendtoclicked(objeto):
    clickedobjects.insert(0, objeto)
    try:
        clickedobjects.remove(9)
    except:
        pass

class MainClase(Gtk.Window):
    def __init__(self):
        global resdir

        self.ventana = builder.get_object("window1")
        self.ventana.connect("key-press-event", self.on_key_press_event)
        self.ventana.connect("key-release-event", self.on_key_release_event)
        self.ventana.set_default_size(WRES, HRES)
        self.ventana.set_keep_above(bool(config.getboolean("GRAPHICS", "window-set-keep-above")))

        #Modifica el color de fondo del viewport
        clr = hex_to_rgba(config.get("GRAPHICS", "viewport-background-color"))
        builder.get_object("viewport1").override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(*clr))#clr[0], clr[1], clr[2], clr[3]))

        i = int(config.get('GRAPHICS', 'toolbutton-size'))

        #Probablemente estas dos variables se puedan coger del builder de alguna manera, pero no se cómo.
        start = 3
        end   = 8
        jlist = ["Router.png", "Switch.png", "Cable.png", "Computer.png", "Hub.png"]
        for j in range(start, end):
            objtmp = builder.get_object("toolbutton" + str(j))
            objtmp.connect("clicked", self.toolbutton_clicked)
            objtmp.set_icon_widget(Gtk.Image.new_from_pixbuf(Gtk.Image.new_from_file(resdir + jlist[j-start]).get_pixbuf().scale_simple(i, i, GdkPixbuf.InterpType.BILINEAR)))
            objtmp.set_tooltip_text(jlist[j - start].replace(".png", ""))

        global configWindow
        #configWindow = cfgWindow()

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
        "on_window1_key_press_event": nothing,
        "onRestartPress":             restart,
        
        }
        builder.connect_signals(handlers)

        self.ventana.show_all()

    def showcfgwindow(self, *args):
        global configWindow
        try:
            configWindow.show()
        except:
            configWindow = cfgWindow()
            configWindow.show()

    #24/06 Eliminada startCable(), incluida en toolbutton_clicked

    def togglegrid(self, *widget):
        widget = widget[0]
        global TheGrid
        obj = TheGrid.backgr_lay
        if widget.get_active() != True and obj.is_visible():
            obj.hide()
        else:
            obj.show()

    #Una función para gobernarlos a todos.
    def toolbutton_clicked(self, objeto):
        global clicked
        global bttnclicked
        global areweputtingcable
        if areweputtingcable != 0:
            areweputtingcable = 0
            push_elemento("Cancelada acción de poner un cable")

        if objeto.props.label == "toolbutton5":
            lprint("Y ahora deberiamos poner un cable")
            push_elemento("Ahora pulsa en dos objetos")
            areweputtingcable = "True"

        object_name = objeto.props.label
        clicked = True
        bttnclicked = object_name

    #Al pulsar una tecla registrada por la ventana, hace todo esto.
    def on_key_press_event(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval).upper() #El upper es por si está BLOQ MAYUS activado.
        global allkeys #Esta es una lista que almacena todas las teclas que están siendo pulsadas
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            lprint("Key %s (%d) pulsada" % (keyname, event.keyval))
            lprint("Todas las teclas: ", allkeys)
        if not keyname in allkeys:
            allkeys.add(keyname)
        if ("CONTROL_L" in allkeys) and ("Q" in allkeys):
            exiting(1)
        if ("CONTROL_L" in allkeys) and ("R" in allkeys):
            restart()
        if ("CONTROL_L" in allkeys) and ("U" in allkeys):
            global allobjects
            print("HARD UPDATE")
            print(allobjects)
            for obj in allobjects:
                obj.update()

        if ("CONTROL_L" in allkeys) and ("S" in allkeys):
            global allobjects
            MainClase.save()
        if ("CONTROL_L" in allkeys) and ("L" in allkeys):
            MainClase.load()
            allkeys.discard("CONTROL_L")
            allkeys.discard("L")
        if ("CONTROL_L" in allkeys) and ("D" in allkeys):
            theend()

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

    #Al dejar de pulsar la tecla deshace lo anterior.
    def on_key_release_event(self, widget, event):
        keynameb = Gdk.keyval_name(event.keyval).upper()
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            lprint("Key %s (%d) released" % (keynameb, event.keyval))
        global allkeys
        allkeys.discard(keynameb)

    def drag_drop(widget, context, x, y, time):
        push_elemento( "Drag drop at " + str(x) +"," + str(y) )

    #Comprueba si el objeto tiene una ip asignada
    def has_ip(self):
        try:
            if self.IP != None:
                return True
            else:
                return False
        except:
            return False

    def save(*args):
        global cables
        global allobjects
        lscl = 0
        try:
            if args[1].get_label() == "gtk-save-as":
                print("Guardando como")
                lscl = 1
        except:
            pass
        save.save(allobjects,cables, aslc=lscl)
        push_elemento("Guardando...")
    def load(*args):
        global cables
        global allobjects
        save.load(allobjects,cables)
        push_elemento("Cargando...")
    def new(*args):
        global allobjects
        global cables
        while len(allobjects) > 0:
            allobjects[0].delete(pr=0)
        while len(cables) > 0:
            cables[0].delete()

#Esta clase no es mas que un prompt que pide 'Si' o 'No'.
#La función run() retorna 1 cuando se clicka sí y 0 cuando se clicka no, así sirven como enteros y booleans.
class YesOrNoWindow(Gtk.Dialog):
    def __init__(self, text, *args, Yest="Sí", Not="No"):

        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladefile)

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
        dialog = self

    def run(self):
        return self.yesornowindow.run()
        self.yesornowindow.hide()

    def destroy(self):
        self.yesornowindow.destroy()

objetocable1 = None

#Esto es el Grid donde van las cosicas. A partir de aqui es donde esta lo divertido.
class Grid():
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

        #13/07/16 Ahora esto va por cairo, mejooor.
        ### INICIO CAIRO

        width, height, sq = self.wres*self.sqres, self.hres*self.sqres, self.sqres
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.close_path ()
        ctx.set_source_rgba(0,0,0,1)
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
            #Para que no aparezca arriba a la izquierda:
            scrolled = builder.get_object("scrolledwindow1")
            scrolled.get_vadjustment().set_value(height/3)
            scrolled.get_hadjustment().set_value(width/3)

        if config.getboolean("GRAPHICS","start-centered"):
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
                print("layout.__class__.__name__", layout.__class__.__name__)
            if image in layout.get_children():
                layout.move(image, x*self.sqres, y*self.sqres)
            else:
                layout.put(image, x*self.sqres, y*self.sqres)
        else:
            print("\033[31mError: Las coordenadas se salen del grid\033[00m")

    def clicked_on_grid(self, widget, event, *args):
        global clicked
        global bttnclicked
        global allobjects
        global areweputtingcable
        self.contadorback += 1

        push_elemento("Clicked on grid @" + str(self.gridparser(event.x, self.wres)) + "," + str(self.gridparser(event.y, self.hres)))

        if self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres)) == False:
            if clicked == 1:
                push_elemento("Clicked: " + str(clicked) + " bttnclicked: " + str(bttnclicked))
                if bttnclicked == "Router":
                    Router(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto router")
                elif bttnclicked == "toolbutton4":
                    Switch(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto switch")
                elif bttnclicked == "toolbutton6":
                    Computador(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto Computador")
                elif bttnclicked == "toolbutton7":
                    Hub(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto Hub")

        elif self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres)) != False:
            push_elemento("Ahí ya hay un objeto, por favor selecciona otro sitio")
        else:
            lprint("pls rebisa l codigo")
        clicked = 0
        bttnclicked = 0

        #Button: 1== Lclick, 2== Mclick
        #Para comprobar si es doble o triple click: if event.type == gtk.gdk.BUTTON_PRESS, o gtk.gdk_2_BUTTON_PRESS
        if event.button == 3:
            rclick_Object = self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
            if rclick_Object != False:
                rclick_Object.rclick(event)
            else:
                print("Agua")

        if areweputtingcable != 0:
            objeto = self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
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

    #Te pasa las cordenadas int que retorna Gtk a coordenadas del Grid, bastante sencillito. Tienes que llamarlo 2 veces, una por coordenada
    def gridparser(self, coord, cuadrados, mode=0):
        if mode == 0:
            partcoord = coord / self.sqres
            for i in range(cuadrados + 1):
                if partcoord < i:
                    return i
                else:
                    pass
        if mode == 1:
            return coord * self.sqres

    def resizetogrid(self, image):
        #Image debe ser una imagen gtk del tipo gtk.Image
        pixbuf = image.get_pixbuf()
        pixbuf = pixbuf.scale_simple(self.sqres, self.sqres, GdkPixbuf.InterpType.BILINEAR)
        image.set_from_pixbuf(pixbuf)

    #Una función para encontrarlos,
    def searchforobject(self, x, y):
        global allobjects
        localvar = False
        for i in range(len(allobjects)):
            if allobjects[i].x == x:
                if allobjects[i].y == y:
                    localvar = True
                    objeto = allobjects[i]
                    break
        if localvar == True:
            return objeto
        else:
            return False

    def __str__(self):
        lprint("No se que es esto")

TheGrid = Grid()

#Clases de los distintos objetos. Para no escribir demasiado tenemos la clase ObjetoBase
#De la que heredaran las demas funciones
cnt_objects = 1
cnt_rows = 2

import uuid

class ObjetoBase():
    allobjects = []
    cnt = 0
    #Una función para atraerlos a todos y atarlos en las tinieblas
    def __init__(self, x, y, objtype, *args, name="Default", maxconnections=4, ip=None):
        global cnt_objects
        global cnt_rows
        global allobjects
        global gladefile

        #IMPORTANTE: GENERAR UUID PARA CADA OBJETO
        #La v4 crea un UUID de forma aleatoria
        self.uuid = uuid.uuid4()
        print("\033[96mUUID:\033[00m", self.uuid)

        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladefile)
        self.menuemergente = self.builder.get_object("grid_rclick")
        self.builder.get_object("grid_rclick-disconnect_all").connect("activate", self.disconnect)
        self.builder.get_object("grid_rclick-delete").connect("activate", self.delete)
        self.builder.get_object("grid_rclick-debug").connect("activate", self.debug)

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
            lprint(f, f.startswith(objtype))
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

        self.macdir = self.mac()
        print("MAC:", self.macdir, int(self.macdir), bin(self.macdir))
        if ip == None:
            print("No ip definida")
            self.ipstr = "None"

        #Ahora vamos con lo de aparecer en la lista de la izquierda,
        #aunque en realidad es un grid
        lista = builder.get_object("grid2")
        lista.insert_row(cnt_rows)
        self.label = Gtk.Label.new(self.name)
        lista.attach(self.label, 0, cnt_rows, 1, 1)
        cnt_rows += 1
        #lprint(cnt_rows)
        self.label.show()
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")\n" + self.ipstr)

        self.window_changethings = w_changethings(self)
        self.builder.get_object("grid_rclick-name").connect("activate", self.window_changethings.show)

        self.cnt = 0 #Se me olvido que hace esta cosa

    def load(self):
        global cnt_objects
        global cnt_rows
        global allobjects
        self.builder = Gtk.Builder()
        self.builder.add_from_file(gladefile)
        self.menuemergente = self.builder.get_object("grid_rclick")
        self.builder.get_object("grid_rclick-disconnect_all").connect("activate", self.disconnect)
        self.builder.get_object("grid_rclick-delete").connect("activate", self.delete)
        self.builder.get_object("grid_rclick-debug").connect("activate", self.debug)
        self.connections = []
        self.cables = []
        cnt_objects += 1
        self.__class__.cnt += 1
        allobjects.append(self)
        self.image = gtk.Image.new_from_file(self.imgdir)
        self.resizetogrid(self.image)
        TheGrid.moveto(self.image, self.x-1, self.y-1)
        self.image.show()
        lista = builder.get_object("grid2")
        lista.insert_row(cnt_rows)
        self.label = Gtk.Label.new(self.name)
        lista.attach(self.label, 0, cnt_rows, 1, 1)
        cnt_rows += 1
        self.label.show()
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")\n" + self.ipstr)
        self.window_changethings = w_changethings(self)
        self.builder.get_object("grid_rclick-name").connect("activate", self.window_changethings.show)

        print("CABLES",self.cables)

    #Esta funcion retorna una str cuando se usa el objeto. En lugar de <0xXXXXXXXX object>
    def __str__(self):
        return  "<Tipo: " + self.objectype +" | Name: " + self.name + " | Pos: " + str(self.x) + ", " + str(self.y) + ">"

    def debug(self, *args):
        print("DEBUG")
        print("MAC:", self.macdir, int(self.macdir))

    def rclick(self, event):
        global rclick_Object
        rclick_Object = self

        print(self)
        lprint("rclick en", self.x, self.y, self.objectype, "\nConnections: ", end="")
        lprint(self.connections)
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

    def resizetogrid(self, image, *args):
        #Ver resizetogrid en Grid (clase)
        lprint(*args)
        TheGrid.resizetogrid(image)

    def clickado(self, widget, event):
        lprint("Clickado en objeto " + str(self) + " @ " + str(self.x) + ", " + str(self.y))

    class mac():
        def __init__(self, *macaddr, bits=48):
            print("macaddr:", *macaddr)
            if macaddr == None or True:
                tmp = self.genmac(bits=bits)

                self.int = tmp[0]
                self.str = tmp[1]
                self.bin = ("{0:0"+str(bits)+"b}").format(self.int)

        def genmac(*self, bits=48, mode=None):
            #Por defecto se usa mac 48, o lo que es lo mismo, la de toa la vida
            #Nota, falta un comprobador de que la mac no se repita
            realmac = int("11" + str("{0:0"+ str(bits-2) +"b}").format(random.getrandbits(bits-2)),2)
            readmac = str(hex(realmac)).upper().replace("0X", "")
            readmac = ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])])
            if mode == 0:
                return realmac
            if mode == 1:
                return readmac
            else:
                return [realmac, readmac]

        def __str__(self):
            readmac = str(hex(self.int)).upper().replace("0X", "")
            return ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])])

        def __bytes__(self):
            return Object.__bytes__(self)

        def __int__(self):
            return self.int
        def __index__(self):
            return self.int
        def list(self):
            return self.str.split(":")


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
            #print(notself, "connections:", iterc)
            #next(iterc)

            for con in iterc:
                if con.uuid != reself.uuid and con.uuid not in [obj.uuid for obj in passedyet]:
                    passedyet.append(con)
                    #print(con)
                    if con.objectype == "Computer":
                        subcomps.append(con)
                    elif con.objectype == "Switch" or con.objectype == "Hub":
                        subcomps.extend(subcompcon(con))
                    else:
                        print("Saltado", con)
                        pass
                #passedyet.append(con)

            #print("passedyet", passedyet)
            return subcomps

        comps.extend(subcompcon(self))

        try:
            #comps.remove(self)
            pass
        except:
            pass

        if args == 1 or "Gtk" in str(args):
            print("Comps:", comps)
            print("\nCompsname:", [x.name for x in comps])

        return comps

    #Comprueba si un objeto está conectado a otro.
    def isconnected(self, objeto):
        cons = compcon(self)
        if objeto in cons:
            return True
        else:
            return False

    #TODO: Para no tener que actualizar todo, que compruebe el que cambió
    #TODO: !! Hacer que modifique el menu_emergente (Hecho a medias xds)
    #Nota !!: No puedes buscar un objeto en una lista, debes buscar sus atr.
    def update(self):
        print("\033[95m>>Updating\033[00m", self)
        print(self.builder.get_object("grid_rclick-disconnect"))
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")")
        self.label.set_text(self.name)
        for child in self.builder.get_object("grid_rclick-disconnect").get_submenu().get_children():
            if child.props.label.upper() != "TODOS":
                if child.link.uuid not in [x.uuid for x in self.connections]:
                    print("Object", child.link.__repr__(), "in connections", self.connections)
                    child.hide()
                    child.destroy()
                else:
                    print("Object", child.link.__repr__(), "in self.connections", self.connections)
            pass
        print("\033[95m<<\033[00m")

    def connect(self, objeto, cable):
        #Permutado objeto y self para ver que tal va
        tmp = Gtk.MenuItem.new_with_label(objeto.name)
        self.builder.get_object("grid_rclick-disconnect").get_submenu().append(tmp)
        tmp.show()
        tmp.connect("activate", self.disconnect)
        #link es un objeto vinculado al widget
        tmp.link = objeto
        tmp2 = Gtk.MenuItem.new_with_label(objeto.name)
        self.builder.get_object("grid_rclick-sendpkg").get_submenu().append(tmp2)
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
        objeto.builder.get_object("grid_rclick-sendpkg").get_submenu().append(tmp2)
        if objeto.__class__.__name__ != "Switch" and objeto.__class__.__name__ != "Hub":
            tmp2.show()
            tmp2.connect("activate", objeto.send_pck)
        tmp2.link = self

        self.connections.append(objeto)
        self.cables.append(cable)

        objeto.connections.append(self)
        objeto.cables.append(cable)

        self.update()
        objeto.update()

        if objeto.__class__.__name__ == "Switch":
            print("Connecting {} to {}".format(objeto, self))
            objeto.connectport(self)
        if self.__class__.__name__ == "Switch":
            print("Connecting {} to {}".format(objeto, self))
            self.connectport(objeto)

    def disconnect(self, widget, *args, de=None):
        print("Cables:", self.cables)
        #QUICKFIX
        try:
            if widget.props.label.upper() == "TODOS" and de == None:
                de = "All"
            elif de == None:
                de = widget.link
        except:
            print("NO WIDGET AT DISCONNECT()")

        if de == "All":
            ###NO FUNCIONA DEL TODO BIEN, NO USAR###
            #Bug, el ultimo cable no se borra
            print("Ahora a desconectar de todos")
            while len(self.connections) > 0:
                self.disconnect(widget, de=self.connections[0])

        else:
            print(self.connections)
            print(de.__repr__())
            de.connections.remove(self)
            self.connections.remove(de)

            iterc = iter(self.builder.get_object("grid_rclick-disconnect").get_submenu().get_children())
            next(iterc)
            print("\033[91mLinks\033[00m", [x.link for x in iterc])

            if de in [x.link for x in iterc]:
                print("\033[91mSelf in\033[00m", self)

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

    def delete(self, *widget, conf=1, pr=1):
        if pr == 1:
            yonW = YesOrNoWindow("¿Estás seguro de que quieres eliminar " + self.name + " definitivamente? El objeto será imposible de recuperar y te hechará de menos.")
            yonR = yonW.run()
            yonW.destroy()
        else:
            yonR = 1
        if yonR == 1:
            self.disconnect(0, de="All")
            self.label.destroy()
            self.image.destroy()
            global allobjects
            allobjects.remove(self)
        elif yonR == 0:
            print("Piénsatelo dos veces")
        else:
            raise

    def packet_received(self, pck, *args, port=None):
        print("Hola, soy {} y he recibido un paquete, pero no sé que hacer con él".format(self.name))
        if config.getboolean("DEBUG", "packet-received"):
            print(">Pck:",pck)
            if pck.frame != None:
                print("\033[91m>>Atributos del paquete\033[00m")
                totalen = pck.lenght + 14*8
                wfr = bformat(pck.frame, (totalen+14)*8)
                print(">Wfr:",wfr)
                mac1 = "{0:0111b}".format(pck.frame)[0:6*8]
                print(">Mac:", int(mac1,2))
                readmac = str(hex(int(mac1,2))).strip("0x")
                print(":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])]).upper())

                print("<<Fin de los atributos")

npack = 0

class Router(ObjetoBase):
    cnt = 1
    def __init__(self, x, y, *args, name="Default"):
        global cnt_objects
        self.objectype = "Router"
        push_elemento("Creado Objeto Router")

        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y

    def __del__(self, *args):
        push_elemento("Eliminado objeto")
        del self

class Switch(ObjetoBase):
    cnt = 1
    #El objeto puerto
    class Port():
        def __init__(self, switch):
            self.id = switch.portid
            self.dic = switch.pdic
            self.all = switch.pall
            switch.portid += 1
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
            #builder.get_object("window_switch_hbox").override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(*hex_to_rgba("#FF9800")))
            builder.get_object("window_switch-table_button").connect("clicked", self.hide)
            builder.get_object("window_switch-table").connect("delete-event", self.hide)
            self.store = Gtk.ListStore(str,int,int,int)
            
            self.view = builder.get_object("window_switch-table-TreeView")
            self.view.set_model(self.store)
            for i, column_title in enumerate(["MAC", "Puerto", "TTL (s)"]):
                renderer = Gtk.CellRendererText()
                column = Gtk.TreeViewColumn(column_title, renderer, text=i)
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
            row = self.store.append(lst)
            print(self.view.get_property("visible"))
            if self.view.get_property("visible") == True and self.ticking == False:
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
                    self.link.table
            pass
            #Get children, if children.get_label() == MAC, delete it.

    def __init__(self, x, y, *args, name="Default", maxconnections=5):
        self.objectype = "Switch"
        self.portid = 0
        self.pdic = {}
        self.pall = {}

        push_elemento("Creado objeto Switch")
        self.imgdir = resdir + "Switch.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name, maxconnections=maxconnections)
        self.x = x
        self.y = y
        self.timeout = 20 #Segundos

        for p in range(self.max_connections):
            self.Port(self)
        print(self.pall)

        self.table = [
        #[MAC, port, expiration]
        ]
        self.wtable = self.w_switch_table(self)
        child = Gtk.MenuItem.new_with_label("Routing Table")
        self.builder.get_object("grid_rclick").append(child)
        child.connect("activate", self.wtable.show)
        child.show()

    def connectport(self, objeto):
        for port in self.pall:
            if self.pall[port].is_available():
                self.pall[port].connect(objeto)
                break
        print(self.pdic)

    def disconnectport(self, objeto):
        for p in self.pdic:
            print("i: {}, idx: {}".format(p,self.pdic[p]))
            if objeto == self.pdic[p]:
                self.pall[p].disconnect()
                break
        print(self.pdic)

    def packet_received(self, pck, port=None):
        macd = "{0:0112b}".format(pck.frame)[0:6*8]
        macs = "{0:0112b}".format(pck.frame)[6*8+1:6*16+1]

        #LO PRIMERO: AÑADIRLO A LA TABLA
        readmac = str(hex(int(macs,2))).upper().replace("0X", "")
        readmac = ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])])

        for tab in self.table:
            if tab[2] <= time.time():
                print("Ha llegado tu hora")
                self.table.remove(tab)
                self.wtable.remove(tab)
            if tab[0] == int(macd,2):
                print("TAB[0] == mcd")
                tab[2] = int(time.time()+self.timeout)
                for row in self.wtable.store:
                    print(row[0], tab[0])
                    if int(row[0].replace(":",""),16) == tab[0]:
                        row[3] = int(time.time()+self.timeout)
        if int(macs,2) not in [x[0] for x in self.table]:
            tmp = [int(macs,2), port, int(time.time()+self.timeout)]            
            self.table.append(tmp)
            tmp = [readmac, port, int(time.time()+self.timeout)]
            self.wtable.append(tmp)

        ################################

        #ObjetoBase.packet_received(self, pck)
        
        ttl  = int(pck.str[64:72],2)
        ttlnew = "{0:08b}".format(ttl-1)
        pck.str = "".join(( pck.str[:64], ttlnew, pck.str[72:] ))

        print("self.macdir",int(self.macdir), int("{0:0112b}".format(pck.frame)[6*8+1:6*16+1],2))
        print("TTL:", int(pck.str[64:72],2), pck.str[64:72])

        print("Soy {} y mi deber es entregar el paquete a {}".format(self.name,int(macd,2)))
        print("El paquete llegó por el puerto  {}".format(port))
        dic = {}
        for i in self.connections:
            dic[int(i.macdir)] = i
        print("Connections MAC's:", dic)

        #Cambiamos los bits de macs
        #Si macd en conn, enviarle el paquete
        #Si existe una tabla de enrutamiento que contiene una ruta para macd, enviar por ahi
        #Si no, enviar al siguiente, y así
        print(">MAAAC:",int(macd,2), "DIIIC:")
        if int(macd,2) in dic and ttl > 0:
            pck.animate(self, dic[int(macd,2)])

        elif int(macd,2) in [x[0] for x in self.table]:
            for x in self.table:
                if x[0] == int(macd,2):
                    pck.animate(self, self.pdic[x[1]])

        elif "Switch" in [x.objectype for x in self.connections] and ttl >= 0:
            print("Ahora lo enviamos al siguiente router")
            print(int(macd,2), dic)
            tmplst = self.connections[:] #Crea una nueva copia de la lista
            print(tmplst)
            for i in tmplst:
                if int(macs,2) == int(i.macdir):
                    print("REMOVING", i)
                    tmplst.remove(i)
            try:
                tmplst.remove(*[x for x in tmplst if x.objectype == "Computer"])
            except TypeError:
                pass
            print("Tmplst:", tmplst)
            obj = choice(tmplst)
            print("Sending to:", obj)
            pck.animate(self, obj)

    def debug(self, *args):
        print(self.pdic)
        print("MyMac:", self.macdir)
        row_format ="{:>20}" * 3
        print(row_format.format("MAC", "NXT", "EXP s"))
        for row in self.table:
            if row[1] == None:
                row[1] = "None"
            if int(row[2]-time.time()) <= 0:
                self.table.remove(row)
            print(row_format.format(row[0], row[1], int(row[2]-int(time.time()))))

#¿Tengo permisos de escritura?, no se si tendré permisos
#Update: Si los tenía
class Hub(ObjetoBase):
    cnt = 1
    def __init__(self, x, y, *args, name="Default", maxconnections=4, ip=None):
        self.objectype = "Hub"
        push_elemento("Creado objeto Hub")
        self.imgdir = resdir + "Hub.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y

    def packet_received(self,pck,port=None):
        ttl  = int(pck.str[64:72],2)
        macs = "{0:0112b}".format(pck.frame)[6*8+1:6*16+1]
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
        #self.IP = self.ip()
        self.IP = None

    class ip():
        def __init__(self, *args, ipstr="None"):
            self.str = ipstr

        def __str__(self):
            return self.str

        def set_str(self, str):
            self.str = str
            self.parser(str, 0)

        def set_bin(self, binar):
            t = binar
            print(bin(t))
            if "0b" not in str(t) and "." in str(t):
                print("Type is str")
                self.bins = t
            elif "0b" in str(bin(t)) and "." not in str(bin(t)):
                print("Type is binar")
                self.bin = t
            else:
                print("Error:", t)
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
                    print("La ip", ip2p, "es bin")
                    tmp = str(ip2p).replace("0b", "")
                    n = 8
                    self.bins = ".".join([tmp[i * n:i * n+n] for i,blah in enumerate(tmp[::n])])
                    self.str = ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i,blah in enumerate(tmp[::n])])
                else:
                    raise
            else:
                print("Debug:", mode)
                raise NameError('No mode defined')

    def update(self):
        ObjetoBase.update(self)
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")\n" + str(self.IP))
        self.label.set_text(self.name)
        submenu1 = self.builder.get_object("grid_rclick-sendpkg").get_submenu()
        print("Compcon: ", [x.name for x in self.compcon()])

        for child in submenu1.get_children():
            if child.link.__class__.__name__ == "Switch" or child.link.__class__.__name__ == "Hub":
                child.hide()
                for con in self.compcon():
                    if con.uuid not in [x.link.uuid for x in submenu1.get_children()]:
                        print("Not yet")
                        MeIt = Gtk.MenuItem.new_with_label(con.name)
                        MeIt.link = con
                        MeIt.connect("activate", self.send_pck)
                        submenu1.append(MeIt)
                        MeIt.show()
                        con.update()
                    else:
                        print("\033[91m",con, "ya está en submenu1\033[0m")
                        pass

                print("self.connections", self.connections)

    #Ahora es cuando viene la parte de haber estudiado.
    #SÓLO ENVÍA PINGS, (ICMP)
    sub_N = 0
    def send_pck(self, *widget, to=None):
        global npack
        Sub_N = Computador.sub_N
        #nonlocal sub_N
        de = self
        print(widget)
        if to == None:
            to = widget[0].link

        print("fnc send_pck from {} to {}".format(self.name, to.name))

        if MainClase.has_ip(self) and MainClase.has_ip(to):
            print("Continuando")
        else:
            print("Un objeto no tiene IP")
            yonW = YesOrNoWindow("Uno o los dos objetos no tienen dirección IP", Yest="OK", Not="Ok también")
            yonR = yonW.run()
            yonW.destroy()
            raise Exception("Un objeto no tiene IP")
        #Ambos deben tener direccion ip
        #def __init__(self, header, payload, trailer, cabel=None):
        ping = Ping.create(0, self.IP, to.IP)
        Sub_N += 1
        npack += 1

        print("PCK ICMP HEADER:", "{0:064b}".format(ping.icmp_header))
        print("PCK IPHEADER:", "{0:0160b}".format(ping.ip_header))

        print("MAC's:", self.macdir, to.macdir)
        frame = eth(int(to.macdir), int(self.macdir), ping)
        frame.applytopack(ping)
        print("Pck frame:", ping.frame)

        ping.animate(self, self.connections[0])

    #Ver routing: https://en.wikipedia.org/wiki/IP_forwarding
    def packet_received(self, pck, *args, port=None):
        print("Hola, soy {} y he recibido un paquete, tal vez tenga que responder".format(self.name))
        #Si el tipo de ping es x, responder, si es y imprimir info
        if config.getboolean("DEBUG", "packet-received"):
            print(">Pck:",pck)
            if pck.frame != None:
                frame="{0:0111b}".format(pck.frame)
                print("\033[91m>>Atributos del paquete\033[00m")
                totalen = pck.lenght + 14*8
                print("Frame:", bin(pck.frame))
                mac1 = "{0:0111b}".format(pck.frame)[0:6*8]
                readmac = str(hex(int(mac1,2))).strip("0x")
                print(">Mac1:", ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])]).upper())
                readmac = str(hex(int( "{0:011b}".format(pck.frame)[6*8+1:6*16+1] ,2))).strip("0x")
                print(">Mac2:", ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])]).upper())
                print("EtherType:", int(frame[12*8+1:8*14+1],2))
                print("Resto==Bits:", int(frame[8*14+1::],2)==pck.bits)
                print(pck.str)
                
                n, tmp = 8, pck.str[96:128]
                print("IPs:", ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i,blah in enumerate(tmp[::n])]))
                tmp = pck.str[128:160]
                print("IPd:", ".".join([str(int(tmp[i * n:i * n+n], base=2)) for i,blah in enumerate(tmp[::n])]))

                print("<<Fin de los atributos")
        n = 8
        tmp = pck.str[128:160]
        print(int(tmp,2), int(self.IP))
        if int(tmp,2) == int(self.IP):
            ty = int("{0:064b}".format(pck.icmp_header)[:8],2)
            if ty == 8:
                print("El paquete era para mí, voy a responder un gracias :D")
                ping = Ping.create(1, self.IP, int(pck.str[96:128],2))
                frame = eth(int("{0:0112b}".format(pck.frame)[6*8+1:6*16+1],2), int(self.macdir), ping)
                frame.applytopack(ping)

                ping.animate(self, self.connections[0])
            elif ty == 0:
                print("De nada")
            else:
                print("ty es:", ty)

class Servidor(Computador):
    def __init__(self, x, y, *args, name="Default", maxconnections=1, ip=None):
        self.objectype = "Servidor"

        push_elemento("Creado objeto {}".format(self.objectype))
        self.img = resdir + "Server.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y
        self.max_connections = maxconnections
        self.IP = self.ip()

#La clase para los objetos cable
class Cable():
    def __init__(self, fromo, to, *color):
        lprint("Argumentos sobrantes: ", *color)
        self.objectype = "Wire"
        self.fromobj = fromo
        self.toobj = to
        self.fromx = TheGrid.gridparser(fromo.x, TheGrid.wres,1)
        self.fromy = TheGrid.gridparser(fromo.y, TheGrid.hres,1)
        self.tox = TheGrid.gridparser(to.x, TheGrid.wres,1)
        self.toy = TheGrid.gridparser(to.y, TheGrid.hres,1)
        self.w   = max(abs(fromo.realx - to.realx),3)
        self.h   = max(abs(fromo.realy - to.realy),3)

        self.cair()

        self.x, self.y = min(fromo.x, to.x)-0.5, min(fromo.y, to.y)-0.5
        
        TheGrid.moveto(self.image, self.x, self.y, layout=TheGrid.cables_lay)
        lprint("Puesto cable en: ", self.x, "; ", self.y)

        self.image.show()

        global cables
        cables.append(self)
        lprint("Todos los cables: ", cables)

    def load(self):
        global cables
        self.cair()
        self.image.show()
        cables.append(self)

        self.fromobj.connect(self.toobj, self)

    def cair(self):
        fromo = self.fromobj
        to    = self.toobj
        width, height = max(abs(self.fromobj.realx - self.toobj.realx),3), max(abs(self.fromobj.realy - self.toobj.realy),3)
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)

        #ctx.scale(width, height)

        ctx.close_path ()

        if config.getboolean("DEBUG", "show-cable-rectangle"):
            ctx.set_source_rgba(0, 0, 1, 0.1) # Solid color
            ctx.rectangle(0,0,width,height)
            ctx.fill()
        

        ctx.set_line_width(1.5)
        ctx.set_source_rgb(1,0,0)
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
        global cables
        cables.remove(self)

        self.fromobj.cables.remove(self)
        self.toobj.cables.remove(self)

        self.image.hide()
        print("\033[96mCable\033[00m", self, "\033[96mdeleted\033[00m")
        del self

save.classes = [ObjetoBase, Switch, Hub, Computador, Servidor, Cable]

#Función debug
tmpvar = 0
def theend():
    from random import randrange
    global tmpvar
    global TestC
    global TestD

    scrolled = builder.get_object("scrolledwindow1")
    scrolled.get_vadjustment().set_value(0)
    scrolled.get_hadjustment().set_value(0)

    if tmpvar>0:
        TestC.send_pck(to=TestD)
        tmpvar += 1
        if tmpvar > 4:
            tmpvar = 1

    else:
        TestC = Computador(2,3, name="From")
        TestC.IP = ip_address("192.168.1.38")
        #TestC.IP.set_str("192.168.1.38")
        print("{0:031b}".format(int(TestC.IP)))

        TestD = Computador(8,3, name="To")
        #TestD.IP.set_str("192.168.1.42")
        TestD.IP = ip_address("192.168.1.42")
        print("{0:031b}".format(int(TestD.IP)))

        bridge = Switch(4, 3, name="Bridge")
        bridge2= Switch(6, 3, name="Bridge2")

        cable = Cable(TestC, bridge)
        cable2= Cable(bridge, bridge2)
        cable3= Cable(bridge2, TestD)
        TestC.connect(bridge, cable)
        bridge.connect(bridge2, cable2)
        TestD.connect(bridge2, cable3)

        tmpvar += 1

#De momento sólo soportará el protocolo IPv4
class packet():
    def __init__(self, header, trailer, payload, cabel=None):
        lprint("Creado paquete de res")
        self.header = header
        self.payload = payload
        self.trailer = trailer
        #self.packet = header + payload + trailer

    def new_from_total(self, bits):
        print("Length (bits):", int(bin(bits)[18:33],2)*8)
        print("Real length:", int(len(bin(bits))-2 ))
        self.bits = bits
        self.lenght = int(bin(bits)[18:33],2)
        self.str = str("{0:0"+str(int(int(bin(bits)[18:33],2)*8 ))+"b}").format(self.bits)
        print(self.str)

    def send(self, de):
        ##SIN TERMINAR##
        ##FALTA AÑADIR TODO LO DEL FRAME##
        if de.objectype == "Computador":
            to = de.connections[1]
        self.animate(de, to)

    #Composición de movimientos lineales en eje x e y
    #Siendo t=fps/s, v=px/s, v default = 84
    def animate(self, start, end, fps=120, v=200, color=None, port=None):
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
        xf, yf = end.x, end.y
        r = sqrt(cable.w**2+cable.h**2) #Pixeles totales
        t=r/v #Tiempo en segundos que durara la animacion
        tf = int(fps*t) #Fotogramas totales
        spf = 1/fps #Segundos por fotograma

        sq = 12
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
        ctx = cairo.Context(surface)
        ctx.close_path()
        ctx.set_source_rgba(0,1,1,1)
        ctx.arc(-sq/2,-sq/2,sq/2,0,2*pi)
        ctx.fill()
        ctx.stroke()
        ctx.close_path()

        image = gtk.Image.new_from_surface(surface)
        TheGrid.animat_lay.put(image,x,y)
        TheGrid.animat_lay.show_all()

        #print("x: {}, y: {}, tf:{}, spf*m:{}, t: {}".format(x/TheGrid.sqres,y/TheGrid.sqres,tf,int(spf*1000), t))
        f = 0
        x,y = xi,yi
        sx,sy = (w-TheGrid.sqres)/tf,(h-TheGrid.sqres)/tf
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
                #print("Current f: {}; x,y: {}, {}".format(f, x,y))
                x += sx
                y += sy

                del ctx
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
                ctx=cairo.Context(surface)
                ctx.set_source_rgba(*hex_to_rgba(color))
                ctx.arc(x,y,sq/2,0,2*pi)
                ctx.fill()
                image.set_from_surface(surface)

                f += 1
                return True
            else:
                del ctx
                image.destroy()
                del surface
                #print("Paquete enviado a {}".format(end))
                if end.__class__.__name__ == "Switch":
                    for p in end.pall:
                        if end.pall[p].connection == start:
                            port = p
                            break
                    print("PORT:", port)
                    end.packet_received(self,port=port)
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
            if type(mac) == str:
                mac2 = 0
                for x in mac.split(":"):
                    mac2 = mac2 << 8 | int(x, 16)
                return mac2
            elif type(mac) == int:
                return mac
            else:
                raise Exception("MAC ERROR")

        destmac = corrector(destmac)
        sourcemac = corrector(sourcemac)
        print("Destmac", "{0:048b}".format(destmac))

        self.macheader = (destmac << (6*8+1) | sourcemac) << 16 | EtherType
        print(int("{0:0111b}".format(self.macheader)[0:6*8],2))

    #Se le añade la payload al frame
    def applytopack(self, pack):
        self.pack = pack
        print(">Mach:", bin(self.macheader).replace("0b", ""))
        print(">Pck:", pack)
        print(pack.lenght)
        ret = (self.macheader << pack.lenght*8) | pack.bits
        pack.frame = ret
        pack.framesrt = None
        print("pack.len: {}, bits len: {}".format(pack.lenght*8, len(bin(pack.bits).strip("0b"))))
        print(">Ret:", bin(ret).replace("0b",""))
        print(int("{0:0111b}".format(self.macheader)[0:6*8],2))
        return ret

    def __str__(self):
        return str( bin(self.macheader) )
    
#Internet Layer
class icmp(packet):
    def __init__(self, ipheader, icmpheader, payload):
        print("Len:", int(bin(ipheader)[18:33],2)-28)
        self.bits = (ipheader << 8*8 | icmpheader) << ( (int(bin(ipheader)[18:33],2) -28) * 8) | payload #BITS 16a31 - 28
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
        icmp_header_checksum = random.getrandbits(16)
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
        writeonlog("Has invocado a la GRAN VENTANA DE CONFIGURACION <--- Boss")
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

        booleans = {"print-key-pressed": "print-key-pressed"}

        #TODO ESTO ES PARA LOS SPINNERS

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
        lprint("spinbuttons: " + str(len(self.spinbuttons)))
        self.spinnergrid = builder.get_object("graph")
        self.contadordespinbuttons = 0
        for spinner in range(len(self.spinbuttons)):
            #spinbutton = builder.get_object(spinner)
            spinbutton = Gtk.SpinButton.new(None, 0, 0)
            tmplst = self.spinbuttons[spinner]
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

            lprint(str(self.contadordespinbuttons) + str(tmplst))

            self.contadordespinbuttons += 1


        #self.cfgventana.show_all()

    def show(self, *args):
        self.cfgventana.show_all()

    def on_key_press_event(self, widget, event):
        #global allkeys
        MainClase.on_key_press_event(self,widget,event)
        if "ESCAPE" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.cfgventana.hide()

        if ("CONTROL_L" in allkeys) and ("S" in allkeys):
            self.save()
        lprint(MainClase.on_key_press_event(self,widget,event))

    def on_key_release_event(self, widget, event):
        MainClase.on_key_release_event(self, widget, event)

    def bttntoggled(self, *args):
        if self.cfgbttn1.get_active() == True:
            push_elemento("print-key-pressed set True")
            config.set("BOOLEANS", "print-key-pressed", "True")
        if self.cfgbttn1.get_active() == False:
            push_elemento("print-key-pressed set False")
            config.set("BOOLEANS", "print-key-pressed", "False")

    def borrarlogs(self, *lala):
        #prompt = YesOrNoWindow("Seguro que quieres borrar los logs?")
        #if prompt.on_button_clicked(0) == True:
        push_elemento("Borrando logs")
        for the_file in os.listdir("logfiles/"):
            file_path = os.path.join("logfiles/", the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except e:
                lprint(e)

    def save(self, *args):
        #[label, cfgsect, cfgkey, rangef, ranget, incrementf, increment],
        lprint(self.createdspinbuttons)
        for i in range(len(self.createdspinbuttons)):
            tmplst = self.spinbuttons[i]
            config.set(tmplst[1], tmplst[2], int(self.createdspinbuttons[i].get_value()))

        push_elemento("Configuracion guardada")
        with open(configdir, 'w') as cfgfile:
            lprint("Guardando archivo de configuracion")
            try:
                config.write(cfgfile)
            except:
                lprint("Error al guardar la configuracion")

    def hidewindow(self, window, *event):
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
        print(objeto.builder.get_object("chg_MAC-regen").set_image(gtk.Image.new_from_stock("gtk-refresh", 1)))

        self.link = objeto
        self.image = Gtk.Image.new_from_pixbuf(objeto.image.get_pixbuf())

        #Esto es un quick fix que hace que las entry sólo acepten números
        def filter_numsdec(widget):
            text = widget.get_text().strip()
            widget.set_text(''.join([i for i in text if i in '0123456789']))

        def filter_numshex(widget):
            text = widget.get_text().strip()
            widget.set_text("".join([i for i in text if i in "0123456789ABCDEFabcdef"]))

        for i in ["changethings_entry-IP" + str(x) for x in range(4)]:
            objeto.builder.get_object(i).connect("changed", filter_numsdec)

        for i in ["chg_MAC-entry" + str(x) for x in range(0,5)]:
            objeto.builder.get_object(i).connect("changed", filter_numshex)

        if objeto.objectype != "Computer":
            objeto.builder.get_object("changethings_box-IP").destroy()
            objeto.builder.get_object("grid_label-IP").destroy()

        #self.applybutton.connect("clicked", self.apply)
        #self.cancelbutton.connect("clicked", self.cancel)

    def show(self, *widget):
        print("widget:", self.link)
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
                tmplst = str(self.link.IP).split(".")
                print("TMPLST:", tmplst)
                for i in tmplst:
                    tmpentry = self.link.builder.get_object("changethings_entry-IP" + str( tmplst.index(i) ))
                    tmpentry.set_text(i)
            except AttributeError: #Cuando no tiene una str definida
                raise
                pass
            except TypeError:
                raise
                pass
            except:
                raise
        else:
            pass

    def apply(self, *npi):
        #acuerdate tambien de terminar esto
        #Nota: Hacer que compruebe nombres de una banlist, por ejemplo "TODOS"
        yonR = None
        lprint(npi)
        
        self.link.name = self.name_entry.get_text()
        lprint([ self.link.builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(0,6)] ])
        self.link.macdir.str = ":".join( [ self.link.builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(6)] ])
        self.link.macdir.int = int(self.link.macdir.str.replace(":",""), 16)
        self.link.macdir.bin = "{0:048b}".format(self.link.macdir.int)
        if self.link.objectype == "Computer":
            try:
                self.link.IP = ip_address(".".join( [ self.link.builder.get_object(y).get_text() for y in ["changethings_entry-IP" + str(x) for x in range(4)] ]))
            except ValueError:
                ip = ".".join( [ self.link.builder.get_object(y).get_text() for y in ["changethings_entry-IP" + str(x) for x in range(4)] ]) 
                if ip != "...":
                    print("No parece ser una IP válida:", ip)
                    yonW = YesOrNoWindow("{} no es una IP válida, por favor, introduzca una IP válida".format(ip), Yest="OK", Not="Ok también")
                    yonR = yonW.run()
                    yonW.destroy()
            except:
                print(Exception)
                raise

        lprint("self.link.name", self.link.name)

        #self.link.image.set_tooltip_text(self.link.name + " (" + str(self.link.connections) + "/" + str(self.link.max_connections) + ")")
        self.link.update()
        self.window.hide()
        if yonR!=None:
            self.show()

    def cancel(self, *npi):
        lprint(npi)
        self.window.hide()

    def hidewindow(self, window, *event):
        window.hide()
        return True

    def on_key_press_event(self, widget, event):
        #global allkeys
        MainClase.on_key_press_event(self,widget,event)
        if "ESCAPE" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.window.hide()

        if ("PERIOD" in allkeys) or ("KP_DECIMAL" in allkeys):
            widget.get_toplevel().child_focus(0)


    def on_key_release_event(self, widget, event):
        MainClase.on_key_release_event(self, widget, event)

    def regenclicked(self, widget):
        t = ObjetoBase.mac.genmac()[1].split(":")
        for i in t:
            tmpentry = self.link.builder.get_object("chg_MAC-entry" + str(t.index(i)))
            tmpentry.set_text(i)
            tmpentry.show()

class about(Gtk.AboutDialog):
    def __init__(self):
        self.win = builder.get_object("AboutWindow")
        self.win.connect("delete-event", self.destroy)
        self.win.connect("response", self.destroy)
        self.win.add_credit_section("Tutores", ["Julio Sánchez"])
        #self.win.add_credit_section("Contribuidores", [""])
        self = self.win
    def show(self, *args):
        print("Showing")
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
    global log
    savelog()
    lprint("End time: " + time.strftime("%H:%M:%S"))
    print ("Window closed, exiting program")
    Gtk.main_quit()

def restart(*args):
    global log
    savelog()
    lprint("End time: " + time.strftime("%H:%M%S"))
    lprint("Restarting program")
    print("\033[92m##############################\033[00m")
    os.chdir(startcwd)
    os.execl(sys.executable, sys.executable, *sys.argv)

def returnTrue(*lala):
    return True

def nothing(self, *args):
    #Funcion Hugo
    pass

def leppard():
    lprint("Gunter glieben glauchen globen")

writeonlog("Esto ha llegado al final del codigo al parecer sin errores")
writeonlog("O tal vez no")
MainClase()

#end()

lprint("Actual time: " + time.strftime("%H:%M:%S"))
lprint("Complete load time: " + str(datetime.now() - startTime))
push_elemento("Parece que esta cosa ha arrancado en tan solo " + str(datetime.now() - startTime))
Gtk.main()

print("\033[92m##############################\033[00m")
