from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap, QImage
from functools import partial


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        qtw.QApplication.instance().quit()


def toggle_stack(stack):
    choice = qtw.QMessageBox.question(None, '', 'Are you sure? You left some blank.',
                                      qtw.QMessageBox.Yes | qtw.QMessageBox.No)
    if choice == qtw.QMessageBox.Yes:
        stack.setCurrentIndex(not stack.currentIndex())


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
    ok_button = qtw.QPushButton('Next')
    ok_button.setFixedHeight(0.1*rect.height())
    base_style = '''
    QPushButton {border:4px solid rgb(0, 0, 0); 
                border-radius:10px;
                font: bold 40px;padding: 24px;}
    '''

    no_resp_style = '''
QPushButton {background-color: rgb(120,120,120);color:rgb(60,60,60);}
QPushButton:pressed {background-color: rgb(0,255,127);}
'''

    ok_button.setStyleSheet(base_style+no_resp_style)
    ok_button.clicked.connect(partial(toggle_stack, stack))
    main_layout.addWidget(ok_button, 2, 1, 1, 1, Qt.AlignRight)

    window.setLayout(main_layout)
    window.show()
    app.exec_()
