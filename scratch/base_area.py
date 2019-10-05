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
        self.scrollarea = qtw.QScrollArea()
        self.scrollarea.setWidgetResizable(False)
        self.scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)  # TODO: check
        self.scrollarea.setFixedSize(1.1 * rect.height(), 0.85*rect.height())
        widget = qtw.QWidget()
        self.scrollarea.setWidget(widget)
        self.main_layout.addWidget(widget, 1, 1, 1, 1, Qt.AlignCenter)

        # handle stack of widgets
        self.widgets = qtw.QStackedWidget()
        for widget in widgets:
            self.widgets.addWidget(widget)

        # next button iterates through the stack
        self.next_button = NextButton(self.height, self.widgets)
        self.main_layout.addWidget(self.next_button, 2, 1, 1, 1, Qt.AlignRight)
