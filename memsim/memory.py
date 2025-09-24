from util import *
import numpy as np
from .program import Program
from util import MEM_SIZE, NULL, byte
from typing import List, Tuple

class Memory:
    def __init__(self):
        self.main_memory = np.array([byte(NULL) for _ in range(MEM_SIZE)], dtype=byte)
        self.next_allocation_index = 0
        self.memory_layout = [(0, MEM_SIZE)]

    def swap_in(self, program:Program):
        prev_alloc_index = self.next_allocation_index
        self.next_allocation_index = len(program.bytes) + self.next_allocation_index
        self.main_memory[prev_alloc_index:self.next_allocation_index] = program.bytes
        self.memory_layout.append((prev_alloc_index,self.next_allocation_index - prev_alloc_index))

    def get_bytes(self) -> np.array:
        return self.main_memory.copy()
    
    def get_memory_layout(self) -> List[Tuple[int, int]]:
        return self.memory_layout.copy()