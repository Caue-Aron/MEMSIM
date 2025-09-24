import numpy as np
from .util import byte, NULL
from .program import Program
from .safe_list import SafeList
from typing import List, Dict, Tuple

HOLE = "H"
PROGRAM = "P"

class Memory:
    def __init__(self, mem_size: int = np.iinfo(byte).max + 1):
        if mem_size > 0:
            self.mem_size = mem_size
        else:
            self.mem_size = np.iinfo(byte).max + 1

        self.main_memory = np.array([byte(NULL) for _ in range(self.mem_size)], dtype=byte)
        self.memory_layout = SafeList([{"type":HOLE, "index": 0, "size": self.mem_size}])

    def swap_in(self, program:Program):
        program_index, program_size = self.set_program_layout(program)
        self.main_memory[program_index:program_index+program_size] = program.stream_bytes()

    def swap_out(self, layout_index:int):
        program_to_remove = self.memory_layout[layout_index]

        if self.memory_layout[layout_index+1]["type"] == HOLE:
            hole_to_grow = self.memory_layout[layout_index+1]
            hole_to_grow["index"] = program_to_remove["index"]
            hole_to_grow["size"] = program_to_remove["size"] + hole_to_grow["size"]
            
            self.memory_layout.pop(layout_index)

        elif self.memory_layout[layout_index-1]["type"] == HOLE:
            hole_to_grow = self.memory_layout[layout_index-1]
            hole_to_grow["size"] = program_to_remove["size"] + hole_to_grow["size"]

            self.memory_layout.pop(layout_index)

        else:
            program_to_remove["type"] = HOLE
        
        self.main_memory[program_to_remove["index"]:program_to_remove["index"]+program_to_remove["size"]] = NULL

    def get_bytes(self) -> np.array:
        return self.main_memory.copy()

    def get_memory_layout(self) -> List[Dict[str, int]]:
        return self.memory_layout.copy()

    def set_program_layout(self, program: Program) -> Tuple[int, int]:
        p_size = len(program.bytes)

        # searches for a hole big enough for the program
        for index, layout in enumerate(self.memory_layout):
            if layout["type"] == HOLE and layout["size"] >= p_size:
                program_in_mem = {"type":PROGRAM, "index":layout["index"], "size": p_size}
                p_index = layout["index"]
                layout["index"] = p_size + layout["index"]
                layout["size"] = layout["size"] - p_size
                self.memory_layout.insert(index, program_in_mem)
                return (p_index, p_size)

