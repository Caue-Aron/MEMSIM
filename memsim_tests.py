from memsim.memsim import MEMSIM

if __name__ == "__main__":
    memsim = MEMSIM("ini.json")

    while(True):
        memsim.step()

    pass