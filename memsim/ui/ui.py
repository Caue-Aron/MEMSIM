from .theme import create_theme_imgui_light, create_stack_theme
from tkinter import Tk, filedialog
import dearpygui.dearpygui as dpg
import time
from memsim.memsim import MEMSIM, PROGRAM
from memsim.memory_errors import MemSimError

def get_left_width():
    viewport_width = dpg.get_viewport_width()
    return int(viewport_width * 0.80)

def get_mem_usage_space():
    viewport_width = dpg.get_viewport_height()
    return int(viewport_width * 0.50)

class MEMSIMUI:
    def __enter__(self):
        dpg.create_context()

        light_theme = create_theme_imgui_light()
        self.stack_theme = create_stack_theme()
        dpg.bind_theme(light_theme)
        
        width = 1200
        height = 800

        self.is_sim_running = False
        self.elapsed_time = 0.0
        self.step_speed = 1
        self.mem_state = None
        self.memsim = None
        self.advance_sim = False

        self.chart_window = None
        self.layout_window = None

        with dpg.window(label="MEMSIM", width=width, height=height) as main_window:
            self.main_window = main_window
            
            with dpg.menu_bar():
                with dpg.menu(label="Arquivo"):
                    dpg.add_menu_item(label="Carregar Simulação Roteirizada", callback=self.load_init_script_callback)
                    dpg.add_menu_item(label="Carregar Simulação Automática", callback=self.load_init_auto_callback)
                    dpg.add_menu_item(label="Salvar Roteiro")
                    dpg.add_menu_item(label="Salvar Estado de Memória")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Sair")

                with dpg.menu(label="Ferramentas"):
                    dpg.add_menu_item(label="Rodar Simulação", callback=self.start_sim_callback)
                    dpg.add_menu_item(label="Avançar", callback=self.advance_sim_callback)
                    dpg.add_menu_item(label="Pausar Simulação", callback=self.pause_sim_callback)
                    dpg.add_menu_item(label="Parar Simulação", callback=self.stop_sim_callback)
                    dpg.add_separator()
                    
                    with dpg.menu(label="Definir Velocidade"):
                        dpg.add_menu_item(label="0.25s", callback=self.step_speed_callback, user_data={"step_speed":0.25})
                        dpg.add_menu_item(label="0.5s", callback=self.step_speed_callback, user_data={"step_speed":0.5})
                        dpg.add_menu_item(label="1s", callback=self.step_speed_callback, user_data={"step_speed":1})
                        dpg.add_menu_item(label="2s", callback=self.step_speed_callback, user_data={"step_speed":2})
                        dpg.add_menu_item(label="3s", callback=self.step_speed_callback, user_data={"step_speed":3})
                        dpg.add_menu_item(label="4s", callback=self.step_speed_callback, user_data={"step_speed":4})
                        dpg.add_menu_item(label="5s", callback=self.step_speed_callback, user_data={"step_speed":5})


            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Informações")

                    with dpg.child_window() as chart_window:
                        self.chart_window = chart_window

                        with dpg.plot(label="Uso de Memória", height=-1, width=-1) as mem_usage:
                            self.mem_usage = mem_usage
                            
                            dpg.add_plot_legend()

                            x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Tempo (segundos)", tag="uso_memoria_x_axis")
                            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Bytes", tag="uso_memoria_y_axis")

                            self.memory_usage_x = []
                            self.memory_usage_y = []

                            self.chart_mem_usage = dpg.add_line_series(x=self.memory_usage_x, y=self.memory_usage_y,
                                                                       label="Uso de Memória", parent=y_axis)

                        with dpg.plot(label="Buracos vs. Programas", height=-1) as holes_programs:
                            self.holes_programs = holes_programs
                            dpg.add_plot_legend()

                            # Add a dummy axis (required even if unused)
                            with dpg.plot_axis(dpg.mvXAxis, label=""):
                                pass
                            with dpg.plot_axis(dpg.mvYAxis, label=""):
                                # Your pie chart goes here
                                self.unallocated_mem = 100
                                self.allocated_mem = 0

                                self.chart_hole_programs = dpg.add_pie_series(
                                    x=0.0,  # X center position of pie
                                    y=0.0,  # Y center position of pie
                                    radius=0.6,
                                    values=[self.allocated_mem, self.unallocated_mem],
                                    labels=["Programas", "Buracos"],
                                    normalize=True
                                )

                with dpg.group():
                    dpg.add_text("Layout da Memória")
                    with dpg.child_window() as layout_window:
                        self.layout_window = layout_window

                        with dpg.table(header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp, height=-1,
                                        borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True) as table:
                            self.mem_stack = table
                        
                            dpg.bind_item_theme(table, self.stack_theme)
                            dpg.add_table_column()

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        dpg.create_viewport(title="MEMSIM", width=width, height=height)

        dpg.configure_item(self.chart_window, width=get_left_width())
        dpg.configure_item(self.layout_window, width=-1)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        return self
    
    def rebuild_mem_stack(self):
        if dpg.does_item_exist(self.mem_stack):
            dpg.delete_item(self.mem_stack, children_only=False)

        with dpg.table(header_row=False, resizable=True, policy=dpg.mvTable_SizingStretchProp, height=-1, parent=self.layout_window,
                        borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True) as table:
            self.mem_stack = table
        
            dpg.bind_item_theme(table, self.stack_theme)
            dpg.add_table_column()

            for segment in self.mem_state.get_memory_layout():
                with dpg.table_row():
                    height = segment.size
                    if height < 45:
                        height = 45

                    if segment.type == PROGRAM:
                        pid = str(self.mem_state.get_program_id(segment))
                        dpg.add_button(label=f"ID: {pid}\nIndex: {segment.index}\nSize: {segment.size}", height=height)

                    else:
                        dpg.add_button(label=f"{segment.type}\nIndex: {segment.index}\nSize: {segment.size}", height=height)

    def advance_sim_callback(self):
        if self.memsim is None:
            self.start_sim()
            self.is_sim_running = False
            self.elapsed_time = -1
            
        self.advance_sim = True      
        self.elapsed_time += 1

    def update_hole_programs(self):
        total_mem = self.mem_state.memory_size
        self.unallocated_mem = int(self.mem_state.get_total_unallocated_memory() / total_mem * 100)
        self.allocated_mem = int(self.mem_state.get_total_allocated_memory() / total_mem * 100)
        dpg.set_value(self.chart_hole_programs, [[self.allocated_mem, self.unallocated_mem], []])

    def update_memory_usage(self):
        self.memory_usage_y.append(self.mem_state.get_total_allocated_memory())
        self.memory_usage_x.append(self.elapsed_time)
        dpg.set_value(self.chart_mem_usage, [list(self.memory_usage_x), list(self.memory_usage_y)])
        dpg.fit_axis_data('uso_memoria_x_axis')
        dpg.fit_axis_data('uso_memoria_y_axis')
        dpg.set_axis_limits("uso_memoria_y_axis", 0, self.mem_state.memory_size)

    def update_simulation(self):
        self.memsim.step()
        self.mem_state = self.memsim.get_state()

        self.update_memory_usage()
        self.update_hole_programs()
        self.rebuild_mem_stack()

    def stop_sim_abruptly(self, sender, app_data, user_data):
        dpg.configure_item(user_data["modal"], show=False)
        self.stop_sim()

    def run_simulation(self):
        last_time = time.perf_counter()
        self.start_time = last_time   # store when the simulation started
        self.elapsed_time = 0.0     # running total

        while dpg.is_dearpygui_running():
            if self.is_sim_running or self.advance_sim:
                now = time.perf_counter()
                self.elapsed_time = now - self.start_time  # total time passed since start

                if now - last_time >= self.step_speed:
                    try:
                        self.update_simulation()
                    except MemSimError as e:
                        with dpg.window(
                                label="Erro de Memória", modal=True,
                                no_resize=True, no_move=True, 
                                show=False, height=-1, no_close=False) as modal:
                            dpg.add_text(f"{str(e)}")
                            dpg.add_button(label="Fechar", callback=self.stop_sim_abruptly, user_data={"modal":modal})

                        dpg.configure_item(
                            modal,
                            show=True,
                            pos=(dpg.get_viewport_width()/2 - 150,
                                dpg.get_viewport_height()/2 - 75)
                        )

                    last_time = now

                self.advance_sim = False 

            dpg.render_dearpygui_frame()

    def step_speed_callback(self, sender, app_data, user_data):
        self.step_speed = user_data["step_speed"]

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.destroy_context()

    def on_viewport_resize(self):
        dpg.configure_item(self.chart_window, width=get_left_width())
        dpg.configure_item(self.mem_usage, height=get_mem_usage_space())
        dpg.configure_item(self.holes_programs, width=get_mem_usage_space() * 0.85)

    def load_init_script(self, file_path):
        if self.memsim:
            self.memsim.stop_simulation()

        self.memsim = MEMSIM(file_path, auto_mode=False)
        self.mem_state = self.memsim.get_state()
    
    def search_init_file(self):
        root = Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=(("All files", "*.json"), ("Text files", "*.txt"))
        )

        root.destroy()

        if file_path:
            return file_path

    def load_init_script_callback(self, sender, app_data, user_data):
        file_path = self.search_init_file()
        self.load_init_script(file_path)

    def load_init_auto(self, file_path):
        if self.memsim:
            self.memsim.stop_simulation()
            self.update_simulation()

        self.memsim = MEMSIM(file_path, auto_mode=True)
        self.mem_state = self.memsim.get_state()

    def load_init_auto_callback(self, sender, app_data, user_data):
        file_path = self.search_init_file()
        self.load_init_auto(file_path)

    def start_sim(self):
        if self.memsim:
            self.is_sim_running = True
        else:
            with dpg.window(label="Aviso", modal=True, no_resize=True, no_move=True, show=False, height=-1) as modal:
                dpg.add_text("Selecione um arquivo de configuração primeiro")

            dpg.configure_item(
                    modal,
                    show=True,
                    pos=(dpg.get_viewport_width()/2 - 150,
                         dpg.get_viewport_height()/2 - 75)
                )
    
    def stop_sim(self):
        self.is_sim_running = False
        dpg.set_value(self.chart_mem_usage, [[0], [0]])
        dpg.fit_axis_data('uso_memoria_x_axis')
        dpg.fit_axis_data('uso_memoria_y_axis')
        dpg.set_axis_limits("uso_memoria_y_axis", 0, 1)
        dpg.set_axis_limits("uso_memoria_x_axis", 0, 1)
        self.memsim = None
            
    def pause_sim(self):
        self.is_sim_running = False

    def start_sim_callback(self, sender, app_data, user_data):
        self.start_sim()

    def pause_sim_callback(self, sender, app_data, user_data):
        self.pause_sim()

    def stop_sim_callback(self, sender, app_data, user_data):
        self.stop_sim()
