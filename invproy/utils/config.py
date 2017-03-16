import configparser, os

#Remove this:
invproy_folder, invproy_home_folder = "",""

config = configparser.RawConfigParser()
config_file_list = [
    os.path.join(invproy_home_folder, "Config.ini"),
    os.path.join(invproy_folder, "Config.ini")
]
config.read(os.path.join(invproy_folder))