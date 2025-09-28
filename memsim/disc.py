from .byte import Byte, NULL
from typing import List
from .memory import Memory, HOLE, PROGRAM, Segment
from .program import Program
from .memory_errors import MSNotEnoughMemory
from .segment import Segment

class Disc(Memory):
    def __init__(self):
        super().__init__(Byte.MAX * 2)

    def swap_in(self, program:Program):
        program_size = len(program.bytes)
        free_segment = self.get_next_free_block(program_size)

        if free_segment:
            super().swap_in(free_segment, program.stream_bytes())
            
        else:
            self.expand_disc(program_size)

            super().swap_in(
                Segment(PROGRAM,
                        self.memory_layout[len(self.memory_layout)-1].index,
                        program_size
                ),
                program.stream_bytes()
            )

    def expand_disc(self, size:int):
        self.main_memory += [NULL] * size
        further_most_segment = self.memory_layout[len(self.memory_layout)-1]
        if further_most_segment.type == HOLE:
            further_most_segment.size += size
        else:
            self.memory_layout.append(Segment(
                HOLE,
                further_most_segment.index + further_most_segment.size,
                size
            ))


    


        