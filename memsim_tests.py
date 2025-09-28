from memsim.program import Program
from memsim.ram import RAM
from memsim.os import OS
from sys import argv

if __name__ == "__main__":
    os = OS(int(argv[1]))
    os.load_program_into_ram(Program([0x11] * 4))
    # os.load_program_into_ram(Program([0x22] * 4))

    pass