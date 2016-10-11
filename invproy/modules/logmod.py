#Tenia ganas de probar como va en Python esto de los modulos
import time, configparser, os
config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)

log = []
logdir = None
ret = 1
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
    global logdir
    global ret
    if ret:
        with open(logdir + "Log.log", "a") as logfile:
            logfile.writelines(log)
            log = []

def createlogfile():
    global logdir
    global ret
    if config.get("DIRS", "logdir") == "Default":
        if not os.path.exists("logfiles/"):
            try:
                os.makedirs("logfiles/")
                logdir = "logfiles/"
            except:
                logdir = "~/.invproy/logfiles/"
                if not os.path.exists(logdir):
                    try:
                        os.makedirs(logdir)
                    except:
                        print("No se ha podido crear {}".format(logdir))
                        ret = 0
        else:
            logdir = "logfiles/"
    else:
        logdir = config.get("DIRS", "logdir")
        if not os.path.exists(logdir):
            try:
                os.makedirs(logdir)
            except:
                ret = 0
    if ret:
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
            newlogfilename = logdir + time.strftime("%y%m%d%H%M%S") + ".log"
            try:
                os.rename("Log.log", newlogfilename)
            except:
                print('Ojo cuidao que no se ha podio renombrar <Log.log>')
        except:
            pass
