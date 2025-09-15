from util import *
import numpy as np
from .program import Program
import util
from util import MEM_SIZE, NULL, byte

class Memory:
    def __init__(self):
        self.main_memory = np.array([byte(NULL) for _ in range(MEM_SIZE)], dtype=byte)
        self.next_allocation_index = 0

    def swap_in(self, program:Program):
        self.main_memory[self.next_allocation_index:self.next_allocation_index + len(program.bytes)] = program.bytes
        self.next_allocation_index = len(program.bytes)