from memsim.memsim import MEMSIM
from memsim.segment import PROGRAM, HOLE
import time

if __name__ == "__main__":
    memsim = MEMSIM()
    memsim.setup_script("ini.json")
    while(True):
        memsim.step()
        state = memsim.get_state()

        ui = ""
        for idx, segment in state.get_all_segments_of_type(PROGRAM):
            pid = state.get_program_id(segment)
            ui += f"#{pid} | {"#"*segment.size}\n"
        ui += "-"*24

        with open("ui.txt", "w+") as ui_file:
            ui_file.write(ui)
        time.sleep(2)
    pass