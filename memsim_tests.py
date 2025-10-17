from memsim.program import Program
from memsim.ram import RAM
from memsim.os import OS
from sys import argv

if __name__ == "__main__":
    os = OS(32)
    id1 = os.load_program(Program([0x11] * 4))
    id2 = os.load_program(Program([0x22] * 4))
    os.swap_out(id1)
    id3 = os.load_program(Program([0x33] * 6))
    id4 = os.load_program(Program([0x44] * 6))
    os.swap_out(id3)
    id5 = os.load_program(Program([0x55] * 2))

    os.shrink_ram()

    pass