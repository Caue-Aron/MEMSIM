from .byte import Byte, NULL
from .safe_list import SafeList
from typing import List, Tuple
from .memory_errors import MSNotEnoughMemory, MSFaultyAccess, MSNoAllocationBlockAvailable, MSIDNotFound
from .segment import Segment, PROGRAM, HOLE
from .program import Program

class Memory:
    def __init__(self, memory_size:int=Byte.MAX+1):
        if memory_size > 0:
            self.memory_size = memory_size
        else:
            self.memory_size = Byte.MAX + 1

        self.main_memory = SafeList([NULL for _ in range(self.memory_size)])
        self.memory_layout = SafeList([Segment(HOLE, 0, self.memory_size)])

    def swap_in(self, block:Segment, program_bytes:list[Byte]):
        block_end = block.index + block.size
        index = block.index
        size = block.size

        for other_programs in self.memory_layout:
            if other_programs.type == PROGRAM:
                other_program_start = other_programs.index
                other_program_end = other_programs.index + other_programs.size

                if other_program_start < index < other_program_end or other_program_start < block_end < other_program_end:
                    raise MSFaultyAccess(self.main_memory, self.memory_layout, Segment(PROGRAM, index, size))
                elif index < other_program_start < block_end or index < other_program_end < block_end:
                    raise MSFaultyAccess(self.main_memory, self.memory_layout, Segment(PROGRAM, index, size))
        
        if self.get_total_unallocated_memory() < size:
            raise MSNotEnoughMemory(self.main_memory, self.memory_layout, size)
        
        next_layout_index = 0
        hole_before = True
        hole_after = True
        segment = None
        for next_layout_index, segment in enumerate(self.memory_layout):
            segment_end = segment.index + segment.size
            if segment.type == HOLE and segment.index <= index <= segment_end and segment.index <= block_end <= segment_end:
                    if segment.index == index:
                        hole_before = False

                    if segment_end == block_end:
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

    def get_program_segment(self, pid:int) -> Tuple[int, Segment]:
        for layout_index, program in self.get_all_segments_of_type(PROGRAM):
            if self.main_memory[program.index] == pid:
                return (layout_index, program.copy())
            
        raise MSIDNotFound(pid, self.main_memory, self.memory_layout)
            
    def get_program_id(self, segment:Segment) -> int:
        return self.main_memory[segment.index]

    def swap_out(self, pid:int) -> List[Byte]:
        layout_index, _ = self.get_program_segment(pid)

        program_to_remove = self.memory_layout[layout_index]
        program_bytes = self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size]
        self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size] = [NULL] * program_to_remove.size


        next_segment = self.memory_layout[layout_index+1]
        prev_segment = self.memory_layout[layout_index-1]
        
        if next_segment.type == HOLE:
            program_to_remove.size = program_to_remove.size + next_segment.size
            self.memory_layout.pop(layout_index+1)

        if prev_segment.type == HOLE:
            program_to_remove.index = prev_segment.index
            program_to_remove.size += prev_segment.size
            self.memory_layout.pop(layout_index-1)

        program_to_remove.type = HOLE
        
        self.main_memory[program_to_remove.index:program_to_remove.index+program_to_remove.size] = [NULL] * program_to_remove.size
        
        return program_bytes

    def get_bytes(self) -> List[Byte]:
        return self.main_memory.copy()

    def get_memory_layout(self) -> List[Segment]:
        return (layout for layout in self.memory_layout)

    def get_next_free_block(self, size:int) -> Segment:
        for segment in self.memory_layout:
            if segment.type == HOLE and segment.size >= size:
                    return Segment(HOLE, segment.index, size)

        return None
        
    def get_next_segment(self, index:int=0, stype:str=PROGRAM) -> Tuple[int, Segment]:
        return next(((layout_index, segment) for layout_index, segment in enumerate(self.memory_layout[index:]) if segment.type == stype), None)

    def get_all_segments_of_type(self, stype:str, index:int=0) -> List[Tuple[int, Segment]]:
        return ((layout_index, segment) for layout_index, segment in enumerate(self.memory_layout[index:]) if segment.type == stype)
    
    def get_total_unallocated_memory(self) -> int:
        combined_program_memory = sum(
            segment.size for segment in self.memory_layout if segment.type == PROGRAM
        )

        return self.memory_size - combined_program_memory
    
    def grow_segment(self, layout_index:int, p_bytes:Program):
        size = len(p_bytes.stream_bytes())
        grow_segment = self.memory_layout[layout_index]
        shrink_segment = self.memory_layout[layout_index+1]

        if grow_segment is shrink_segment or shrink_segment.type == PROGRAM or grow_segment.type == HOLE:
            raise MSFaultyAccess([], self.memory_layout, shrink_segment)

        if shrink_segment.size < size:
            raise MSNotEnoughMemory([], self.memory_layout, size)
        
        grow_size = grow_segment.size
        grow_segment.size += size
        shrink_segment.index = grow_segment.index + grow_segment.size

        self.main_memory[grow_size:shrink_segment.index] = p_bytes.stream_bytes()
