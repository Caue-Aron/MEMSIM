from .os import OS
from .program import Program
from .memory import Memory, PROGRAM, HOLE
from .byte import Byte
import json
import random

INSERT = "insert"
POP = "pop"
TERMINATE = "terminate"

class MEMSIM:
    def __init__(self, config_path:str, auto_mode:bool=True):
        self.dt = 0
        self.running = True
        self.auto = auto_mode
        self.os = None
        self.script = None

        programs = None
        ram_size = None
        disc_size = None

        with open(config_path, "r") as config_file:
            config_data = json.load(config_file)

            ram_size = config_data["setup"]["ram_size"]
            disc_size = config_data["setup"]["disc_size"]
            programs = config_data["script"]["programs"]

        self.os = OS(ram_size, disc_size)
        self.script = dict()
        for program in programs:
            pid = self.os.load_program(Program(program["initialize"]["data"]))
            if self.auto:
                self.script[pid] = dict()
            else:
                self.script[pid] = program["timestamps"]

        if self.auto:
            self.prepare_next_step()

    def get_state(self) -> Memory:
        return self.os.ram
    
    def advance_sim(self, dt:int):
        for pid, program in self.script.items():
            for timestamps, action in program.items():
                if dt == int(timestamps):
                    command = next(iter(action))
                    param = action[command]

                    if command == INSERT:
                        self.os.add_bytes_program(pid, param)

                    if command == POP:
                        self.os.pop_bytes_program(pid, param)

                    if command == TERMINATE:
                        self.os.terminate_program(pid)

    def prepare_next_step(self):
        next_df = self.dt + 1
        unallocated_memory = self.os.ram.get_total_unallocated_memory()
        number_programs = sum(1 for _ in self.os.ram.get_all_segments_of_type(PROGRAM))
        allocated_memory = self.os.ram.get_total_allocated_memory()
        ram_size = self.os.ram.memory_size

        for idx, program in self.os.ram.get_all_segments_of_type(PROGRAM):
            choices = [INSERT for _ in range(1, int(unallocated_memory / number_programs))]
            choices.extend([POP for _ in range(1, int(allocated_memory / number_programs))])
            choices.extend([TERMINATE for _ in range(1, number_programs)])
            random.shuffle(choices)

            choice = random.choice(choices)
            param = None

            if choice == INSERT:
                segs = self.os.ram.get_all_segments_of_type("HOLE")
                seg_choices = list()
                for idx, hole in segs:
                    seg_choices.append(hole.size)
                    
                allocation_size = random.choice(seg_choices)
                if allocation_size + allocated_memory >= ram_size:
                    continue
                
                stride = random.randint(1, allocation_size)
                param = [random.randrange(0, Byte.MAX) for _ in range(int(stride*0.40))]
                unallocated_memory -= allocation_size
                
            elif choice == POP:
                if program.size <= 2:
                    continue

                param = random.randrange(1, program.size-1)
                unallocated_memory += param

            elif choice == TERMINATE:
                param = 0

            else:
                continue

            pid = self.os.ram.get_program_id(program)
            self.script[pid][next_df] = dict()
            self.script[pid][next_df][choice] = param

        if number_programs == 0:
            for i in range(random.randrange(0, int(ram_size/32))):
                allocation_size = random.randrange(1, int(ram_size/16))
                if allocation_size + allocated_memory < ram_size:
                    new_program_bytes = [random.randrange(0, Byte.MAX) for _ in range(0, allocation_size)]
                    unallocated_memory -= allocation_size
                    new_pid = self.os.load_program(Program(new_program_bytes))
                    self.script[new_pid] = dict()

        elif random.randrange(0, number_programs) == 0:
            allocation_size = random.randrange(1, int(ram_size/16))
            if allocation_size + allocated_memory < ram_size:
                new_program_bytes = [random.randrange(0, Byte.MAX) for _ in range(0, allocation_size)]
                unallocated_memory -= allocation_size
                new_pid = self.os.load_program(Program(new_program_bytes))
                self.script[new_pid] = dict()

    def step(self):
        if self.running:
            self.advance_sim(self.dt)

            if self.auto:
                self.prepare_next_step()

        self.dt += 1

    def stop_simulation(self):
        self.os.clear_all()
        self.script = None
        self.running = False
        self.auto = False
        
        with open("script_output.json", "w") as script_output:
            json.dump(self.script, script_output, indent=4)