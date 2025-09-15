from memsim.memory import Memory
from memsim.program import Program
import numpy as np
import util

if __name__ == "__main__":
    mem = Memory()
    mem.swap_in(Program([0x01, 0x0A, 0xBA]))
    mem.swap_in(Program([0x04, 0x30F, 0xFFA]))

    [print(util.byte_str(mem.main_memory[i])) for i in range(10)]