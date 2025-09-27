from memsim.memory import Memory
from memsim.program import Program
from sys import argv

if __name__ == "__main__":
    mem = Memory(int(argv[1]))
    mem.swap_in(Program([0x02, 0x02, 0x02]))
    mem.swap_in(Program([0x01, 0x01, 0x01]))
    mem.swap_out(0)
    mem.swap_in(Program([0x03, 0x03, 0x03, 0x03]))
    mem.swap_in(Program([0x02, 0x02, 0x02, 0x02]))
    mem.swap_out(2)

    mem.swap_in(Program([0x04, 0x04, 0x04, 0x04, 0x04]))

    pass