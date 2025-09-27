from .byte import Byte, NULL
from .program import Program
from .safe_list import SafeList
from typing import List
from .memory_errors import MSNotEnoughMemory

HOLE = "H"
PROGRAM = "P"

class Segment:
    def __init__(self, stype:str, index:int, size:int):
        self.type = stype
        self.index = index
        self.size = size

    def __repr__(self):
        return f"{self.type}, {self.index}, {self.size}"

class Memory:
    def __init__(self, memory_size:int=Byte.MAX+1):
        if memory_size > 0:
            self.memory_size = memory_size
        else:
            self.memory_size = Byte.MAX + 1

        self.main_memory = [NULL for _ in range(self.memory_size)]
        self.memory_layout = SafeList([Segment(HOLE, 0, self.memory_size)])

    def swap_in(self, program:Program):
        program_index, program_size = self.get_next_alloc_block(program)
        self.main_memory[program_index:program_index+program_size] = program.stream_bytes()

    def swap_out(self, layout_index:int) -> List[Byte]:
        program_to_remove = self.memory_layout[layout_index]
        
        if self.memory_layout[layout_index-1].type == HOLE and self.memory_layout[layout_index+1].type == HOLE:
            program_to_remove.type = HOLE
            program_to_remove.index = self.memory_layout[layout_index-1].index
            program_to_remove.size += self.memory_layout[layout_index-1].size + self.memory_layout[layout_index+1].size
            self.memory_layout.pop(layout_index+1)
            self.memory_layout.pop(layout_index-1)

        elif self.memory_layout[layout_index+1].type == HOLE:
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
        
        program_bytes = self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size]
        self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size] = [NULL] * program_to_remove.size
        
        return program_bytes

    def get_bytes(self) -> List[Byte]:
        return self.main_memory.copy()

    def get_memory_layout(self) -> List[Segment]:
        return self.memory_layout.copy()

    def get_next_alloc_block(self, program: Program) -> Segment:
        p_size = len(program.bytes)
        combined_hole_size = 0

        for layout_index, segment in enumerate(self.memory_layout):
            if segment.type == HOLE:
                if segment.size >= p_size:
                    program_in_mem = Segment(PROGRAM, segment.index, p_size)
                    p_index = segment.index
                    segment.index = p_size + segment.index
                    segment.size = segment.size - p_size
                    self.memory_layout.insert(layout_index, program_in_mem)
                    if segment.size == 0:
                        self.memory_layout.pop(layout_index+1)
                    return (p_index, p_size)
            
                combined_hole_size += segment.size

        if combined_hole_size >= p_size:
            self.shrink()
            return self.get_next_alloc_block(program)

        else:
            raise MSNotEnoughMemory(self.main_memory.copy(), self.memory_layout.copy(), p_size)
        
    def get_next_segment(self, index:int, stype:str) -> Segment:
        return next((i for i in self.memory_layout[index:] if i.type == stype), None)
    
    def get_unallocated_memory(self) -> int:
        combined_program_memory = sum(
            segment.size for segment in self.memory_layout if segment.type == PROGRAM
        )

        return self.memory_size - combined_program_memory
            
    def shrink(self):
        for layout_index, segment in enumerate(self.memory_layout):
            if segment.type == HOLE:
                program_to_move = self.memory_layout[layout_index+1]
                if program_to_move.type == PROGRAM:
                    program_start = program_to_move.index
                    program_end = program_to_move.index + program_to_move.size
                    program_size = program_to_move.size

                    self.persistent_memory[0:program_size] = self.main_memory[program_start:program_end]
                    self.main_memory[program_start:program_end] = [NULL] * program_size
                    program_to_move.index = segment.index
                    
                    self.main_memory[program_to_move.index:program_to_move.index+program_size] = self.persistent_memory[0:program_size]

                    hole_to_remove = self.memory_layout.pop(layout_index)
                    next_hole = self.get_next_segment(layout_index, HOLE)

                    if next_hole:
                        next_hole.size = next_hole.size + hole_to_remove.size
                        next_hole.index = program_to_move.index + program_size
                    else:
                        self.memory_layout.append(Segment(HOLE, program_to_move.index + program_size, self.get_unallocated_memory()))
