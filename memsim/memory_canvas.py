# memsim/memory_canvas.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt

class MemoryCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(120)
        self.memory_layout = []
        self.total_size = 1

    def update_layout(self, layout, total_size):
        self.memory_layout = layout
        self.total_size = max(total_size, 1)
        self.update() 

    def paintEvent(self, event):
        if not self.memory_layout:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        x = 0

        for segment in self.memory_layout:
            size = segment.get("size", 1)
            seg_type = segment.get("type", "HOLE")
            pid = segment.get("pid", None)

            if seg_type == "PROGRAM":
                color = QColor(50, 180, 90)
            elif seg_type == "HOLE":
                color = QColor(130, 130, 130)
            else:
                color = QColor(180, 90, 50)

            seg_width = width * (size / self.total_size)
            painter.setBrush(color)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(int(x), 10, int(seg_width), int(height - 20))


            label = f"{pid}" if pid is not None else seg_type
            painter.drawText(int(x) + 5, int(height // 2), label)

            x += seg_width
            x = int(x)

        painter.end()
