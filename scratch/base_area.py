from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw


class BaseArea(qtw.QGridLayout):
    def __init__(self, height, stack):
        super().__init__()


class ScrollArea:
    def __init__(self, height, widgets):
        super().__init__()
        self.stack = qtw.QStackedWidget()
        for widget in widgets:
            self.stack.addWidget(widget)
        self.stack.setCurrentIndex(0)
