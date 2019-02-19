import sys

from PyQt4.QtCore import QDateTime, pyqtSignal, QTimer
from PyQt4.QtGui import QFont, QGraphicsTextItem, QApplication, QLabel


class ClockWidget(QLabel):
	timeout = pyqtSignal()

	def __init__(self, parent=None):
		super(ClockWidget, self).__init__("00:00", parent)
		self.setFont(QFont("Arial", 70, QFont.Bold))
		self.time = 0
		self.timer = QTimer()
		self.timer.timeout.connect(self.update)
	
	def show(self):
		self.update()
		super(ClockWidget, self).show()

	def update(self):
		time_string = QDateTime.fromTime_t(self.time).toString("mm:ss")
		self.setText(time_string)
		if self.timer.isActive() and self.time <= 0:
			self.timeout.emit()
			self.timer.stop()
		self.time = self.time - 1

	def set_time(self,t):
		self.time = t
		self.update()

	def start(self):
		self.timer.start(1000)

def time_out_clock():
	print("Ringing")

if __name__ == '__main__':
	app = QApplication(sys.argv)
	clock = ClockWidget()
	clock.show()
	clock.set_time(3)
	clock.timeout.connect(time_out_clock)
	clock.start()
	app.exec_()
