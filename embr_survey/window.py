from PySide2.QtCore import Qt
import PySide2.QtWidgets as qtw
from embr_survey.next_button import NextButton
from functools import partial
from embr_survey.common_widgets import SpecialStack
import logging

logger = logging.getLogger('embr_survey')


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        logger.warn('Premature escape.')
        qtw.QApplication.instance().quit()


def scroll_up(area, removed):
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


class MainWindow(object):
    def __init__(self, widgets):
        self.win = qtw.QWidget()
        # TODO: add back once other style sheets are resolved
        # (currently makes selected thing in dropdown menu invisible)
        # self.win.setStyleSheet('background-color:#ffffff')
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

        # next button iterates through the stack
        self.widgets = SpecialStack()
        self.next_button = NextButton(self.height, self.widgets)

        self.widgets.widgetRemoved.connect(partial(scroll_up, self.scroll_area))
        # accept single widget or list of widgets (for multi-page experiments)
        # alternatively, we could've detected in the button whether the current
        # widget was a StackedWidget or not
        self.add_widgets(widgets)
        self.widgets.setFixedWidth(1.2*self.height)
        self.scroll_area.setWidget(self.widgets)
        self.widgets.currentWidget().setSizePolicy(qtw.QSizePolicy.Preferred,
                                                   qtw.QSizePolicy.Preferred)
        self.widgets.adjustSize()
        self.main_layout.addWidget(self.next_button, Qt.AlignRight)

        self.win.setLayout(self.main_layout)

    def add_widgets(self, widgets):
        # add (more) widgets from a list of widgets
        for widget in widgets:
            try:
                widget.setSizePolicy(qtw.QSizePolicy.Ignored,
                                     qtw.QSizePolicy.Ignored)
                widget._button = self.next_button
                if isinstance(widget, SpecialStack):
                    widget.widgetRemoved.connect(partial(scroll_up, self.scroll_area))
                self.widgets.addWidget(widget)
            except AttributeError:  # list of widgets (hopefully)
                for w2 in widget:
                    w2.setSizePolicy(qtw.QSizePolicy.Ignored,
                                     qtw.QSizePolicy.Ignored)
                    w2._button = self.next_button
                    if isinstance(w2, SpecialStack):
                        w2.widgetRemoved.connect(partial(scroll_up, self.scroll_area))
                    self.widgets.addWidget(w2)

    def show(self):
        self.win.show()
