import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
import PyQt5.QtWidgets as qtw
from functools import partial

base_style = '''
QPushButton {border:4px solid rgb(0, 0, 0); 
             border-radius:10px;
             font: bold 40px;padding: 24px;}
QPushButton:pressed {border-style:inset;}
'''

incomplete_style = '''
QPushButton {background-color: rgb(255, 140, 0);}
QPushButton:pressed {background-color: rgb(255, 165, 0);}
'''

resp_style = '''
QPushButton {background-color: rgb(0,255,127);}
QPushButton:pressed {background-color: rgb(0,230,134);}
'''

no_style = '''
QPushButton {background-color: rgb(120, 120, 120);color:rgb(40,40,40);}
'''


class NextButton(qtw.QPushButton):
    def __init__(self, height, stack):
        super().__init__('Next')
        self.setFixedHeight(0.1*height)
        self.setStyleSheet(base_style)
        self.stack = stack
        self.clicked.connect(partial(self._callback))
        self.state = 'incomplete'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value
        if value == 'neutral':
            new_sty = no_style
            self.setDisabled(True)
        elif value == 'incomplete':
            new_sty = incomplete_style
            self.setEnabled(True)
        elif value == 'complete':
            new_sty = resp_style
            self.setEnabled(True)
        self.setStyleSheet(base_style + new_sty)

    def _callback(self):
        if self.state == 'neutral':
            return
        if self.state == 'incomplete':
            choice = qtw.QMessageBox.question(None, '',
                                              'Are you sure? You left some blank.',
                                              qtw.QMessageBox.Yes | qtw.QMessageBox.No)
            if choice != qtw.QMessageBox.Yes:
                return
        # all good to keep going, save data (no-op for instructions, but important for surveys)
        current = self.stack.currentWidget()
        # implement a save_data if doing a survey section
        if hasattr(current, 'save_data'):
            current.save_data()
        self.state = 'neutral'
        self._callback_pt2()
        # self.eff = qtw.QGraphicsOpacityEffect()
        # current.setGraphicsEffect(self.eff)
        # a = QPropertyAnimation(self.eff, b'opacity')
        # a.setDuration(500)
        # a.setStartValue(1)
        # a.setEndValue(0)
        # a.setEasingCurve(QEasingCurve.Linear)
        # a.finished.connect(self._callback_pt2)
        # a.start(QPropertyAnimation.DeleteWhenStopped)
        # self.a = a  # keep from GC

    # part 2
    # need to:
    # - pop off previous widget
    # - if we're out of widgets
    # TODO: (non-critical, but nice) reset the scrolling region
    def _callback_pt2(self):
        self.stack.removeWidget(self.stack.currentWidget())
        if self.stack.count() <= 0:
            sys.exit(0)

        # move to the next one
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
        new_widget = self.stack.currentWidget()
        self._callback_pt3()
        # self.eff = qtw.QGraphicsOpacityEffect()
        # new_widget.setGraphicsEffect(self.eff)
        # a = QPropertyAnimation(self.eff, b'opacity')
        # a.setDuration(350)
        # a.setStartValue(0)
        # a.setEndValue(1)
        # a.setEasingCurve(QEasingCurve.OutQuad)
        # a.finished.connect(self._callback_pt3)
        # a.start(QPropertyAnimation.DeleteWhenStopped)
        # self.a = a

    def _callback_pt3(self):
        # re-enable the button on completion
        self.state = 'incomplete'
