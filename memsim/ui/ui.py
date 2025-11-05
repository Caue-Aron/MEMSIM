from .theme import create_theme_imgui_light
from tkinter import Tk, filedialog
import dearpygui.dearpygui as dpg
import time
from memsim.memsim import MEMSIM

def get_left_width():
    viewport_width = dpg.get_viewport_width()
    return int(viewport_width * 0.75)

class MEMSIMUI:
    def __enter__(self):
        dpg.create_context()

        light_theme = create_theme_imgui_light()
        dpg.bind_theme(light_theme)
        
        width = 1200
        height = 800

        self.step_speed = 1
        self.mem_state = None
        self.memsim = None

        self.chart_window = None
        self.layout_window = None

        with dpg.window(label="MEMSIM", width=width, height=height) as main_window:
            self.main_window = main_window
            
            with dpg.menu_bar():
                with dpg.menu(label="Arquivo"):
                    dpg.add_menu_item(label="Carregar Inicialização", callback=self.load_init_file_callback)
                    dpg.add_menu_item(label="Salvar Roteiro")
                    dpg.add_menu_item(label="Salvar Estado de Memória")
                    dpg.add_separator()
                    dpg.add_menu_item(label="Sair")

                with dpg.menu(label="Ferramentas"):
                    dpg.add_menu_item(label="Rodar Simulação", shortcut="| F5")
                    dpg.add_menu_item(label="Rodar Aleatório", shortcut="| F6")
                    dpg.add_menu_item(label="Pausar Simulação", shortcut="| F7")
                    dpg.add_menu_item(label="Parar Simulação", shortcut="| F8")
                    dpg.add_separator()
                    
                    with dpg.menu(label="Definir Velocidade"):
                        dpg.add_menu_item(label="0.25s", shortcut="| Ctrl+1", callback=self.step_speed_callback, user_data={"step_speed":0.25})
                        dpg.add_menu_item(label="0.5s", shortcut="| Ctrl+2", callback=self.step_speed_callback, user_data={"step_speed":0.5})
                        dpg.add_menu_item(label="1s", shortcut="| Ctrl+3", callback=self.step_speed_callback, user_data={"step_speed":1})
                        dpg.add_menu_item(label="2s", shortcut="| Ctrl+4", callback=self.step_speed_callback, user_data={"step_speed":2})
                        dpg.add_menu_item(label="3s", shortcut="| Ctrl+5", callback=self.step_speed_callback, user_data={"step_speed":3})
                        dpg.add_menu_item(label="4s", shortcut="| Ctrl+6", callback=self.step_speed_callback, user_data={"step_speed":4})
                        dpg.add_menu_item(label="5s", shortcut="| Ctrl+7", callback=self.step_speed_callback, user_data={"step_speed":5})


            with dpg.group(horizontal=True):
                with dpg.group():
                    dpg.add_text("Gráficos")
                    with dpg.child_window() as chart_window:
                        self.chart_window = chart_window

                with dpg.group():
                    dpg.add_text("Layout da Memória")
                    with dpg.child_window() as layout_window:
                        self.layout_window = layout_window

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        dpg.create_viewport(title="MEMSIM", width=width, height=height)

        dpg.configure_item(self.chart_window, width=get_left_width())
        dpg.configure_item(self.layout_window, width=-1)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window(self.main_window, True)

        return self
    
    def update_simulation(self):
        pass

    def run_simulation(self):
        last_time = time.perf_counter()

        while dpg.is_dearpygui_running():
            now = time.perf_counter()
            if now - last_time >= self.step_speed:
                self.update_simulation()
                last_time = now

            dpg.render_dearpygui_frame()

    def step_speed_callback(self, sender, app_data, user_data):
        self.step_speed = user_data["step_speed"]

    def __exit__(self, exc_type, exc_val, exc_tb):
        dpg.destroy_context()

    def on_viewport_resize(self):
        dpg.configure_item(self.chart_window, width=get_left_width())

    def load_init_file(self, file_path):
        if self.memsim:
            self.memsim.stop_simulation()

        self.memsim = MEMSIM(file_path)
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

    def load_init_file_callback(self, sender, app_data, user_data):
        file_path = self.search_init_file()
        self.load_init_file(file_path)