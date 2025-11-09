import sys
import time
import json
from multiprocessing import Process, Queue, Value

from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QIcon
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from memsim.memory_canvas import MemoryCanvas


def run_simulation_worker(output_queue, show_holes_flag):
    from memsim.memsim import MEMSIM
    from memsim.segment import PROGRAM, HOLE

    config_file = "ini.json"
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    ram_size = config_data.get("setup", {}).get("ram_size", 128)
    memsim = MEMSIM(config_file)

    while True:
        memsim.step()
        state = memsim.get_state()
        show_holes = show_holes_flag.value
        segments = []

        program_segments_with_idx = state.get_all_segments_of_type(PROGRAM)
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

        output_queue.put({
            "segments": segments,
            "used_ram": used_ram,
            "free_ram": free_ram,
            "total_ram": total_ram,
            "usage_percent": usage_percent
        })

        if not program_segments_with_idx:
            output_queue.put({"done": True})
            break

        time.sleep(1)


class MemoryStatsChart(QWidget):
    """Widget com gráficos de barras e pizza + legenda."""
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setStyleSheet("background-color: #1e1e1e;")

        self.placeholder = QLabel("Aguardando início da simulação...")
        self.placeholder.setStyleSheet("color: gray; font-size: 14px; font-style: italic;")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.placeholder)

        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)

        if not MATPLOTLIB_AVAILABLE:
            msg = QLabel("Matplotlib não encontrado. Execute: pip install matplotlib")
            msg.setStyleSheet("color: #ff5555; font-size: 14px;")
            self.chart_layout.addWidget(msg)
        else:
            self.figure = Figure(figsize=(6, 3), facecolor="#1e1e1e")
            self.canvas = FigureCanvas(self.figure)
            self.ax_bar = self.figure.add_subplot(121)
            self.ax_pie = self.figure.add_subplot(122)
            self.figure.tight_layout()
            self.chart_layout.addWidget(self.canvas)

            # legenda colorida
            legend_layout = QHBoxLayout()
            legend_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            legend_layout.addWidget(self._make_legend_item("🟩 Uso leve (<30%)"))
            legend_layout.addWidget(self._make_legend_item("🟧 Uso médio (30–60%)"))
            legend_layout.addWidget(self._make_legend_item("🟥 Uso alto (>60%)"))
            self.chart_layout.addLayout(legend_layout)

        self.layout.addWidget(self.chart_container)
        self.chart_container.hide()  # começa escondido

    def _make_legend_item(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: white; font-size: 12px;")
        return label

    def update_charts(self, segments, used_ram, free_ram, total_ram):
        if not MATPLOTLIB_AVAILABLE:
            return

        self.placeholder.hide()
        self.chart_container.show()

        self.ax_bar.clear()
        self.ax_pie.clear()

        pids = [seg["pid"] for seg in segments if seg["type"] == "PROGRAM"]
        sizes = [seg["size"] for seg in segments if seg["type"] == "PROGRAM"]

        if not pids:
            self.canvas.draw()
            return

        colors = []
        for s in sizes:
            perc = s / total_ram
            if perc < 0.3:
                colors.append("#00FF88")  # verde
            elif perc < 0.6:
                colors.append("#FFA500")  # laranja
            else:
                colors.append("#FF5555")  # vermelho

        # gráfico de barras
        bars = self.ax_bar.barh(pids, sizes, color=colors)
        self.ax_bar.set_facecolor("#1e1e1e")
        self.ax_bar.set_title("Uso por PID", color="white", fontsize=10)
        self.ax_bar.tick_params(axis='x', colors='white')
        self.ax_bar.tick_params(axis='y', colors='white')
        self.ax_bar.spines['bottom'].set_color('#888888')
        self.ax_bar.spines['left'].set_color('#888888')

        # adiciona labels com tamanhos sobre as barras
        for bar, size in zip(bars, sizes):
            self.ax_bar.text(
                bar.get_width() + 2,
                bar.get_y() + bar.get_height() / 2,
                f"{size} MB",
                va='center',
                color='white',
                fontsize=9
            )

        # gráfico de pizza
        self.ax_pie.pie(
            [used_ram, free_ram],
            labels=["Usado", "Livre"],
            autopct="%1.1f%%",
            colors=["#00FFFF", "#404040"],
            textprops={"color": "white"}
        )
        self.ax_pie.set_title("RAM Total", color="white", fontsize=10)

        self.figure.tight_layout()
        self.canvas.draw()


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
        self.setGeometry(100, 100, 1000, 700)

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#121212"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        title = QLabel("MEMSIM - Simulação de Memória")
        title.setStyleSheet("color: cyan; font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # estilos de botão
        btn_style_active = """
            QPushButton {
                background-color: #00FFFF;
                color: black;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover { background-color: #00cccc; }
        """
        btn_style_inactive = """
            QPushButton {
                background-color: #333333;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover { background-color: #444444; }
        """

        controls = QHBoxLayout()

        play_icon = QPixmap(16, 16)
        play_icon.fill(Qt.GlobalColor.transparent)
        painter = QPainter(play_icon)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        points = [  # triângulo de play
            (4, 3),
            (12, 8),
            (4, 13)
        ]
        poly = [QPointF(x, y) for x, y in points]
        painter.drawPolygon(*poly)
        painter.end()
        play_icon_obj = QIcon(play_icon)

        self.start_button = QPushButton("Iniciar Simulação")
        self.start_button.setIcon(play_icon_obj)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #00FFFF;
                color: black;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00cccc;
            }
        """)
        self.start_button.clicked.connect(self.start_simulation)

        # botão de pausa com ícone branco vetorial
        pause_icon = QPixmap(16, 16)
        pause_icon.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pause_icon)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(Qt.PenStyle.NoPen)
        # Desenha as duas barrinhas de pausa
        bar_width = 4
        bar_height = 12
        spacing = 4
        painter.drawRect(2, 2, bar_width, bar_height)
        painter.drawRect(2 + bar_width + spacing, 2, bar_width, bar_height)
        painter.end()

        pause_icon_obj = QIcon(pause_icon)

        self.stop_button = QPushButton("Pausar Simulação")
        self.stop_button.setIcon(pause_icon_obj)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #555555;
                color: #00FFFF;
            }
        """)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_simulation)

        hole_icon = QPixmap(16, 16)
        hole_icon.fill(Qt.GlobalColor.transparent)
        painter = QPainter(hole_icon)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.GlobalColor.white)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(3, 3, 10, 10)
        painter.end()
        hole_icon_obj = QIcon(hole_icon)

        self.show_holes_button = QPushButton("Mostrar Holes")
        self.show_holes_button.setIcon(hole_icon_obj)
        self.show_holes_button.setCheckable(True)
        self.show_holes_button.setStyleSheet("""
            QPushButton {
                background-color: #00FFFF;
                color: black;
                border-radius: 6px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00cccc;
            }
        """)
        self.show_holes_button.toggled.connect(self.toggle_holes)

        controls.addWidget(self.start_button)
        controls.addWidget(self.stop_button)
        controls.addWidget(self.show_holes_button)
        layout.addLayout(controls)

        # Gráficos
        self.chart = MemoryStatsChart()
        layout.addWidget(self.chart)

        # Canvas de memória
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

    def stop_simulation(self):
        self.queue_timer.stop()
        if self.sim_process and self.sim_process.is_alive():
            self.sim_process.terminate()
            self.sim_process.join()
        self.sim_process = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def check_ui_queue(self):
        if self.ui_queue is None:
            return
        try:
            while not self.ui_queue.empty():
                msg = self.ui_queue.get_nowait()
                if "done" in msg:
                    self.stop_simulation()
                    return
                segments = msg.get("segments", [])
                used = msg.get("used_ram", 0)
                free = msg.get("free_ram", 0)
                total = msg.get("total_ram", 1)
                self.chart.update_charts(segments, used, free, total)
                self.memory_canvas.update_layout(segments, total)
        except Exception:
            pass

    def toggle_holes(self, checked):
        self.show_holes_flag.value = checked

        # Redesenha o ícone dinamicamente
        icon_pix = QPixmap(16, 16)
        icon_pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(icon_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.GlobalColor.white)
        if checked:
            painter.setBrush(QBrush(Qt.GlobalColor.white))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(3, 3, 10, 10)
        painter.end()

        self.show_holes_button.setIcon(QIcon(icon_pix))
        self.show_holes_button.setText("Esconder Holes" if checked else "Mostrar Holes")


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
