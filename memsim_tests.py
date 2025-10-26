import sys
import time
from multiprocessing import Process, Queue, Value

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QFont


def run_simulation_worker(output_queue, show_holes_flag):
    import json
    from memsim.memsim import MEMSIM
    from memsim.segment import PROGRAM, HOLE

    config_file = "ini.json"

    with open(config_file, 'r') as f:
        config_data = json.load(f)

    ram_size = config_data.get("setup", {}).get("ram_size", 128)

    memsim = MEMSIM(config_file)

    _is_running = True
    while _is_running:
        memsim.step()
        state = memsim.get_state()

        ui_lines = []
        total_size = ram_size

        ui_lines.append(f"Uso de RAM (Tamanho: {total_size})\n" + "=" * 40)

        show_holes = show_holes_flag.value

        program_segments_with_idx = state.get_all_segments_of_type(PROGRAM)

        all_segments_to_render = []
        for idx, segment in program_segments_with_idx:
            all_segments_to_render.append((segment, PROGRAM, idx))

        if show_holes:
            hole_segments_with_idx = state.get_all_segments_of_type(HOLE)
            for idx, segment in hole_segments_with_idx:
                all_segments_to_render.append((segment, HOLE, idx))

        all_segments_to_render.sort(key=lambda x: x[2])

        for segment, seg_type, idx in all_segments_to_render:
            if seg_type == PROGRAM:
                pid = state.get_program_id(segment)

                pid_int = int(pid)
                start_int = int(idx)
                size_int = int(segment.size)
                line = f"PID {pid_int:02d} [Addr: {start_int:03d}, Size: {size_int:03d}] | {'#' * size_int}"
                ui_lines.append(line)
            elif seg_type == HOLE:
                start_int = int(idx)
                size_int = int(segment.size)
                line = f"HOLE [Addr: {start_int:03d}, Size: {size_int:03d}] | {'.' * size_int}"
                ui_lines.append(line)

        ui_lines.append(f"\n" + "=" * 40 + "\nSimulação em execução...")
        ui_string = "\n".join(ui_lines)

        output_queue.put(ui_string)

        if not program_segments_with_idx:
            output_queue.put("DONE: Simulação encerrada (nenhum programa restante).")
            _is_running = False

        time.sleep(1)

class MemSimWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.sim_process = None
        self.ui_queue = None

        self.show_holes_flag = Value('b', False)

        self.init_ui()

        self.queue_timer = QTimer(self)
        self.queue_timer.timeout.connect(self.check_ui_queue)

    def init_ui(self):
        self.setWindowTitle("MEMSIM - Visualizador de Simulação de Memória")
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Iniciar Simulação")
        self.start_button.clicked.connect(self.start_simulation)

        self.stop_button = QPushButton("Parar Simulação")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)

        self.show_holes_button = QPushButton("Mostrar Holes")
        self.show_holes_button.setCheckable(True)
        self.show_holes_button.toggled.connect(self.on_toggle_holes)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.show_holes_button)

        layout.addLayout(control_layout)

        self.display_label = QLabel("Clique em 'Iniciar' para começar a simulação.")
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.TypeWriter)
        self.display_label.setFont(font)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.display_label)
        self.setLayout(layout)
        self.show()

    def start_simulation(self):
        self.ui_queue = Queue()
        self.show_holes_flag.value = self.show_holes_button.isChecked()

        self.sim_process = Process(
            target=run_simulation_worker,
            args=(self.ui_queue, self.show_holes_flag)
        )
        self.sim_process.start()

        self.queue_timer.start(100)

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.display_label.setText("Começando o processo de simulação...")

    def stop_simulation(self):
        self.queue_timer.stop()

        if self.sim_process and self.sim_process.is_alive():
            self.sim_process.terminate()
            self.sim_process.join()

        self.sim_process = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.display_label.setText("Simulação parada pelo usuário.")

    def check_ui_queue(self):
        if self.ui_queue is None:
            return

        try:
            while not self.ui_queue.empty():
                message = self.ui_queue.get_nowait()

                if message.startswith("DONE:"):
                    self.display_label.setText(message)
                    self.stop_simulation()
                elif message.startswith("ERROR:"):
                    self.display_label.setText(message)
                    self.stop_simulation()
                else:
                    self.display_label.setText(message)

        except Exception as e:
            pass

        if self.sim_process and not self.sim_process.is_alive():
            self.stop_simulation()
            self.display_label.setText("Simulação parou inesperadamente.")

    def on_toggle_holes(self, checked):
        self.show_holes_flag.value = checked

        if checked:
            self.show_holes_button.setText("Esconder Holes")
        else:
            self.show_holes_button.setText("Mostrar Holes")

    def closeEvent(self, event):
        self.stop_simulation()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MemSimWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

