import sys
import time
import json
from multiprocessing import Process, Queue, Value

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QFont

from memsim.memory_canvas import MemoryCanvas

def run_simulation_worker(output_queue, show_holes_flag):
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

        show_holes = show_holes_flag.value
        segments = []

        program_segments_with_idx = state.get_all_segments_of_type(PROGRAM)

        all_segments_to_render = []
        for idx, segment in program_segments_with_idx:
            pid = state.get_program_id(segment)
            segments.append({
                "type": "PROGRAM",
                "pid": f"PID {pid}",
                "addr": idx,
                "size": segment.size
            })

        if show_holes:
            hole_segments_with_idx = state.get_all_segments_of_type(HOLE)
            for idx, segment in hole_segments_with_idx:
                segments.append({
                    "type": "HOLE",
                    "addr": idx,
                    "size": segment.size
                })

        segments.sort(key=lambda x: x["addr"])

        used_ram = sum(seg["size"] for seg in segments if seg["type"] == "PROGRAM")
        total_ram = ram_size
        free_ram = total_ram - used_ram
        usage_percent = (used_ram / total_ram) * 100 if total_ram > 0 else 0

        header = (
            f"Memória atualizada ({len(segments)} segmentos)" +
            f"\nUso de RAM (Tamanho total: {total_ram} | "
            f"Em uso: {used_ram} | Livre: {free_ram} | " +
            f"{usage_percent:.2f}%)\n" +
            "=" * 40
        )

        lines = [header]

        for seg in segments:
            addr = seg["addr"]
            size = seg["size"]
            seg_type = seg["type"]
            pid = seg.get("pid", "")

            if seg_type == "PROGRAM":
                line = f"{pid} [Addr: {addr:03d}, Size: {size:03d}] | {'#' * min(size, 20)}"
            else:
                line = f"HOLE  [Addr: {addr:03d}, Size: {size:03d}] | {'.' * min(size, 20)}"
            lines.append(line)

        ui_string = "\n".join(lines)


        output_queue.put({
            "text": ui_string,
            "layout": segments,
            "total_size": ram_size
        })

        if not program_segments_with_idx:
            output_queue.put({"text": "DONE: Simulação encerrada.", "layout": []})
            break

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
        #self.setGeometry(100, 100, 600, 400)
        self.setGeometry(100, 100, 800, 500)
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

        self.memory_canvas = MemoryCanvas()
        layout.addWidget(self.memory_canvas)

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

                if isinstance(message, dict):
                    text = message.get("text", "")
                    layout = message.get("layout", [])
                    total_size = message.get("total_size", 1)

                    self.display_label.setText(text)
                    self.memory_canvas.update_layout(layout, total_size)

                    if text.startswith("DONE"):
                        self.stop_simulation()
                else:
                    self.display_label.setText(str(message))


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

