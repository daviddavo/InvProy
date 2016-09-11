#Tenia ganas de probar como va en Python esto de los modulos
import time, configparser, os
config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)

log = []
logidr = None
def writeonlog(thingtowrite, *otherthingstowrite):
    global log
    global logdir
    thingtowrite = time.strftime("%H:%M:%S") + "@" + thingtowrite
    try:
        thingtowrite += " | " + str(otherthingstowrite)
    except:
        pass
    log.append(thingtowrite + "\n")

def savelog():
    global log
    with open(config.get("DIRS", "Log"), "a") as logfile:
        logfile.writelines(log)
        log = []

def createlogfile():
    if config.get("DIRS", "logdir") == "Default":
        if not os.path.exists("logfiles/"):
            try:
                os.makedirs("logfiles/")
                logdir = "logfiles/"
            except:
                logdir = "~/.invproy/logfiles/"
                if not os.path.exists(logdir)
                    try:
                        os.makedirs(logdir)
    else:
        logdir = config.get("DIRS", "logdir")

    nlogfiles = int(len(os.listdir(logdir)))
    if nlogfiles >= int(config.get("DIRS", "Maxlogs")):
        while nlogfiles > int(config.get("DIRS", "Maxlogs")):
            #Aqui pones que borre el archivo mas viejo
            nlogfiles -= 1
            log.append("Borrado: " + str(min(os.listdir("logfiles/")))+ "\n")
            try:
                os.remove("logfiles/" + min(os.listdir("logfiles/")))
            except OSError:
                print("\033[31mError de I/O en {}, borrar la carpeta de logfiles\033[00m".format(str(OSError.filename)))
            except:
                raise
    try:
        newlogfilename = logdir + time.strftime("%y%m%d%H%M%S") + " " +  config.get("DIRS", "Log")
        try:
            os.rename("Log.log", newlogfilename)
        except:
            print('Ojo cuidao que no se ha podio renombrar <Log.log>')
    except:
        pass
