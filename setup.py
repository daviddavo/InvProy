from setuptools import setup, find_packages
import os

try:
    LONG_DESCRIPTION = open("README.md").read()
except IOError:
    LONG_DESCRIPTION = __doc__

NAME = "Invproy"
VERSION = "0.2.3.1"
REQUIREMENTS = [
"ipaddress", "pygobject"]
EXTRA_REQUIREMENTS = { #Por ejemplo, cuando haya emulación
}

def recur(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        print(path, directories, filenames)
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

datafiles = []
datafiles.append( ("invproy/resources/Cisco", recur("invproy/resources/Cisco")) )
datafiles.append( ("invproy/resources/Seriouspack", recur("invproy/resources/Seriouspack")) )
datafiles.append( ("invproy/resources/Testpack", recur("invproy/resources/Testpack")) )
datafiles.append( ("invproy", ["invproy/Interface2.glade", "invproy/Config.ini", "invproy/Example.inv"]))
print("")
print(datafiles)

setup(
    include_package_data=True,
    name=NAME,
    version = VERSION,
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    extras_require=EXTRA_REQUIREMENTS,
    #data_files=data_files,
    #package_data={"invproy": ["resources/*", "Interface2.glade", "Config.ini, resources/Seriouspack/*"]},
    data_files=datafiles,

    author="David Davó",
    author_email="david@ddavo.me",
    description="Simulador de redes por y para alumnos",
    long_description=LONG_DESCRIPTION,
    url="https://github.com/daviddavo/InvProy",
    keywords="spanish, learning, network, simulator, MAX",
    license="GPL-3",
    entry_points={
        "gui_scripts": [
            "invproy = invproy.main"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Studients",
        "Programming Language :: Python"
    ]
)