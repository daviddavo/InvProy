 # -*- coding: utf-8 -*-
 #!/usr/bin/env python3
import configparser, os, csv, sys, time
import xml.etree.ElementTree as xmltree
from datetime import datetime
from copy import copy, deepcopy
startTime = datetime.now()

#Para cualquier duda: david@ddavo.me
os.system("clear")

try: #Intenta importar los modulos necesarios
    sys.path.append("Modules/")
    import Test
except:
    print("Error: No se han podido importar los modulos...")
    sys.exit()

#Aqui importamos los modulos del programa que necesitamos...

from logmod import *

def lprint(*objects, sep=" ", end="\n", file=sys.stdout, flush=False):
    print(*objects, sep=sep, end=end, file=file, flush=flush)
    thing=str()
    for i in objects:
        thing += str(i) + sep
    writeonlog(thing)

lprint("Start loading time: " + time.strftime("%H:%M:%S"))
try:
    #Importando las cosicas de la interfaz
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject, Gdk, GdkPixbuf
except:
    lprint("Por favor, instala PyGObject en tu ordenador. \n  En ubuntu suele ser 'apt-get install python3-gi'\n  En Archlinux es 'pacman -S python-gobject'")
    sys.exit()

sys.path.append("Modules/svgwrite")
import __init__ as svgwrite

try: #Intenta importar una libreria que puede no estar instalada
	#import svgwrite #Esto es para cuando el paquete lo distrubuya un administrador de paquetes...
    sys.path.append("Modules/svgwrite")
    import __init__ as svgwrite
    pass
except:
    lprint("Necesitas tener instalado svgwrite \nTan solo pon 'sudo pip3 install svgwrite'")
    lprint("Para instalar eso necesitas tener python3-pip")
    sys.exit()

#Definiendo un par de cosillas necesarias

gtk = Gtk
config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)

#Funcion que convierte un numero a una str con [digits] cifras
def digitsnumber(number, digits):
    if len(str(number)) == digits:
        return str(number)
    elif len(str(number)) < digits:
        return  "0" * ( digits - len(str(number)) ) + str(number)
    else:
        return "-1"

#Convierte hezadesimal a RGBA tal y como Gdk lo quiere
def hex_to_rgba(value):
    value = value.lstrip('#')
    if len(value) == 3:
        value = ''.join([v*2 for v in list(value)])
    (r1,g1,b1,a1)=tuple(int(value[i:i+2], 16) for i in range(0, 6, 2))+(1,)
    (r1,g1,b1,a1)=(r1/255.00000,g1/255.00000,b1/255.00000,a1)

    return (r1,g1,b1,a1)

#Comprueba la integridad del pack de recursos
def checkres(recurdir):
    files = ["Cable.png", "Router.png", "Switch.png", "Computer.png"]
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

#Imprime cosas al log. Movido a Modules/logmod.py 190216

#Prueba. Get la  version de Gtk necesaria.
gladefile = "Interface2.glade"

try:
    builder = Gtk.Builder()
    builder.add_from_file(gladefile)
    writeonlog("Cargando interfaz")
    count = 0
    for i in builder.get_objects():
        count += 1
        writeonlog("  " + digitsnumber(count, 2) +  str(i))
    lprint("Interfaz cargada\nCargados un total de " + str(count) + " objetos")
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

WRES        = int(config.get("GRAPHICS", "WRES"))
HRES        = int(config.get("GRAPHICS", "HRES"))
resdir      = config.get("DIRS", "respack")

lprint(resdir)

#CLASSES

allkeys = set()
allobjects = []
cables = []
clickedobjects = set() #Creamos una cosa para meter los ultimos 10 objetos clickados
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
        #self.ventana.connect("drag-drop", self.drag_drop)
        self.ventana.set_default_size(WRES, HRES)
        self.ventana.set_keep_above(bool(config.get("GRAPHICS", "window-set-keep-above")))

        i = int(config.get('GRAPHICS', 'toolbutton-size'))

        #Probablemente estas dos variables se puedan coger del builder de alguna manera, pero no se cómo.
        start = 3
        end   = 7
        jlist = ["Router.png", "Switch.png", "Cable.png", "Computer.png"]
        for j in range(start, end):
            objtmp = builder.get_object("toolbutton" + str(j))
            objtmp.connect("clicked", self.toolbutton_clicked)
            objtmp.set_icon_widget(Gtk.Image.new_from_pixbuf(Gtk.Image.new_from_file(resdir + jlist[j-start]).get_pixbuf().scale_simple(i, i, GdkPixbuf.InterpType.BILINEAR)))
            objtmp.set_tooltip_text(jlist[j - start].replace(".png", ""))

        global configWindow
        #configWindow = cfgWindow()

        builder.get_object("imagemenuitem9").connect("activate", self.showcfgwindow)

        ### EVENT HANDLERS & show ventana###

        handlers = {
        "onDeleteWindow":             exiting,
        "onExitPress":                exiting,
        "on_window1_key_press_event": nothing,
        "addbuttonclicked":           self.addbuttonclicked,
        "onRestartPress":             restart,
        "grid_rclick-name_activate":  w_changethings.show,
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

    ##### TODAS LAS FUNCIONES DE LA BOTONERA ####

    def addbuttonclicked(self, *args):
        global testelement
        global allobjects
        #testelement = Router(3, 1, 0)
        lprint("TODOS LOS OBJETOS:")
        for i in range(len(allobjects)):
            lprint(allobjects[i])

    #Esta va a ser la función definitiva creada para manejarlos a todos
    #Fue bastante más fácil de lo que pensaba.
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
        lprint("Object name", object_name)
        clicked = True
        bttnclicked = object_name

    #Al pulsar una tecla registrada por la ventana, hace todo esto.
    def on_key_press_event(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        global allkeys #Esta es una lista que almacena todas las teclas que están siendo pulsadas
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            lprint("Key %s (%d) pulsada" % (keyname, event.keyval))
            lprint("Todas las teclas: ", allkeys)
        if not keyname in allkeys:
            allkeys.add(keyname)
        if ("Control_L" in allkeys) and ("q" in allkeys):
            exiting(1)
        if ("Control_L" in allkeys) and ("r" in allkeys):
            restart()
        if ("Control_L" in allkeys) and ("u" in allkeys):
            #HARD UPDATE: DEBUG
            global allobjects
            print("HARD UPDATE")
            print(allobjects)
            for obj in allobjects:
                obj.update()

        #Para no tener que hacer click continuamente
        if ("q" in allkeys):
            self.toolbutton_clicked(builder.get_object("toolbutton3"))
        if "w" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton4"))
        if "e" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton5"))
        if "r" in allkeys:
            self.toolbutton_clicked(builder.get_object("toolbutton6"))
        return keyname

    #Al dejar de pulsar la tecla deshace lo anterior.
    def on_key_release_event(self, widget, event):
        keynameb = Gdk.keyval_name(event.keyval)
        if config.getboolean("BOOLEANS", "print-key-pressed") == True:
            lprint("Key %s (%d) released" % (keynameb, event.keyval))
        global allkeys
        allkeys.discard(keynameb)

    def drag_drop(widget, context, x, y, time):
        push_elemento( "Drag drop at " + str(x) +"," + str(y) )

    #Comprueba si el objeto tiene una ip asignada
    def has_ip(self):
        if self.ip != None:
            return True
        else:
            return False

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
        self.mainport = builder.get_object("fixed1")
        self.viewport = builder.get_object("viewport1")
        self.eventbox = builder.get_object("eventbox1")
        self.eventbox.connect("button-press-event", self.clicked_on_grid)
        #self.viewport.get_hadjustment()
        self.viewport.get_hadjustment().set_value(800)

        self.image0 = gtk.Image.new_from_file("resources/Back.png")
        self.wres = config.getint("GRAPHICS", "viewport-wres")
        self.hres = config.getint("GRAPHICS", "viewport-hres")
        self.sqres = config.getint("GRAPHICS", "viewport-sqres")
        self.mainport.set_size_request(self.wres * self.sqres, self.hres * self.sqres)

        #03/05/16 Ahora esto va por svgwrite, bieeeen.
        drawing = svgwrite.Drawing(size=( str(self.wres * self.sqres)+"px", str(self.hres * self.sqres)+"px"))
        for i in range(self.wres):
            linex = drawing.line(start=(i*self.sqres,0), end=(i*self.sqres,self.hres*self.sqres), stroke="black", stroke_width="1")
            drawing.add(linex)
        for i in range(self.hres):
            liney = drawing.line(start=(0, i*self.sqres), end=(self.wres*self.sqres, i*self.sqres), stroke="black")
            drawing.add(liney)

        encoded = drawing.tostring().encode()
        loader = GdkPixbuf.PixbufLoader()
        loader.write(encoded)
        loader.close()
        self.pixbuf = loader.get_pixbuf()
        #self.pixbufback0 = self.pixbuf.scale_simple(self.sqres, self.sqres, GdkPixbuf.InterpType.BILINEAR)
        self.image = gtk.Image.new_from_pixbuf(self.pixbuf)

        self.mainport.put(self.image, 0, 0)

        self.contadorback = 0

    def moveto(self, image, x, y):
        #image.destroy()
        self.mainport.put(image, x*self.sqres, y*self.sqres)

    def clicked_on_grid(self, widget, event, *args):
        global clicked
        global bttnclicked
        global allobjects
        global areweputtingcable
        self.contadorback += 1

        push_elemento("Clicked on grid @" + str(self.gridparser(event.x, self.wres)) + "," + str(self.gridparser(event.y, self.hres)))
        #lprint(str(self.contadorback) + " Clicked on grid " + str(args) + "@" + str(self.gridparser(event.x, self.wres)) + ", " + str(self.gridparser(event.y, self.hres)))

        if self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres)) == False:
            if clicked == 1:
                push_elemento("Clicked: " + str(clicked) + " bttnclicked: " + str(bttnclicked))
                if bttnclicked == "toolbutton3":
                    Router(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto router")
                elif bttnclicked == "toolbutton4":
                    Switch(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto switch")
                elif bttnclicked == "toolbutton6":
                    Computador(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
                    push_elemento("Creado objeto Computador")

        elif self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres)) != False:
            #lprint("Objeto encontrado: " + str(self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))))
            push_elemento("Ahí ya hay un objeto, por favor selecciona otro sitio")
        else:
            lprint("pls rebisa l codigo")
        clicked = 0
        bttnclicked = 0

        #Button: 1== Lclick, 2== Mclick
        #Para comprobar si es doble o triple click: if event.type == gtk.gdk.BUTTON_PRESS, o gtk.gdk_2_BUTTON_PRESS
        if event.button == 3:
            global rclick_Object
            rclick_Object = self.searchforobject(self.gridparser(event.x, self.wres), self.gridparser(event.y, self.hres))
            if rclick_Object != False:
                print(rclick_Object)
                lprint("rclick en", rclick_Object.x, rclick_Object.y, rclick_Object.objectype, "\nConnections: ", end="")
                lprint(rclick_Object.connections)
                self.rmenu = rclick_Object.menuemergente
                if rclick_Object.objectype == "Computer" and len(rclick_Object.connections) > 0:
                    rclick_Object.builder.get_object("grid_rclick-sendpkg").show()
                else:
                    rclick_Object.builder.get_object("grid_rclick-sendpkg").hide()
                if len(rclick_Object.connections) > 0:
                    rclick_Object.builder.get_object("grid_rclick-disconnect").show_all()
                else:
                    rclick_Object.builder.get_object("grid_rclick-disconnect").hide()
                self.rmenu.popup(None, None, None, None, event.button, event.time)

            else:
                lprint("Agua")

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
    #Asumiendo que el grid esta formado por cuadrados
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

    def searchforobject(self, x, y):
        global allobjects
        localvar = False
        for i in range(len(allobjects)):
            if allobjects[i].x == x:
                if allobjects[i].y == y:
                    localvar = True
                    objeto = allobjects[i]
                    break
                    #lprint("Objeto encontrado: " + str(objeto))
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

class ObjetoBase(MainClase):
    allobjects = []
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
        #self.builder.get_object("grid_rclick-disconnect").set_submenu(Gtk.Menu.new())
        self.builder.get_object("grid_rclick-disconnect_all").connect("activate", self.disconnect)
        self.builder.get_object("grid_rclick-delete").connect("activate", self.delete)
        self.builder.get_object("grid_rclick-debug").connect("activate", self.compcon)

        allobjects.append(self)

        #MainClase.__init__(self)
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
                imgdir = resdir + f
                break

        self.image = gtk.Image.new_from_file(imgdir)
        self.resizetogrid(self.image)
        if name == "Default" or name == None:
            self.name = self.objectype + " " + str(cnt_objects)
        else:
            self.name = name
        cnt_objects += 1
        self.obcnt += 1

        TheGrid.moveto(self.image, self.x, self.y)
        self.image.show()

        self.macdir = self.genmac()
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

        self.cnt = 0

        #Acuerdate de quitar esto:
        print('self.builder.get_object("grid_rclick-disconnect")', self.builder.get_object("grid_rclick-disconnect"))

    #Esta funcion retorna una str cuando se usa el objeto. En lugar de <0xXXXXXXXX object>
    def __str__(self):
        return  "<Tipo: " + self.objectype +" | Name: " + self.name + " | Pos: " + str(self.x) + ", " + str(self.y) + ">"

    def appendtoall(self):
        pass

    def resizetogrid(self, image, *args):
        #Ver resizetogrid en Grid (clase)
        lprint(*args)
        TheGrid.resizetogrid(image)

    def clickado(self, widget, event):
        lprint("Clickado en objeto " + str(self) + " @ " + str(self.x) + ", " + str(self.y))

    def genmac(self, *args, bits=48, mode=None):
        #Por defecto se usa mac 48, o lo que es lo mismo, la de toa la vida
        #Nota, falta un comprobador de que la mac no se repita
        import random
        realmac = random.getrandbits(bits)
        readmac = str(hex(realmac)).upper().replace("0X", "")
        readmac = ":".join([readmac[i * 2:i * 2 + 2] for i,bl in enumerate(readmac[::2])])
        if mode == 0:
            return realmac
        if mode == 1:
            return readmac
        else:
            return [realmac, readmac]

    #Esta fucnión se encarga de comprobar a que ordenador(es) está conectado
    #en total, pasando por routers, hubs y switches.
    def compcon(self, *args, first=None):
        passedyet = []
        comps     = []

        def subcompcon(self, *args, first=None):
            nonlocal passedyet
            subcomps = []

            for con in self.connections:
                if con not in passedyet:
                    if con.objectype == "Computer":
                        subcomps.append(con)
                    elif con.objectype == "Switch":
                        subcomps.extend(subcompcon(con, subcomps, passedyet))

                    passedyet.append(con)
                else:
                    pass

            print("passedyet", passedyet)
            return subcomps
        
        comps.extend(subcompcon(self, passedyet))

        try:
            #comps.remove(self)
            pass
        except:
            pass

        print(comps)
        for i in comps:
            print(self, "conected to", i)
        return comps


    #TODO: Actualizar la info de la barra de la izquierda
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

        tmp = Gtk.MenuItem.new_with_label(self.name)
        objeto.builder.get_object("grid_rclick-disconnect").get_submenu().append(tmp)
        tmp.show()
        tmp.connect("activate", objeto.disconnect)
        tmp.link = self

        self.connections.append(objeto)
        self.cables.append(cable)
        self.update()

        objeto.connections.append(self)
        objeto.cables.append(cable)
        objeto.update()

    def disconnect(self, widget, *args, de=None):
        global rclick_Object
        print("Cables:", self.cables)
        #QUICKFIX
        try:
            if widget.props.label.upper() == "TODOS" and de == None:
                de = "All"
            elif de == None:
                de = widget.link
        except:
            print("NO WIDGET AT DISCONNECT()")
        if rclick_Object == self:
            print(self, " <|> ",rclick_Object)
            if de == "All":
                ###NO FUNCIONA DEL TODO BIEN, NO USAR###
                #Bug, el ultimo cable no se borra
                print("Ahora a desconectar de todos")
                for connection in self.connections:
                    print("Connection:", connection)
                    self.disconnect(widget, de=connection)

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

            self.update()

    def delete(self, *widget, conf=1):
        yonW = YesOrNoWindow("¿Estás seguro de que quieres eliminar " + self.name + " definitivamente? El objeto será imposible de recuperar y te hechará de menos.")
        yonR = yonW.run()
        yonW.destroy()
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

class Router(ObjetoBase):
    obcnt = 1
    def __init__(self, x, y, *args, name="Default"):
        global cnt_objects
        self.objectype = "Router"
        push_elemento("Creado Objeto Router")

        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y

    def deleteobject(self, *kasfbkja):
        self.image.destroy()
        push_elemento("Eliminado objeto router")
        self.__del__()

    def __del__(self, *args):
        push_elemento("Eliminado objeto")
        del self

class Switch(ObjetoBase):
    obcnt = 1
    def __init__(self, x, y, *args, name="Default", maxconnections=4, ip=None):
        self.objectype = "Switch"

        push_elemento("Creado objeto Switch")
        self.imgdir = resdir + "Switch.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y

    def deleteobject(self, *jhafg):
        self.image.destroy()
        push_elemento("Eliminado objeto " + self.objectype)
        self.__del__()

#¿Tengo permisos de escritura?, no se si tendré permisos
#Update: Si los tenía
class Hub(ObjetoBase):
    def __init__(self, x, y, *args, name="Default", maxconnections=4, ip=None):
        self.objectype = "Hub"

        push_elemento("Creado objeto Hub")
        self.imgdir = resdir + "Hub.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=self.objectype)
        self.x = x
        self.y = y

class Computador(ObjetoBase):
    obcnt = 1
    def __init__(self, x, y, *args, name="Default", maxconnections=4, ip=None):
        self.objectype = "Computer"

        push_elemento("Creado objeto Hub")
        self.img = resdir + "Comp.*"
        ObjetoBase.__init__(self, x, y, self.objectype, name=name)
        self.x = x
        self.y = y
        self.max_connections = 1
        self.ip = self.ip()

    class ip():
        def __init__(self, *args, ipstr="None"):
            self.str = ipstr

        def __str__(self):
            return self.str

        def set_str(self, str):
            self.str = str
            self.parser(str, 0)

        def set_bin(self, binar):
            t = bin(binar)
            print(t)
            if "0b" not in str(t) and "." in str(t):
                print("Type is str")
                self.bins = t
            elif "0b" in str(t) and "." not in str(t):
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
                self.bin = bin(int(self.bins.replace(".", ""), base=2))
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
        self.image.set_tooltip_text(self.name + " (" + str(len(self.connections)) + "/" + str(self.max_connections) + ")\n" + self.ip.str)
        self.label.set_text(self.name)

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

        #Lo del maximo del absoluto es una forma simple de decirle que si el ancho es 0, ponga el ancho como 3.
        drawing = svgwrite.Drawing(size=( str( max(abs(fromo.realx - to.realx),3)) + "px", str( max(abs(fromo.realy - to.realy),3) ) + "px"), debug=True)
        #Esto es para DEBUG, acuérdate de comentarlo cuando no sea necesario
        drawing.add(drawing.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill="#3399FF", fill_opacity="0.1"))

        #Bueno, lo importante es que funciona xd
        if (fromo.x < to.x and fromo.y < to.y) or (fromo.x > to.x and fromo.y > to.y):
            line = drawing.line(start=(0,0), end=('100%','100%'), stroke=config.get("GRAPHICS", "cable-color"), stroke_width=1.5)
        elif fromo.x == to.x:
            line = drawing.line(start=('50%',0), end=('50%','100%'), stroke=config.get("GRAPHICS", "cable-color"), stroke_width=1.5)
        elif fromo.y == to.y:
            line = drawing.line(start=(0,'50%'), end=('100%','50%'), stroke=config.get("GRAPHICS", "cable-color"), stroke_width=1.5)
        else:
            line = drawing.line(start=(0,'100%'), end=('100%',0), stroke=config.get("GRAPHICS", "cable-color"), stroke_width=1.5)

        drawing.add(line)

        loader = GdkPixbuf.PixbufLoader()
        loader.write(drawing.tostring().encode())
        loader.close()
        self.pixbuf = loader.get_pixbuf()

        self.image = gtk.Image.new_from_pixbuf(self.pixbuf)

        TheGrid.moveto(self.image, min(fromo.x, to.x)-0.5, min(fromo.y, to.y)-0.5)
        #Esto es para que las imagenes esten por encima del cable, no te olvides de descomentarlo

        TheGrid.moveto(fromo.image, fromo.x-1, fromo.y-1)
        TheGrid.moveto(to.image, to.x-1, to.y-1)
        lprint("Puesto cable en: ", min(fromo.x, to.x), "; ", min(fromo.y, to.y))

        self.image.show()

        global cables
        cables.append(self)
        lprint("Todos los cables: ", cables)

    def delete(self):
        global cables
        cables.remove(self)

        self.fromobj.cables.remove(self)
        self.toobj.cables.remove(self)

        self.image.hide()
        print("\033[96mCable\033[00m", self, "\033[96mdeleted\033[00m")
        del self

#De momento sólo soportará el protocolo IPv4
class packet():
    def __init__(self, header, payload, trailer):
        lprint("Creado paquete de res")
        self.header = header
        self.payload = payload
        self.trailer = trailer

        drawing = svgwrite.Drawing(size=("50px", "50px"), debug=True)
        circle = drawing.circle(center=(25,25), r=5)
        drawing.add(circle)
        loader = GdkPixbuf.PixbufLoader()
        loader.write(drawing.tostring().encode())
        loader.close()
        self.pixbuf = loader.get_pixbuf()

        self.image = gtk.Image.new_from_pixbuf(self.pixbuf)
        TheGrid.moveto(self.image, 7, 7)
        self.image.show()

pckt = packet(1,2,3)

class icmp(packet):
    def __init__(self):
        pass

#Estos paquetes pueden ser Request o Reply.
#El header es de 20 bytes, la payload es de 8 + datos opcionales, pero el estándar es 64 bits.
#Tipo de mensaje es 8 para request y 0 para reply. El ICMP es siempre 0.
class ping(icmp):
    def __init__(self, r):
        if r == 0:
            self.tipo = 0
        if r == 1:
            self.tipo = 8

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
        if "Escape" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.cfgventana.hide()

        if ("Control_L" in allkeys) and ("s" in allkeys):
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
    def __init__(self):
        self.window = builder.get_object("changethings")
        self.name_entry = builder.get_object("changethings_name-entry")
        self.applybutton = builder.get_object("chg_apply")
        self.applybutton.connect("clicked", self.apply)
        self.cancelbutton = builder.get_object("chg_cancel")
        self.cancelbutton.connect("clicked", self.cancel)
        self.window.connect("delete-event", self.hidewindow)
        self.window.connect("key-press-event", self.on_key_press_event)
        self.window.connect("key-release-event", self.on_key_release_event)

        #Esto es un quick fix que hace que las entry sólo acepten números
        def filter_numsdec(widget):
            text = widget.get_text().strip()
            widget.set_text(''.join([i for i in text if i in '0123456789']))

        def filter_numshex(widget):
            text = widget.get_text().strip()
            widget.set_text("".join([i for i in text if i in "0123456789ABCDEFabcdef"]))

        for i in ["changethings_entry-IP" + str(x) for x in range(1,5)]:
            builder.get_object(i).connect("changed", filter_numsdec)

        for i in ["chg_MAC-entry" + str(x) for x in range(0,5)]:
            builder.get_object(i).connect("changed", filter_numshex)

        #self.applybutton.connect("clicked", self.apply)
        #self.cancelbutton.connect("clicked", self.cancel)

    def show(self, *args):
        global rclick_Object
        lprint(self, *args)

        self = window_changethings
        self.obj = rclick_Object
        self.window.show_all()
        self.name_entry.set_text(rclick_Object.name)
        lprint(rclick_Object.macdir[1])
        tmplst = rclick_Object.macdir[1].split(":")
        for i in tmplst:
            tmpentry = builder.get_object("chg_MAC-entry" + str(tmplst.index(i)))
            tmpentry.set_text(i)

        #Hacer que muestre/oculte los campos de "IP"
        if self.obj.objectype == "Computer":
            try:
                tmplst = rclick_Object.ip.str.split(".")
                for i in tmplst:
                    tmpentry = builder.get_object("changethings_entry-IP" + str(tmplst.index(i+1)))
                    tmpentry.set_text(i)
            except AttributeError: #Cuando no tiene una str definida
                pass
            except:
                raise
        else:
            pass

    def apply(self, *npi):
        #acuerdate tambien de terminar esto
        #Nota: Hacer que compruebe nombres de una banlist, por ejemplo "TODOS"
        lprint(npi)
        self.window.hide()
        self.obj.name = self.name_entry.get_text()
        lprint([ builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(0,5)] ])
        self.obj.macdir[1] = ":".join( [ builder.get_object(y).get_text() for y in ["chg_MAC-entry" + str(x) for x in range(5)] ])
        lprint(self.obj.macdir)
        self.obj.ip.set_str(".".join( [ builder.get_object(y).get_text() for y in ["changethings_entry-IP" + str(x) for x in range(1,5)] ]))
        print(self.obj.ip.str, self.obj.ip.bins, self.obj.ip.bin)

        lprint("self.obj.name", self.obj.name)

        #self.obj.image.set_tooltip_text(self.obj.name + " (" + str(self.obj.connections) + "/" + str(self.obj.max_connections) + ")")
        self.obj.update()

    def cancel(self, *npi):
        lprint(npi)
        self.window.hide()

    def hidewindow(self, window, *event):
        window.hide()
        return True

    def on_key_press_event(self, widget, event):
        #global allkeys
        MainClase.on_key_press_event(self,widget,event)
        if "Escape" in allkeys:
            push_elemento("Cerrada ventana de Configuracion")
            self.window.hide()

        if ("period" in allkeys) or ("KP_Decimal" in allkeys):
            widget.get_toplevel().child_focus(0)


    def on_key_release_event(self, widget, event):
        MainClase.on_key_release_event(self, widget, event)

window_changethings = w_changethings()

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

lprint("Actual time: " + time.strftime("%H:%M:%S"))
lprint("Complete load time: " + str(datetime.now() - startTime))
push_elemento("Parece que esta cosa ha arrancado en tan solo " + str(datetime.now() - startTime))
Gtk.main()

print("\033[92m##############################\033[00m")
