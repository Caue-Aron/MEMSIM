from memsim.program import Program
from memsim.ram import RAM
from sys import argv

if __name__ == "__main__":
    ram = RAM(int(argv[1]))
    # ram.swap_in(Program([0x10 for _ in range (16)]))
    ram.swap_in(Program([0x02] * 3))
    ram.swap_in(Program([0x01] * 3))
    print(ram.swap_out(0))

    print(ram.swap_out(1))

    pass