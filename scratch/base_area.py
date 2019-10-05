from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from next_button import NextButton


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        # TODO log
        qtw.QApplication.instance().quit()


class MainWindow(object):
    def __init__(self, widgets):
        self.win = qtw.QWidget()
        rect = qtw.QDesktopWidget().screenGeometry()
        self.width, self.height = rect.width(), rect.height()
        self.win.setFixedSize(self.width, self.height)
        self.win.showFullScreen()
        self.win.keyPressEvent = _exit_on_esc

        self.main_layout = qtw.QGridLayout()
        self.win.setLayout(self.main_layout)

        # main scroll area

        # handle stack of widgets
        self.widgets = qtw.QStackedWidget()
        for widget in widgets:
            self.widgets.addWidget(widget)

        # next button iterates through the stack
        self.next_button = NextButton(self.height, self.widgets)
        self.main_layout.addWidget(self.next_button, 2, 1, 1, 1, Qt.AlignRight)
