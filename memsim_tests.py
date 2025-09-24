from memsim.memory import Memory
from memsim.program import Program
import numpy as np
import util

if __name__ == "__main__":
    mem = Memory()
    mem.swap_in(Program([0x01, 0x01, 0x01]))
    mem.swap_in(Program([0x02, 0x02, 0x02, 0x02, 0x02, 0x02]))

    [print(util.byte_str(mem.get_bytes()[i])) for i in range(10)]

    print(mem.get_memory_layout())