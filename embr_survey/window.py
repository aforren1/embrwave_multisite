from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from next_button import NextButton
from functools import partial


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        # TODO log
        qtw.QApplication.instance().quit()


def scroll_up(area):
    area.verticalScrollBar().setValue(0)


scroll_style = '''
QScrollBar:vertical {
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

QScrollBar::sub-line:vertical {
      border: none;
      background: none;
}
'''

# https://stackoverflow.com/questions/23511430/qt-qstackedwidget-resizing-issue


class SpecialStack(qtw.QStackedWidget):
    def sizeHint(self):
        return self.currentWidget().sizeHint()

    def minimumSizeHint(self):
        return self.currentWidget().minimumSizeHint()


class MainWindow(object):
    def __init__(self, widgets):
        self.win = qtw.QWidget()
        self.win.setStyleSheet('background-color:#ffffff')
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

        self.widgets = SpecialStack()
        self.widgets.widgetRemoved.connect(partial(scroll_up, self.scroll_area))
        # accept single widget or list of widgets (for multi-page experiments)
        # alternatively, we could've detected in the button whether the current
        # widget was a StackedWidget or not
        for widget in widgets:
            try:
                widget.setSizePolicy(qtw.QSizePolicy.Ignored,
                                     qtw.QSizePolicy.Ignored)
                self.widgets.addWidget(widget)
            except AttributeError:  # list of widgets (hopefully)
                for w2 in widget:
                    w2.setSizePolicy(qtw.QSizePolicy.Ignored,
                                     qtw.QSizePolicy.Ignored)
                    self.widgets.addWidget(w2)
        self.widgets.setFixedWidth(1.2*self.height)
        self.scroll_area.setWidget(self.widgets)
        self.widgets.currentWidget().setSizePolicy(qtw.QSizePolicy.Preferred,
                                                   qtw.QSizePolicy.Preferred)
        self.widgets.adjustSize()

        # next button iterates through the stack
        self.next_button = NextButton(self.height, self.widgets)
        self.main_layout.addWidget(self.next_button, Qt.AlignRight)
        self.win.setLayout(self.main_layout)

    def show(self):
        self.win.show()
