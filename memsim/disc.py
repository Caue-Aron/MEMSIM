from .byte import Byte, NULL
from .memory import Memory
from .program import Program
from .segment import Segment, PROGRAM, HOLE

class Disc(Memory):
    def __init__(self, size:Byte.dtype=Byte.MAX * 2):
        super().__init__(size)

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


    


        