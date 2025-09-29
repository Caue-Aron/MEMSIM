from .byte import Byte, NULL
from typing import List
from .ram import RAM
from .disc import Disc
from .program import Program
from .memory_errors import MSNotEnoughMemory
from .segment import Segment, PROGRAM, HOLE
from .memory import Memory

class OS:
    def __init__(self, ram_size=Byte.MAX+1):
        self.disc = Disc()
        self.ram = RAM(ram_size)

    def load_program(self, memory:Memory, program:Program):
        p_bytes = program.stream_bytes()
        p_size = len(p_bytes)

        memory_block = memory.get_next_free_block(p_size)
        if memory_block:
            memory.swap_in(Segment(PROGRAM, memory_block.index, memory_block.size), p_bytes)
        else:
            raise MSNotEnoughMemory(memory.main_memory, memory.memory_layout, p_size)

    def load_program_into_ram(self, program:Program):
        self.load_program(self.ram, program)
        
    def load_program_into_disc(self, program:Program):
        self.load_program(self.disc, program)

    def swap_ram_to_disc(self, program_index:int):
        layout_index = 0
        program_to_remove = None
        for i, content in enumerate(self.ram.get_all_segments_of_type(PROGRAM)):
            layout_index, program_to_remove = content
            if i == program_index:
                break
                        
        bytes_to_transfer = self.ram.swap_out(layout_index)
        self.load_program_into_disc(Program(bytes_to_transfer))

    def swap_disc_to_ram(self, program_index:int):
        layout_index = 0
        program_to_remove = None
        for i, content in enumerate(self.disc.get_all_segments_of_type(PROGRAM)):
            layout_index, program_to_remove = content
            if i == program_index:
                break

        bytes_to_transfer = self.disc.swap_out(layout_index)
        self.load_program_into_ram(Program(bytes_to_transfer))

    def shrink_ram(self):
        combined_program_size = sum(program.size for program in self.ram.get_memory_layout() if program.type == PROGRAM)
        free_disc_block = self.disc.get_next_free_block(combined_program_size)

        if free_disc_block:
            swap_out_index = free_disc_block.index
            # we do reverse so we can pop from memory without interference
            programs = [i for i in self.ram.get_all_segments_of_type(PROGRAM)][::-1]
            offset = 0
            for program_index, program in programs:
                # program_index, program = content
                size = program.size

                program_bytes = self.ram.swap_out(program_index)
                self.disc.swap_in(
                    Segment(PROGRAM, swap_out_index+offset, size),
                    program_bytes
                )
                
                offset += size

        else:
            pass