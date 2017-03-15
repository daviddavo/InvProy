import logging

format = "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
console_format = "%(asctime)s %(name)-14s %(levelname)-8s %(message)s"
loglevel = logging.DEBUG
logfile = "tmp.log"

logging.basicConfig(level=loglevel, filename=logfile, format=format)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter(console_format))

root = logging.getLogger("")
root.addHandler(console)

try:
    import coloredlogs
    coloredlogs.install(level=loglevel, logger=root, fmt=console_format)
except ModuleNotFoundError:
    pass

def getLogger(*args): return logging.getLogger(*args)

logger = getLogger(__name__)
logger.debug("Logfile: %s", logfile)
logger.info("Loglevel: %s", loglevel)