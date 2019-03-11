import sys

from PySide2.QtCore import Signal, QTimer, QDateTime
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QLabel, QApplication


class ClockWidget(QLabel):
	timeout = Signal()

	def __init__(self, parent=None):
		super(ClockWidget, self).__init__("00:00", parent)
		self.setFont(QFont("Arial", 70, QFont.Bold))
		self._time = 0
		self._timer = QTimer()
		self._timer.timeout.connect(self.update_timer)

	
	def show(self):
		self.update_timer()
		super(ClockWidget, self).show()

	def update_timer(self):
		try:
			time_string = QDateTime.fromTime_t(self._time).toString("mm:ss")
			self.setText(time_string)
			if self._timer.isActive() and self._time <= 0:
				self.timeout.emit()
				self._timer.stop()
			self._time = self._time - 1
		except Exception as e:
			print("Catched exception %s"%e.message)

	def set_time(self,t):
		self._time = t
		self.update_timer()

	def start(self):
		self._timer.start(1000)

def time_out_clock():
	print("Ringing")

if __name__ == '__main__':
	app = QApplication(sys.argv)
	clock = ClockWidget()
	clock.show()
	clock.set_time(7)
	clock.start()
	sys.exit(app.exec_())
