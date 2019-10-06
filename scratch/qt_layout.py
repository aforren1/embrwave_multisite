from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap, QImage
from functools import partial
from base_area import MainWindow


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        qtw.QApplication.instance().quit()


if __name__ == '__main__':
    # main window (fullscreen)
    app = qtw.QApplication([])

    pic = QImage('dv5_1.png').scaledToHeight(600, Qt.SmoothTransformation)
    pic_inst = qtw.QLabel()
    # pic_inst.setScaledContents(True)
    pic_inst.setAlignment(Qt.AlignCenter)
    pic_inst.setPixmap(QPixmap.fromImage(pic))
    pic_inst.setStyleSheet('border:2px solid rgb(0, 0, 0);border-radius:20px;')

    pic2 = qtw.QLabel()
    pic2.setPixmap(QPixmap.fromImage(pic))
    pic3 = qtw.QLabel()
    pic3.setPixmap(QPixmap.fromImage(pic))
    xxx = qtw.QWidget()
    #t0 = qtw.QVBoxLayout()
    t0 = qtw.QGridLayout()
    t0.addWidget(pic_inst, 0, 0, 1, 1, Qt.AlignCenter)
    t0.addWidget(pic2, 1, 0, 1, 1, Qt.AlignLeft)
    t0.addWidget(pic3, 2, 0, 1, 1, Qt.AlignCenter)
    xxx.setLayout(t0)

    tmp = qtw.QLabel('FOOO')
    stack = [xxx, tmp]

    window = MainWindow(stack)

    app.exec_()
