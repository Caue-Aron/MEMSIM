from .byte import Byte, NULL
from typing import List
from .memory import HOLE, PROGRAM
from .ram import RAM
from .disc import Disc
from .program import Program
from .memory_errors import MSNotEnoughMemory
from .segment import Segment

class OS:
    def __init__(self, ram_size=Byte.MAX+1):
        self.disc = Disc()
        self.ram = RAM(ram_size)

    def load_program_into_ram(self, program:Program):
        p_bytes = program.stream_bytes()
        p_size = len(p_bytes)

        memory_block = self.ram.get_next_alloc_block(p_size)
        if not memory_block:
            raise MSNotEnoughMemory(self.ram.main_memory, self.ram.memory_layout, p_size)
        else:
            self.ram.swap_in(0x04, 0x08, p_bytes)

    def shrink_ram(self):
        combined_program_size = sum(program.size for program in self.disc.get_memory_layout() if program.type == PROGRAM)
        swap_out_index = 0

        try:
            swap_out_index = self.disc.get_next_alloc_block(combined_program_size).index

        except MSNotEnoughMemory:
            self.disc.expand_disc(combined_program_size)
            swap_out_index = self.disc.get_next_alloc_block(combined_program_size).index

        for program in self.ram.get_memory_layout():
            if program.type == PROGRAM:
                self.disc.swap_in()

        