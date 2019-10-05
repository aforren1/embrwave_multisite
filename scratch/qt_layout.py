from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap, QImage
from functools import partial
from next_button import NextButton


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        qtw.QApplication.instance().quit()


if __name__ == '__main__':
    # main window (fullscreen)
    app = qtw.QApplication([])

    window = qtw.QWidget()
    rect = qtw.QDesktopWidget().screenGeometry()
    window.setFixedSize(rect.width(), rect.height())
    window.showFullScreen()
    window.keyPressEvent = _exit_on_esc

    # primary layout
    # should be a 3x3 grid--
    # top row should be ~5% tall?
    # middle (potential scroll) region should be centered;
    #  ~85% (width ~1.1*total height)
    # bottom ~10% reserved for buttons
    main_layout = qtw.QGridLayout()

    # stack
    scroll = qtw.QScrollArea()
    scroll.setWidgetResizable(False)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setFixedSize(1.1 * rect.height(), 0.85*rect.height())
    scroll_wid = qtw.QWidget()
    scroll.setWidget(scroll_wid)
    scroll_area = qtw.QVBoxLayout(scroll_wid)
    scroll_area.addStretch(1)

    stack = qtw.QStackedWidget()
    scroll_area.addWidget(stack, Qt.AlignCenter)
    scroll_area.addStretch(1)

    #stack.setFixedSize(1.05 * rect.height(), 0.8*rect.height())
    main_layout.addWidget(scroll_wid, 1, 1, 1, 1, Qt.AlignCenter)

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
    t0 = qtw.QVBoxLayout()
    t0.addWidget(pic_inst)
    t0.addWidget(pic2)
    t0.addWidget(pic3)
    t0.addStretch(1)
    xxx.setLayout(t0)
    stack.addWidget(xxx)
    stack.setCurrentIndex(0)

    tmp = qtw.QLabel('FOOO')
    stack.addWidget(tmp)

    # OK button
    ok_button = NextButton(rect.height(), stack)
    ok_button.state = 'incomplete'
    main_layout.addWidget(ok_button, 2, 1, 1, 1, Qt.AlignRight)

    window.setLayout(main_layout)
    window.show()
    app.exec_()
