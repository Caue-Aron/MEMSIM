from memsim.ui.ui import MEMSIMUI

if __name__ == "__main__":
    with MEMSIMUI() as ui:
        ui.run_simulation()

    quit()

# -------------------------------------------------------------------------------------------------------------

import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Tables"):

    with dpg.table(header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                   borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True):

        dpg.add_table_column(label="Header 1", init_width_or_weight=100, width_fixed=True)

        # once it reaches the end of the columns
        for i in range(1, 12):
            with dpg.table_row(height=i*100):
                dpg.add_text(f"{i}")

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()