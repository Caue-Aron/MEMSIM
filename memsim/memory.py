import numpy as np
from .util import *
from .program import Program
from .safe_list import SafeList
from typing import List, Dict, Tuple
from .memory_errors import MSNotEnoughMemory

HOLE = "H"
PROGRAM = "P"

class Segment:
    def __init__(self, stype:str, index:int, size:int):
        self.type = stype
        self.index = index
        self.size = size

class Memory:
    def __init__(self, memory_size: byte = np.iinfo(byte).max + 1):
        if memory_size > 0:
            self.memory_size = memory_size
        else:
            self.memory_size = np.iinfo(byte).max + 1

        self.main_memory = np.array([byte(NULL) for _ in range(self.memory_size)], dtype=byte)
        self.memory_layout = SafeList([Segment(HOLE, 0, self.memory_size)])

    def swap_in(self, program:Program):
        program_index, program_size = self.get_next_alloc_bock(program)
        self.main_memory[program_index:program_index+program_size] = program.stream_bytes()

    def swap_out(self, layout_index:int):
        program_to_remove = self.memory_layout[layout_index]

        if self.memory_layout[layout_index+1].type == HOLE:
            hole_to_grow = self.memory_layout[layout_index+1]
            hole_to_grow.index = program_to_remove.index
            hole_to_grow.size = program_to_remove.size + hole_to_grow.size
            
            self.memory_layout.pop(layout_index)

        elif self.memory_layout[layout_index-1].type == HOLE:
            hole_to_grow = self.memory_layout[layout_index-1]
            hole_to_grow.size = program_to_remove.size + hole_to_grow.size

            self.memory_layout.pop(layout_index)

        else:
            program_to_remove.type = HOLE
        
        self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size] = NULL

    def get_bytes(self) -> np.array:
        return self.main_memory.copy()

    def get_memory_layout(self) -> List[Dict[str, int]]:
        return self.memory_layout.copy()

    def get_next_alloc_bock(self, program: Program) -> Segment:
        p_size = len(program.bytes)
        combined_hole_size = 0

        # searches for a hole big enough for the program
        for index, layout in enumerate(self.memory_layout):
            if layout.type == HOLE:
                if layout.size >= p_size:
                    program_in_mem = Segment(PROGRAM, layout.index, p_size)
                    p_index = layout.index
                    layout.index = p_size + layout.index
                    layout.size = layout.size - p_size
                    self.memory_layout.insert(index, program_in_mem)
                    return (p_index, p_size)
            
                combined_hole_size += layout.size

        if combined_hole_size >= p_size:
            next_index = self.shrink()

        else:
            raise MSNotEnoughMemory(self.main_memory.copy(), self.memory_layout.copy(), p_size)
            
    def shrink(self) -> int:
        pass

