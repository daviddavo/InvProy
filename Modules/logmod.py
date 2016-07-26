#Tenia ganas de probar como va en Python esto de los modulos
import time, configparser, os
config      = configparser.RawConfigParser()
configdir   = "Config.ini"
config.read(configdir)

log = []
def writeonlog(thingtowrite, *otherthingstowrite):
    global log
    thingtowrite = time.strftime("%H:%M:%S") + "@" + thingtowrite
    try:
        thingtowrite += " | " + str(otherthingstowrite)
    except:
        pass
    log.append(thingtowrite + "\n")
    #if len(log) > 15:
    #    savelog()


def savelog():
    global log
    with open(config.get("DIRS", "Log"), "a") as logfile:
        logfile.writelines(log)
        log = []

def createlogfile():
    nlogfiles = int(len(os.listdir("logfiles/")))
    if nlogfiles >= int(config.get("DIRS", "Maxlogs")):
        #print(nlogfiles)
        #print(int(config.get("DIRS", "Maxlogs")) - nlogfiles)
        #for i in range(abs(nlogfiles - int(config.get("DIRS", "Maxlogs")))):
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
        newlogfilename = "logfiles/" + time.strftime("%y%m%d%H%M%S") + " " +  config.get("DIRS", "Log")
        try:
            os.rename("Log.log", newlogfilename)
        except:
            print('Ojo cuidao que no se ha podio renombrar <Log.log>')
    except:
        pass
