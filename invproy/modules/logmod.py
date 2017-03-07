#Tenia ganas de probar como va en Python esto de los modulos
import configparser, logging
from invproy.main import __home__
config      = configparser.RawConfigParser()
configfile   = "/".join([__home__, "Config.ini"])
logfile = "/".join([__home__, "invproy.log"])
config.read(configfile)

print(configfile)
print(config.sections())
loglevel = config["DEBUG"]["logging-print-level"]
loglevel = getattr(logging, loglevel.upper(), None)
logging.basicConfig(level=loglevel, filename=logfile,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    #datefmt='%m-%d %H:%M')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-7s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)