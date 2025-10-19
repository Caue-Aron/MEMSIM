from .byte import Byte, NULL
from typing import List, Dict, Union
from .ram import RAM
from .disc import Disc
from .program import Program
from .memory_errors import MSNotEnoughMemory, MSNotEnoughDiscMemory, MSIDNotFound
from .segment import Segment, PROGRAM, HOLE
from .memory import Memory

ID_IN_RAM = "id_in_ram"
ID_IN_DISC = "id_in_disc"

class OS:
    def __init__(self, ram_size:Byte.dtype=Byte.MAX+1, disc_size:Byte.dtype=Byte.MAX+1):
        self.disc = Disc(disc_size)
        self.ram = RAM(ram_size)
        self.ids = list()

    def _load_program_mem(self, memory:Memory, program:Program):
        p_bytes = program.stream_bytes()
        p_size = len(p_bytes)

        memory_block = memory.get_next_free_block(p_size)
        if memory_block:
            memory.swap_in(Segment(PROGRAM, memory_block.index, memory_block.size), p_bytes)
        else:
            raise MSNotEnoughMemory(memory.main_memory, memory.memory_layout, p_size)
        
    def _search_lowest_id(self):
        if not self.ids:
            return 0x0
        
        self.ids.sort(key=lambda x: x["id"])
        biggest_id = self.ids[-1]["id"] + 2
        for i in range(0, biggest_id):
            existing_id = any(i in ids.values() for ids in self.ids)
            if not existing_id:
                return i


    def load_program(self, program:Program) -> int:
        lowest_id = self._search_lowest_id()
        self.ids.append({"id": lowest_id, "storage": ID_IN_RAM})
        self._load_program_mem(self.ram, Program([lowest_id] + program.bytes))
        return lowest_id

    def _swap_ram_to_disc(self, pid:int):
        bytes_to_transfer = self.ram.swap_out(pid)
        self._load_program_mem(self.disc, Program(bytes_to_transfer))

    def _swap_disc_to_ram(self, pid:int):
        bytes_to_transfer = self.disc.swap_out(pid)
        self._load_program_mem(self.ram, Program(bytes_to_transfer))

    def check_id_memory(self, pid:int, memory:Memory) -> bool:
        mem = ID_IN_RAM if isinstance(memory, RAM) else ID_IN_DISC
        for pids in self.ids:
            if pid == pids["id"] and mem == pids["storage"]:
                return True
            
        return False

    def swap_out(self, pid:int):
        if self.check_id_memory(pid, self.ram):
            self._swap_ram_to_disc(pid)
            
        else:
            raise MSIDNotFound(pid, self.ram.main_memory, self.ram.memory_layout)

    def swap_in(self, pid:int):
        if self.check_id_memory(pid, self.disc):
            self._swap_disc_to_ram(pid)
        
        else:
            raise MSIDNotFound(pid, self.disc.main_memory, self.disc.memory_layout)

    def shrink_ram(self):
        program_ids = list()
        for program_index, program in self.ram.get_all_segments_of_type(PROGRAM):
            pid = self.ram.get_program_id(program)
            program_ids.append(pid)
            
            self._swap_ram_to_disc(pid)
        
        for pid in program_ids:
            self._swap_disc_to_ram(pid)

        # raise MSNotEnoughMemory(self.disc.main_memory, self.disc.memory_layout, combined_program_size)