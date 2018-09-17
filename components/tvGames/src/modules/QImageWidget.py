import cv2

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QHBoxLayout, QLabel, QPixmap, QImage, QApplication


class QImageWidget(QWidget):
    def __init__(self, parent=None):
        super(QImageWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)
        self.label = QLabel()
        self.layout.addWidget(self.label)
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)
        self.image = QImage()
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)

    def set_opencv_image(self, raw_image, BGR=True):
        if raw_image is not None:
            if BGR:
                raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
            print "DEBUG: QImageWidget: %s"%str(raw_image.shape)
            self.image = QImage(raw_image, raw_image.shape[1], \
                                raw_image.shape[0], raw_image.shape[1] * 3,
                                QImage.Format_RGB888)
            self.pixmap = QPixmap(self.image)
            self.label.setPixmap(self.pixmap)

    def show_on_second_screen(self):
        desktop_widget = QApplication.desktop()
        if desktop_widget.screenCount() > 1 and not self.isMaximized():
            second_screen_size = desktop_widget.screenGeometry(1)
            self.move(second_screen_size.left(), second_screen_size.top())
            # self.resize(second_screen_size.width(), second_screen_size.height())
            self.showMaximized()