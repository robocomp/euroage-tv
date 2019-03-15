import os
import sys

from PySide2.QtCore import Signal, QTimer, QDateTime, QRectF, Qt, QSize, QPoint
from PySide2.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPalette, QFontMetrics
from PySide2.QtWidgets import QLabel, QApplication, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, \
	QStyleOption, QStyle, QSizePolicy, QFrame

CURRENT_PATH = os.path.dirname(__file__)


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
			print("Catched exception %s" % e.message)

	def set_time(self, t):
		self._time = t
		self.update_timer()

	def start(self):
		self._timer.start(1000)


def time_out_clock():
	print("Ringing")


GREEN_TITTLE_COLOR = "#91C69A"


class GameTopBarWidget(QWidget):
	def __init__(self, parent=None):
		super(GameTopBarWidget, self).__init__(parent)
		self._main_layout = QHBoxLayout()
		self.setLayout(self._main_layout)
		self._clock = ClockWidget()
		self._game_name_label = GameNameWidget("El nombre del juego")
		self._main_layout.addWidget(self._game_name_label)
		self._main_layout.addStretch()
		self._main_layout.addWidget(self._clock)
		self.setMaximumHeight(100)

	def paintEvent(self, event):
		opt = QStyleOption()
		opt.init(self)
		p = QPainter(self)
		self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
		QWidget.paintEvent(self, event)


class BullseyeWidget(QWidget):
	def __init__(self, color=QColor(GREEN_TITTLE_COLOR), out_color=None, parent=None):
		super(BullseyeWidget, self).__init__(parent)
		self._color = color
		if out_color is None:
			self._out_color = self._color.dark(150)
		else:
			self._out_color = out_color
		self.setMinimumSize(10, 10)
		self.setBackgroundRole(QPalette.Base)
		sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		sizePolicy.setHeightForWidth(True)
		self.setSizePolicy(sizePolicy)

	def heightForWidth(self, width):
		return width * 1.5

	def minimumSizeHint(self):
		return QSize(10, 10)

	def sizeHint(self):
		return QSize(50, 50)


	def paintEvent(self, event):
		inital_rect = self.rect()
		diameter = min(inital_rect.width() - 4, inital_rect.height() - 4)
		painter = QPainter(self)
		painter.save()
		color_pen = QPen(self._color)
		outer_pen = QPen(self._out_color)
		outer_pen.setWidth(3)
		painter.setPen(outer_pen)
		color_brush = QBrush(self._color)
		painter.setBrush(color_brush)
		painter.drawEllipse(QRectF(0, 0, diameter, diameter))

		new_diameter = diameter / 1.4
		white_pen = QPen(Qt.white)
		painter.setPen(white_pen)
		white_brush = QBrush(Qt.white)
		painter.setBrush(white_brush)
		painter.drawEllipse(
			QRectF((diameter - new_diameter) / 2, (diameter - new_diameter) / 2, new_diameter, new_diameter))

		new_diameter = new_diameter / 1.4
		painter.setBrush(color_brush)
		painter.setPen(color_pen)
		painter.drawEllipse(
			QRectF((diameter - new_diameter) / 2, (diameter - new_diameter) / 2, new_diameter, new_diameter))

		new_diameter = new_diameter / 2
		painter.setBrush(white_brush)
		painter.setPen(white_pen)
		painter.drawEllipse(
			QRectF((diameter - new_diameter) / 2, (diameter - new_diameter) / 2, new_diameter, new_diameter))
		painter.restore()
		super(BullseyeWidget, self).paintEvent(event)


class ScoreWidget(QWidget):

	def __init__(self):
		super(ScoreWidget, self).__init__()


class GameNameWidget(QWidget):
	def __init__(self, text, size=30, parent=None):
		super(GameNameWidget, self).__init__(parent)
		self._main_layout = QHBoxLayout()
		self.setLayout(self._main_layout)
		self._bulleyeicon = BullseyeWidget()
		self._label = QLabel(text)
		name_font = QFont("Times", size)
		self._label.setFont(name_font)
		self._label.setStyleSheet("border-radius: 12px; background: #91C69A; color: black;")
		self._label.setContentsMargins(10, 0, 10, 0)
		self._main_layout.addWidget(self._bulleyeicon)
		self._main_layout.addWidget(self._label)
		self._main_layout.addStretch(100)
		self.setContentsMargins(2, 2, 2, 2)
		self._main_layout.setContentsMargins(2, 2, 2, 2)

	# #
	def resizeEvent(self, event):
		super(GameNameWidget, self).resizeEvent(event)
		self._bulleyeicon.setMinimumWidth(self._label.height())

	def paintEvent(self, event):
		opt = QStyleOption()
		opt.init(self)
		p = QPainter(self)
		self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
		QWidget.paintEvent(self, event)


class GameScores(QFrame):
	def __init__(self, parent=None):
		super(GameScores, self).__init__(parent)
		self._main_layout = QHBoxLayout()
		self.setLayout(self._main_layout)
		self._bad_score = GameScoreCircle()
		self._bad_score.set_colors(QColor("Red"), QColor("White"))
		self._good_score = GameScoreCircle()
		self._good_score.set_colors(QColor("Green"), QColor("Black"))
		self._main_layout.addWidget(self._good_score)
		self._main_layout.addWidget(self._bad_score)

	def set_score(self, index, value):
		if index==0:
			self._bad_score.set_value(value)
		elif index == 1:
			self._good_score.set_value(value)
		else:
			raise IndexError("Index error for scores")





	def paintEvent(self, event):
		opt = QStyleOption()
		opt.init(self)
		p = QPainter(self)
		self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
		QWidget.paintEvent(self, event)

class GameScoreCircle(QWidget):
	def __init__(self, value=0, parent=None):
		super(GameScoreCircle, self).__init__(parent)
		self._font = QFont("times", 24)
		self._font_metrics = QFontMetrics(self._font)
		self.setFont(self._font)
		self._value = value
		self._border_color = QColor("Red")
		self._color = QColor("Red")
		self._text_color = QColor("White")
		self._border_width = 1


	def set_font(self, font):
		self._font = font
		self.resize_font()

	def set_color(self, color):
		self._color = color
		self._border_color = color

	def set_text_color(self, text_color):
		self._text_color = text_color

	def set_colors(self, color, text_color, border_color = None):
		self._color = color
		self._text_color = text_color
		if border_color is not None:
			self._border_color = border_color
		else:
			self._border_color = color

	def resize_font(self):
		inital_rect = self.rect()
		diameter = min(inital_rect.width() - 4, inital_rect.height() - 4)
		if diameter > 0:
			next_point_size = diameter
			self._font.setPointSize(next_point_size)
			self._font_metrics = QFontMetrics(self._font)
			while self._font_metrics.width(str(self._value)) > diameter:
				next_point_size = next_point_size * 0.9
				self._font.setPointSize(next_point_size)
				self._font_metrics = QFontMetrics(self._font)
			self.setFont(self._font)

	def set_border_width(self, width):
		self._border_width = width

	def paintEvent(self, event):
		inital_rect = self.rect()
		diameter = min(inital_rect.width() - 4, inital_rect.height() - 4)
		self.resize_font()
		painter = QPainter(self)
		painter.save()
		outer_pen = QPen(self._border_color)
		outer_pen.setWidth(self._border_width)
		painter.setPen(outer_pen)
		color_brush = QBrush(self._color)
		painter.setBrush(color_brush)
		painter.drawEllipse(0,0,diameter,diameter)
		# painter.translate(diameter/2,diameter/2)

		painter.setBrush(QBrush(QColor("Black")))

		painter.setBrush(QBrush(self._text_color))
		outer_pen = QPen(self._text_color)
		painter.setPen(outer_pen)
		# painter.drawText(self._font_metrics.width(str(self._value))/2, self._font_metrics.height()/2, str(self._value))
		painter.drawText(QRectF(0,0,diameter,diameter),Qt.AlignCenter|Qt.AlignTop,str(self._value) )
		painter.restore()
		super(GameScoreCircle, self).paintEvent(event)

	def sizeHint(self):
		return QSize(self._font_metrics.width(str(self._value)),self._font_metrics.height())

class other(QWidget):
	def __init__(self, parent=None):
		super(other, self).__init__(parent)

	# self.setAutoFillBackground(False)

	def paintEvent(self, event):
		opt = QStyleOption()
		opt.init(self)
		p = QPainter(self)
		self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
		QWidget.paintEvent(self, event)


if __name__ == '__main__':
	app = QApplication(sys.argv)

	# ## COLOR CHANGING PROBLEM
	# main_widget = QWidget()
	# main_widget.setWindowTitle("COLOR CHANGING PROBLEM")
	# main_layout = QVBoxLayout()
	# main_widget.setLayout(main_layout)
	#
	# main_widget.setStyleSheet(".QWidget{background-color: blue}")
	#
	# child_widget1 = QWidget()
	# child_widget1.setStyleSheet(".QWidget{background-color: green}")
	#
	# child_widget2 = QWidget()
	# child_widget2.setStyleSheet(".QWidget{background-color: white}")
	#
	# other = other()
	# other.setStyleSheet(".other{background-color: black}")
	#
	# main_widget.setMinimumSize(QSize(600, 600))
	# main_layout.addWidget(child_widget1)
	# main_layout.addWidget(child_widget2)
	# main_layout.addWidget(other)
	#
	# main_widget.show()
	# #####
	#
	# bulleye = BullseyeWidget()
	# bulleye.setFixedSize(100, 100)
	# bulleye.setWindowTitle("BULLsEYE")
	# bulleye.show()
	# ####
	#
	# game_name_widget = GameNameWidget("The name you want")
	# game_name_widget.show()
	#
	# ####
	#
	# top_bar = GameTopBarWidget()
	# top_bar.setStyleSheet(".GameTopBarWidget{background-color: black}")
	# top_bar.show()
	#
	# ###
	#
	# score_circle = GameScoreCircle(200000)
	# score_circle.set_colors(QColor("black"), QColor("White"), QColor("Red"))
	# score_circle.set_border_width(5)
	# score_circle.setWindowTitle("Score circle")
	# score_circle.show()

	######

	scores = GameScores()
	scores.show()

	sys.exit(app.exec_())
