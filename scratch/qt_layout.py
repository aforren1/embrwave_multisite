from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap
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
    stack = qtw.QStackedWidget()
    stack.setFixedSize(1.1 * rect.height(), 0.85*rect.height())
    main_layout.addWidget(stack, 1, 1)

    pic = QPixmap('dv5_1.png')
    pic_inst = qtw.QLabel()
    pic_inst.setAlignment(Qt.AlignCenter)
    pic_inst.setPixmap(pic)
    pic_inst.setStyleSheet('border:2px solid rgb(0, 0, 0);border-radius:20px;')
    stack.addWidget(pic_inst)
    stack.setCurrentIndex(0)

    tmp = qtw.QLabel('FOOO')
    stack.addWidget(tmp)

    # OK button
    ok_button = qtw.QPushButton('Next')
    ok_button.setFixedHeight(0.1*rect.height())
    ok_button.setStyleSheet('''
    QPushButton {border:4px solid rgb(0, 0, 0); border-radius:10px;background-color: rgb(255, 0, 0);font: bold 40px;padding: 24px;}
    QPushButton:pressed { background-color: rgb(255, 128, 128); border-style: inset;}''')
    ok_button.clicked.connect(partial(toggle_stack, stack))
    main_layout.addWidget(ok_button, 2, 1, 1, 1, Qt.AlignRight)

    window.setLayout(main_layout)
    window.show()
    app.exec_()
