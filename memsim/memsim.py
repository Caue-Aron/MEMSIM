from .os import OS
import json

class MEMSIM:
    def __init__(self, config_path:str):
        self.target_fps = None

        ram_size = None
        disc_size = None

        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

            self.target_fps = config_data["setup"]["target_fps"]

            ram_size = config_data["setup"]["ram_size"]
            disc_size = config_data["setup"]["disc_size"]

        self.os = OS(ram_size, disc_size)