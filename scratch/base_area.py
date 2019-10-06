from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from next_button import NextButton


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        # TODO log
        qtw.QApplication.instance().quit()


scroll_style = '''
QScrollBar:vertical {
    border: 4px solid grey;
    background: #444444;
    width: 40px;
}
QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-width: 40px;
}
QScrollBar::add-line:vertical {
      border: none;
      background: none;
}

QScrollBar::sub-line:verticall {
      border: none;
      background: none;
}
'''


class MainWindow(object):
    def __init__(self, widgets):
        self.win = qtw.QWidget()
        rect = qtw.QDesktopWidget().screenGeometry()
        self.width, self.height = rect.width(), rect.height()
        self.win.setFixedSize(self.width, self.height)
        self.win.showFullScreen()
        self.win.keyPressEvent = _exit_on_esc

        # overall layout
        self.main_layout = qtw.QVBoxLayout(self.win)
        # scroll region
        self.scroll_area = qtw.QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet(scroll_style)
        self.main_layout.addWidget(self.scroll_area)

        self.widgets = qtw.QStackedWidget()
        for widget in widgets:
            widget.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
            self.widgets.addWidget(widget)
        self.widgets.setCurrentIndex(0)
        self.widgets.setFixedWidth(1.2*self.height)
        # top_layout.addWidget(self.widgets)
        self.scroll_area.setWidget(self.widgets)
        self.widgets.currentWidget().setSizePolicy(qtw.QSizePolicy.Preferred, qtw.QSizePolicy.Preferred)
        self.widgets.adjustSize()

        # next button iterates through the stack
        self.next_button = NextButton(self.height, self.widgets)
        self.main_layout.addWidget(self.next_button, Qt.AlignRight)
        self.win.setLayout(self.main_layout)

    def show(self):
        self.win.show()
