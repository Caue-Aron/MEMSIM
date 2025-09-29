from memsim.program import Program
from memsim.ram import RAM
from memsim.os import OS
from sys import argv

if __name__ == "__main__":
    os = OS(24)
    os.load_program_into_ram(Program([0x11] * 4))
    os.load_program_into_ram(Program([0x22] * 4))
    os.swap_ram_to_disc(0)
    os.load_program_into_ram(Program([0x33] * 6))
    os.load_program_into_ram(Program([0x44] * 6))
    os.load_program_into_ram(Program([0x55] * 2))
    os.swap_ram_to_disc(2)

    os.shrink_ram()

    pass