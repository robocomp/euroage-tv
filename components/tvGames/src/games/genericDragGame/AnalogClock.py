import os
import sys

from PySide2.QtCore import Signal, QTimer, Qt, QPoint, QTime
from PySide2.QtGui import QColor, QPainter, QBrush
from PySide2.QtWidgets import QApplication, QWidget

hourHand = [QPoint(7, 8),
            QPoint(-7, 8),
            QPoint(0, -40)]


class AnalogClock(QWidget):
    def __init__(self, parent=None):
        # QWidget.__init__(self, parent=parent)
        super(AnalogClock, self).__init__(parent)
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(200)
        self.setWindowTitle("Clock test")
        self.resize(200, 200)
        self.color_clock = QColor(127, 0, 127)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime().currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.color_clock))

        painter.save()
        painter.rotate(30.0 * time.second())
        painter.drawConvexPolygon(hourHand)
        painter.restore()

        painter.setPen(self.color_clock)

        for i in range(0, 12):
            painter.drawLine(88, 0, 96, 0)
            painter.rotate(30.0)

        super(AnalogClock, self).paintEvent(event)

    def setColor(self, q_color):
        self.color_clock = q_color


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = AnalogClock()
    w.show()
    sys.exit(app.exec_())
