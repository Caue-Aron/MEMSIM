from .byte import Byte, NULL
from .program import Program
from .safe_list import SafeList
from typing import List
from .memory_errors import MSNotEnoughMemory, MSFaultyAccess, MSNoAllocationBlockAvailable
from .segment import Segment

HOLE = "H"
PROGRAM = "P"

class Memory:
    def __init__(self, memory_size:int=Byte.MAX+1):
        if memory_size > 0:
            self.memory_size = memory_size
        else:
            self.memory_size = Byte.MAX + 1

        self.main_memory = SafeList([NULL for _ in range(self.memory_size)])
        self.memory_layout = SafeList([Segment(HOLE, 0, self.memory_size)])

    def swap_in(self, index:int, size:int, program_bytes:list[Byte]):
        for other_programs in self.memory_layout:
            if other_programs.type == PROGRAM:
                other_program_start = other_programs.index
                other_program_end = other_programs.index + other_programs.size
                if other_program_start < index < other_program_end or other_program_start < index + size < other_program_end:
                    raise MSFaultyAccess(self.main_memory, self.memory_layout, Segment(PROGRAM, index, size))
                elif index < other_program_start < index + size or index < other_program_end < index + size:
                    raise MSFaultyAccess(self.main_memory, self.memory_layout, Segment(PROGRAM, index, size))
        
        if self.get_unallocated_memory() < size:
            raise MSNotEnoughMemory(self.main_memory, self.memory_layout, size)
        
        next_layout_index = 0
        hole_before = True
        hole_after = True
        segment = None
        for next_layout_index, segment in enumerate(self.memory_layout):
            segment_end = segment.index + segment.size
            if segment.type == HOLE and segment.index <= index <= segment_end and segment.index <= index + size <= segment_end:
                    if segment.index == index:
                        hole_before = False

                    if segment_end == index + size:
                        hole_after = False

                    break
        else:
            raise MSNoAllocationBlockAvailable(self.main_memory, self.memory_layout, Segment(PROGRAM, index, size))
        
        if hole_after:
            self.memory_layout.insert(next_layout_index+1, Segment(HOLE, index+size, (segment.index + segment.size) - (index+size)))

        if hole_before:
            self.memory_layout.insert(next_layout_index, Segment(HOLE, segment.index, index - segment.index))
        
        segment.type = PROGRAM
        segment.size = size
        segment.index = index

        self.main_memory[index:index+size] = program_bytes

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
        return (layout for layout in self.memory_layout)

    def get_next_alloc_block(self, size:int) -> Segment:
        for segment in self.memory_layout:
            if segment.type == HOLE and segment.size >= size:
                    return Segment(HOLE, segment.index, size)

        return None
        
    def get_next_segment(self, index:int, stype:str) -> Segment:
        return next((i for i in self.memory_layout[index:] if i.type == stype), None)

    def get_last_segment(self, stype:str) -> Segment:
        return self.memory_layout[len(self.memory_layout)-1]
    
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
