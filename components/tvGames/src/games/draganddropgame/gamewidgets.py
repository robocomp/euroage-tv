import os
import sys

from PySide2.QtCore import QRect, Qt, QSize, QPoint, Signal, QTimer, QTime, QDateTime, QRectF
from PySide2.QtGui import QBrush, QPen,QPalette, QRegion, QColor, QIcon, QPixmap, QPainter, QFont, QFontMetrics
from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, \
    QHBoxLayout, QStyleOption, QStyle, QSizePolicy, QFrame


CURRENT_PATH = os.path.dirname(__file__)

GREEN_TITTLE_COLOR = "#91C69A"


class GameTopBarWidget(QWidget):
    clock_timeout = Signal()
    """	Top bar for the game integrating all the other bar widgets (name, scores, timer)...

    """
    def __init__(self, parent=None):
        super(GameTopBarWidget, self).__init__(parent)
        self._main_layout = QHBoxLayout()
        self.setLayout(self._main_layout)
        self._clock = CountDownWidget()
        self._game_name_label = GameNameWidget("El nombre del juego")
        self._game_scores = GameScores()
        self._main_layout.addWidget(self._game_name_label)
        self._main_layout.addStretch()
        self._main_layout.addWidget(self._game_scores)
        self._main_layout.addWidget(self._clock)
        self._game_scores.setFixedWidth(90)
        self._main_layout.setContentsMargins(0, 0, 10, 0)
        self._clock.timeout.connect(self.clock_timeout.emit)



    # self._main_layout.setStretchFactor(self._game_scores,100)
    # self.setMaximumHeight(100)
    # self._game_scores.setMinimumHeight(100)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.init(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        QWidget.paintEvent(self, event)

    def set_game_name(self, text):
        self._game_name_label.set_text(text)

    def set_time(self, seconds):
        self._clock.set_time(seconds)

    def set_scores(self, value1, value2):
        self._game_scores.set_score(1, value1)
        self._game_scores.set_score(0, value2)

    def set_good_score(self, value):
        self._game_scores.set_score(0, value)

    def set_bad_score(self, value):
        self._game_scores.set_score(1, value)

    def start_clock(self):
        self._clock.start()

    def pause_clock(self):
        self._clock.pause()

    def resume_clock(self):
        self._clock.resume()


# def resizeEvent(self, event):
# 	self._game_scores.setFixedHeight(event.size().height()-20)


class AnalogClock(QWidget):
    HOUR_HAND = [QPoint(7, 8),
                QPoint(-7, 8),
                QPoint(0, -40)]
    def __init__(self, parent=None):
        # QWidget.__init__(self, parent=parent)
        super(AnalogClock, self).__init__(parent)
        self._timer = QTimer()
        self._timer.timeout.connect(self.update)
        self._timer.start(1000)
        self.setWindowTitle("Clock test")
        self.resize(200, 200)
        self.color_clock = QColor(127, 0, 127)

    def paintEvent(self, event):
        side = min(self.width(), self.height())-2
        time = QTime().currentTime()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color_clock)
        pen.setWidth(4)
        painter.setPen(pen)

        painter.drawEllipse(((self.width()-side)/2.)+1, ((self.height()-side)/2.)+1, side-2, side-2)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200.0, side / 200.0)

        painter.setBrush(QBrush(self.color_clock))

        painter.save()
        painter.rotate(-30.0 * time.second())
        painter.drawConvexPolygon(self.HOUR_HAND)
        painter.restore()

        painter.setPen(self.color_clock)

        for i in range(0, 12):
            painter.drawRect(70,0, 15, 10)
            painter.rotate(30.0)

        super(AnalogClock, self).paintEvent(event)

    def setColor(self, q_color):
        self.color_clock = q_color

    def pause(self):
        self._timer.stop()

    def resume(self):
        self._timer.start(1000)


class ClockLabelWidget(QLabel):
    """	Countdown clock shown in a QLabel
        This class is responsible of emmiting the signal of the countdown timeout.


    """
    timeout = Signal()

    def __init__(self, parent=None):
        super(ClockLabelWidget, self).__init__("00:00", parent)
        self.setFont(QFont("Arial", 20))
        self._time = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self.update_timer)
        self.setStyleSheet(
            ".ClockLabelWidget{ background-color: white; border-radius: 12px;}")
        self.setFixedHeight(30)

    # self._label.setStyleSheet("border-radius: 12px; background: #91C69A; color: black;")

    def show(self):
        self.update_timer()
        super(ClockLabelWidget, self).show()

    def update_timer(self):
        try:
            time_string = QDateTime.fromTime_t(self._time).toString("mm:ss")
            self.setText(time_string)
            if self._timer.isActive():
                if self._time <= 0:
                    self.timeout.emit()
                    self._timer.stop()
                else:
                    self._time = self._time - 1
        except Exception as e:
            print("Catched exception %s" % e.message)

    def set_time(self, t):
        self._time = t
        self.update_timer()

    def start(self):
        self._timer.start(1000)

    def pause(self):
        self._timer.stop()

    def resume(self):
        self._timer.start(1000)



class CountDownWidget(QFrame):
    """Frame with layout to integrate the clock label and the analog clock animation.

    """
    timeout = Signal()
    def __init__(self, parent=None):
        super(CountDownWidget, self).__init__(parent)
        self._main_layout = QHBoxLayout()
        self._main_layout.setContentsMargins(6, 0, 6, 0)
        self._clock_label = ClockLabelWidget()
        self._analog_clock = AnalogClock()
        self._main_layout.addWidget(self._clock_label)
        self._analog_clock.setFixedSize(40, 40)
        self._analog_clock.setColor(QColor("dimgrey"))
        self._main_layout.addWidget(self._analog_clock)
        self.setLayout(self._main_layout)
        self.setStyleSheet(
            ".CountDownWidget{ background-color: lightgray; border : 0px solid blue; border-right : 2px solid gray;border-left : 2px solid gray;}")
        self._clock_label.timeout.connect(self.timeout.emit)
        self._clock_label.timeout.connect(self.pause)




    def set_time(self, value):
        self._clock_label.set_time(value)

    def start(self):
        self._clock_label.start()
        self._analog_clock.resume()

    def pause(self):
        self._clock_label.pause()
        self._analog_clock.pause()

    def resume(self):
        self._clock_label.resume()
        self._analog_clock.resume()

class BullseyeWidget(QWidget):
    """	Just a widget illustration for the bullseye icon

    """
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
        self._border_widh = 4

    def heightForWidth(self, width):
        return width

    def minimumSizeHint(self):
        return QSize(10, 10)

    def sizeHint(self):
        return QSize(50, 50)

    def paintEvent(self, event):
        inital_rect = self.rect()
        diameter = min(inital_rect.width(), inital_rect.height()) - self._border_widh
        painter = QPainter(self)
        painter.save()
        color_pen = QPen(self._color)
        outer_pen = QPen(self._out_color)
        outer_pen.setWidth(self._border_widh)
        painter.setPen(outer_pen)
        color_brush = QBrush(self._color)
        painter.setBrush(color_brush)
        centered_x = (self.width() - diameter) / 2.
        centered_y = (self.height() - diameter) / 2.
        ellipse_width = diameter - self._border_widh / 2

        painter.drawEllipse(centered_x + 1, centered_y + 1, ellipse_width, ellipse_width)
        # painter.drawEllipse(QRectF(0, 0, diameter, diameter))

        new_diameter = diameter / 1.4
        white_pen = QPen(Qt.white)
        painter.setPen(white_pen)
        white_brush = QBrush(Qt.white)
        painter.setBrush(white_brush)

        centered_x = (self.width() - new_diameter) / 2.
        centered_y = (self.height() - new_diameter) / 2.
        painter.drawEllipse(
            QRectF(centered_x, centered_y, new_diameter, new_diameter))

        new_diameter = new_diameter / 1.4
        painter.setBrush(color_brush)
        painter.setPen(color_pen)
        centered_x = (self.width() - new_diameter) / 2.
        centered_y = (self.height() - new_diameter) / 2.
        painter.drawEllipse(
            QRectF(centered_x, centered_y, new_diameter, new_diameter))

        new_diameter = new_diameter / 2
        painter.setBrush(white_brush)
        painter.setPen(white_pen)
        centered_x = (self.width() - new_diameter) / 2.
        centered_y = (self.height() - new_diameter) / 2.
        painter.drawEllipse(
            QRectF(centered_x, centered_y, new_diameter, new_diameter))
        painter.restore()
        super(BullseyeWidget, self).paintEvent(event)


class GameNameWidget(QWidget):
    def __init__(self, text, size=25, parent=None):
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

    def set_text(self, text):
        self._label.setText(text)

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
        self._main_layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(self._main_layout)
        self._bad_score = GameScoreCircleLabel()
        self._bad_score.set_colors(QColor("Red"), QColor("White"))
        self._good_score = GameScoreCircleLabel()
        self._good_score.set_colors(QColor("Green"), QColor("Black"))
        self._main_layout.setAlignment(self._good_score, Qt.AlignRight)
        self._main_layout.addWidget(self._good_score)
        self._main_layout.addWidget(self._bad_score)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet(
            ".GameScores{ background-color: lightgray; border : 0px solid blue; border-right : 2px solid gray;border-left : 2px solid gray;}")

    def set_score(self, index, value):
        if index == 0:
            self._bad_score.set_value(value)
        elif index == 1:
            self._good_score.set_value(value)
        else:
            raise IndexError("Index error for scores")

    # def sizeHint(self):
    # 	sum_size = self._bad_score.sizeHint()+self._good_score.sizeHint()
    # 	print(sum_size)
    # 	return sum_size

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.init(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        QWidget.paintEvent(self, event)


class GameScreenLogo(QLabel):
    def __init__(self, parent=None):
        super(GameScreenLogo, self).__init__(parent)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMaximumSize(QSize(600, 100))
        self.setText("")
        self.setPixmap(QPixmap("../../etc/logos_banner.jpg"))
        self.setScaledContents(True)


class GameScoreCircle(QLabel):
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
        self.setBackgroundRole(QPalette.Base)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    # self.setStyleSheet("border: 1px solid black")

    def minimumSizeHint(self):
        return QSize(30, 30)

    #
    #
    def sizeHint(self):
        if self.parent():
            max_s = max(self.parent().width(), self.parent().height())
            return QSize(max_s, max_s)
        else:
            width = self._font_metrics.width(str(self._value))
            return QSize(width, width)

    # min_s = min(self.width(), self.height())
    # print(self.width(), self.height(), min_s)
    # 	return QSize(30, 30)

    # def sizeHint(self):
    # 	return QSize(self._font_metrics.width(str(self._value)),self._font_metrics.height())
    #

    def paintEvent(self, event):
        inital_rect = self.rect()
        diameter = min(inital_rect.width(), inital_rect.height())
        self.resize_font()
        painter = QPainter(self)
        painter.save()
        outer_pen = QPen(self._border_color)
        outer_pen.setWidth(self._border_width)
        painter.setPen(outer_pen)
        color_brush = QBrush(self._color)
        painter.setBrush(color_brush)
        painter.drawEllipse(((self.width() - diameter) / 2.) + 1, ((self.height() - diameter) / 2.) + 1, diameter - 2,
                            diameter - 2)
        # painter.drawEllipse(0,0,diameter,diameter)
        # painter.translate(diameter/2,diameter/2)

        painter.setBrush(QBrush(QColor("Black")))

        painter.setBrush(QBrush(self._text_color))
        outer_pen = QPen(self._text_color)
        painter.setPen(outer_pen)
        # painter.drawText(self._font_metrics.width(str(self._value))/2, self._font_metrics.height()/2, str(self._value))
        painter.drawText(QRectF(0, 0, diameter, diameter), Qt.AlignCenter | Qt.AlignTop, str(self._value))
        opt = QStyleOption()
        opt.init(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.restore()
        super(GameScoreCircle, self).paintEvent(event)

    def set_value(self, value):
        self._value = value

    def set_font(self, font):
        self._font = font
        self.resize_font()

    def set_color(self, color):
        self._color = color
        self._border_color = color

    def set_text_color(self, text_color):
        self._text_color = text_color

    def set_colors(self, color, text_color, border_color=None):
        self._color = color
        self._text_color = text_color
        if border_color is not None:
            self._border_color = border_color
        else:
            self._border_color = color

    def set_border_width(self, width):
        self._border_width = width

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
            next_point_size = next_point_size * 0.9
            self._font.setPointSize(next_point_size)
            self._font_metrics = QFontMetrics(self._font)
            self.setFont(self._font)


class GameScoreCircleLabel(QLabel):
    def __init__(self, value=0, parent=None):
        super(GameScoreCircleLabel, self).__init__(parent)
        self._font = QFont("times", 24)
        self.setFont(self._font)
        self._font_metrics = self.fontMetrics()
        self.set_value(value)
        self._border_color = QColor("Red")
        self._color = QColor("Red")
        # self._text_color = QColor("White")
        self._border_width = 1
        # self.setBackgroundRole(QPalette.Base)
        # sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # sizePolicy.setHeightForWidth(True)
        # self.setSizePolicy(sizePolicy)
        # self.setStyleSheet("border: 1px solid black")
        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        inital_rect = self.rect()
        diameter = min(inital_rect.width(), inital_rect.height()) - self._border_width
        # self.resize_font()
        painter = QPainter(self)
        painter.save()
        outer_pen = QPen(self._border_color)
        outer_pen.setWidth(self._border_width)
        painter.setPen(outer_pen)
        color_brush = QBrush(self._color)
        painter.setBrush(color_brush)
        painter.drawEllipse((self.width() - diameter) / 2, (self.height() - diameter) / 2, diameter, diameter)
        # # painter.translate(diameter/2,diameter/2)
        #
        # painter.setBrush(QBrush(QColor("Black")))
        #
        # painter.setBrush(QBrush(self._text_color))
        # outer_pen = QPen(self._text_color)
        # painter.setPen(outer_pen)
        # # painter.drawText(self._font_metrics.width(str(self._value))/2, self._font_metrics.height()/2, str(self._value))
        # painter.drawText(QRectF(0, 0, diameter, diameter), Qt.AlignCenter | Qt.AlignTop, str(self._value))
        # opt = QStyleOption()
        # opt.init(self)
        # self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        painter.restore()
        super(GameScoreCircleLabel, self).paintEvent(event)

    def set_value(self, value):
        self.setText(str(value))

    def set_font(self, font):
        self._font = font
        self.resize_font()

    def set_color(self, color):
        self._color = color
        self._border_color = color

    def set_text_color(self, text_color):
        self._text_color = text_color
        palette = self.palette()
        palette.setColor(self.foregroundRole(), text_color)
        self.setPalette(palette)

    def set_colors(self, color, text_color, border_color=None):
        self.set_color(color)
        self.set_text_color(text_color)
        if border_color is not None:
            self._border_color = border_color
        else:
            self._border_color = color

    def set_border_width(self, width):
        self._border_width = width

# def resizeEvent(self, event):
# 	self.resize_font()
# 	super(GameScoreCircleLabel, self).resizeEvent(event)

# def resize_font(self):
# 	inital_rect = self.rect()
# 	diameter = min(inital_rect.width() - 4, inital_rect.height() - 4)
# 	if diameter > 1:
# 		next_point_size = float(diameter)
# 		self._font.setPointSize(next_point_size)
# 		self._font_metrics = QFontMetrics(self._font)
# 		while self._font_metrics.width(str(self.text())) > diameter and next_point_size > 3:
# 			next_point_size = next_point_size * 0.9
# 			self._font.setPointSize(next_point_size)
# 			self._font_metrics = QFontMetrics(self._font)
# 		next_point_size = next_point_size * 0.9
# 		self._font.setPointSize(next_point_size)
# 		self._font_metrics = QFontMetrics(self._font)
# 		self.setFont(self._font)


class CoolButton(QPushButton):
    def __init__(self,image_path, text="", size=200, offset=20, color=QColor("green"), img=None, parent=None):
        super(CoolButton, self).__init__(parent)
        self._size = size
        self._offset = offset
        self.setFixedSize(QSize(size, size))
        self.set_color(color)
        self.__text = text
        self.__image_path = image_path
        self.__size = size
        self.__offset = offset
        self.__color = color
        self.repaint()


        # self.setMask(QRegion(QRect(OFFSET/4, OFFSET/4, self._size-OFFSET, self._size-OFFSET), QRegion.Ellipse))
        self.setMask(
            QRegion(
                QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2,
                      self._size - self._offset, self._size - self._offset),
                QRegion.Ellipse))

        self.pressed.connect(self._button_pressed)
        self.released.connect(self._button_released)

        # Shadow
        self._set_released_shadow()

    def setText(self, text):
        self.__text = text
        self.repaint()

    def repaint(self):
        pixmap = QPixmap(self.__image_path).scaled(QSize(self.__size, self.__size))
        painter = QPainter(pixmap)
        f = QFont("Arial", self.__size / 12, QFont.Bold)
        painter.setFont(f)
        font_size = QFontMetrics(f).width(self.__text.upper())
        painter.drawText(QPoint((self.__size - font_size) / 2 + 2, self.__size * 0.8), self.__text.upper())
        painter.end()
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(pixmap.rect().size())

    def set_color(self, color):
        if isinstance(color, QColor):
            self.setStyleSheet(
                "QPushButton:!hover { background-color:" + color.name() + ";  }")
            self.update()
        else:
            raise Exception("color must be a QColor class")

    def _set_pressed_shadow(self):
        pressed_shadow = QGraphicsDropShadowEffect(self)
        pressed_shadow.setBlurRadius(10)
        pressed_shadow.setOffset(2)
        self.setGraphicsEffect(pressed_shadow)
        self.update()

    def _set_released_shadow(self):
        released_shadow = QGraphicsDropShadowEffect(self)
        released_shadow.setBlurRadius(22)
        released_shadow.setOffset(10)
        self.setGraphicsEffect(released_shadow)
        self.update()

    def _button_pressed(self):
        self.w, self.h = self.width() - self._offset, self.height() - self._offset
        self.offset = self._offset / 2

        self.setMask(QRegion(QRect(
            (self._size - (self.w + self.offset)) / 2,
            (self._size - (self.h + self.offset)) / 2,
            self.w + self.offset,
            self.h + self.offset), QRegion.Ellipse))

        self._set_pressed_shadow()

    def _button_released(self):
        self.setMask(
            QRegion(
                QRect((self._size - (self._size - self._offset)) / 2, (self._size - (self._size - self._offset)) / 2,
                      self._size - self._offset, self._size - self._offset),
                QRegion.Ellipse))

        self._set_released_shadow()

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




######################## TESTING FUNCTIONS ########################
###################################################################


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
    #
    ###### Game Name Widget
    #
    game_name_widget = GameNameWidget("The name you want")
    game_name_widget.show()
    #
    ###### bulleye
    #
    bulleye = BullseyeWidget()
    bulleye.setFixedSize(100, 100)
    bulleye.setWindowTitle("BULLsEYE")
    bulleye.show()
    #
    ###### game scores circle
    #
    score_circle = GameScoreCircleLabel(200000)
    score_circle.set_colors(QColor("black"), QColor("White"), QColor("Red"))
    score_circle.set_border_width(5)
    score_circle.setWindowTitle("Score circle")
    score_circle.show()

    ###### game scores

    from PySide2.QtCore import QCoreApplication, QEventLoop
    from time import sleep

    scores = GameScores()
    scores.set_score(0, 40000)
    scores.set_score(1, 100000000)
    scores.show()

    for points in range(0,100):
        if points % 3:
            scores.set_score(0,points)
        else:
            scores.set_score(1, points)
        QCoreApplication.processEvents(QEventLoop.AllEvents, 100)
        sleep(1)

    ###### analog_clock
    analog_clock = AnalogClock()
    analog_clock.show()
    #
    #
    ###### top_bar
    top_bar = GameTopBarWidget()
    top_bar.show()


    ###### cool button
    widget = QWidget()
    text = QLabel()
    text = QLabel("Hello World")
    text.setAlignment(Qt.AlignCenter)
    button = CoolButton(text="AYUDA",
                        image_path="/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/draganddropgame/resources/button/justQuestion.png")
    button.set_color(QColor("Orange"))
    button2 = CoolButton(text="FINALIZAR",
                         image_path="/home/robocomp/robocomp/components/euroage-tv/components/tvGames/src/games/draganddropgame/resources/button/checked.png")
    layout_h = QHBoxLayout()
    layout_h.addWidget(button)
    layout_h.addWidget(button2)

    layout_v = QVBoxLayout()
    layout_v.addWidget(text)
    layout_v.addLayout(layout_h)
    widget.setLayout(layout_v)
    widget.show()

    sys.exit(app.exec_())
