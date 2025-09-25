import numpy as np
from .byte import Byte, NULL
from .program import Program
from .safe_list import SafeList
from typing import List, Dict
from .memory_errors import MSNotEnoughMemory

HOLE = "H"
PROGRAM = "P"
np.set_printoptions(formatter={'int': lambda x: f"0x{x:04X}"})

class Segment:
    def __init__(self, stype:str, index:int, size:int):
        self.type = stype
        self.index = index
        self.size = size

    def __repr__(self):
        return f"{self.type}, {self.index}, {self.size}"

class Memory:
    def __init__(self, memory_size:int=np.iinfo(Byte).max+1):
        if memory_size > 0:
            self.memory_size = memory_size
        else:
            self.memory_size = np.iinfo(Byte).max + 1

        self.main_memory = [Byte(NULL) for _ in range(self.memory_size)]
        self.memory_layout = SafeList([Segment(HOLE, 0, self.memory_size)])
        self.persistent_memory = []

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
        
        self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size] = [NULL] * program_to_remove.size

    def get_bytes(self) -> np.array:
        return self.main_memory.copy()

    def get_memory_layout(self) -> List[Dict[str, int]]:
        return self.memory_layout.copy()

    def get_next_alloc_bock(self, program: Program) -> Segment:
        p_size = len(program.bytes)
        combined_hole_size = 0

        # searches for a hole big enough for the program
        for layout_index, segment in enumerate(self.memory_layout):
            if segment.type == HOLE:
                if segment.size >= p_size:
                    program_in_mem = Segment(PROGRAM, segment.index, p_size)
                    p_index = segment.index
                    segment.index = p_size + segment.index
                    segment.size = segment.size - p_size
                    self.memory_layout.insert(layout_index, program_in_mem)
                    return (p_index, p_size)
            
                combined_hole_size += segment.size

        if combined_hole_size >= p_size:
            self.shrink()
            self.swap_in(program)

        else:
            raise MSNotEnoughMemory(self.main_memory.copy(), self.memory_layout.copy(), p_size)
            
    def shrink(self):
        for layout_index, segment in enumerate(self.memory_layout):
            if segment.type == HOLE:
                program_to_move = self.memory_layout[layout_index+1]
                if program_to_move.type == PROGRAM:
                    program_start = program_to_move.index
                    program_end = program_to_move.index + program_to_move.size
                    program_size = program_to_move.size

                    self.persistent_memory = [NULL for _ in range(program_size)]

                    self.persistent_memory[0:program_size] = self.main_memory[program_start:program_end]
                    self.main_memory[program_start:program_end] = [NULL] * program_size
                    program_to_move.index = segment.index
                    
                    self.main_memory[program_to_move.index:program_to_move.index+program_size] = self.persistent_memory[0:program_size]

                    self.persistent_memory[:] = [NULL] * len(self.persistent_memory)

                    hole = self.memory_layout.pop(layout_index)
                    furthest_hole = self.memory_layout[len(self.memory_layout)-1]
                    furthest_hole.size = furthest_hole.size + hole.size
