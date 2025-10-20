from .os import OS
from .program import Program
from .memory import Memory
import json

class MEMSIM:
    def __init__(self, config_path:str):
        self.target_fps = None
        self.os = None
        self.script = None

        programs = None
        ram_size = None
        disc_size = None

        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

            self.target_fps = config_data["setup"]["target_fps"]

            ram_size = config_data["setup"]["ram_size"]
            disc_size = config_data["setup"]["disc_size"]
            programs = config_data["script"]["programs"]

        self.os = OS(ram_size, disc_size)
        self.script = dict()
        for program in programs:
            pid = self.os.load_program(Program(program["initialize"]["data"]))
            self.script[pid] = program["timestamps"]

        self.dt = 0

    def get_state(self) -> Memory:
        return self.os.ram

    def step(self):
        for pid, program in self.script.items():
            for timestamps, action in program.items():
                if self.dt == int(timestamps):
                    command = next(iter(action))
                    param = action[command]

                    if command == "insert":
                        self.os.add_bytes_program(pid, param)

                    if command == "pop":
                        self.os.pop_bytes_program(pid, param)

                    if command == "terminate":
                        self.os.terminate_program(pid)

        self.dt += 1
