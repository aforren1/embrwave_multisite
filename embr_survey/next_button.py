import sys
from time import sleep
from PyQt5.QtCore import Qt, QTimer
import PyQt5.QtWidgets as qtw
from functools import partial
from datetime import datetime

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
        self.clicked.connect(self._callback)
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
        # divided into three parts for potential animations between
        # sections-- however, the attempt (9496818f6a9b7ae3694a7f77faa354d96351a53a)
        # seemed to lead to "smearing" artifacts on subsequent widgets...
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
        current._end_time = datetime.now()
        # implement a save_data if doing a survey section
        if hasattr(current, 'save_data'):
            current.save_data()
        self.state = 'neutral'
        self._callback_pt2()

    # part 2
    # need to:
    # - pop off previous widget
    # - if we're out of widgets, exit
    def _callback_pt2(self):
        current_widget = self.stack.currentWidget()
        # TODO: handle StackedWidgets properly? Would allow for more
        # natural data movement...
        passed_data = getattr(current_widget, 'passed_data', None)
        current_widget.setSizePolicy(qtw.QSizePolicy.Ignored,
                                     qtw.QSizePolicy.Ignored)
        self.stack.adjustSize()
        self.stack.removeWidget(self.stack.currentWidget())
        if self.stack.count() <= 0:
            sys.exit(0)

        # move to the next one
        new_widget = self.stack.currentWidget()
        new_widget._start_time = datetime.now()
        if passed_data is not None:
            new_widget.passed_data = passed_data
        new_widget.setSizePolicy(qtw.QSizePolicy.Preferred,
                                 qtw.QSizePolicy.Preferred)
        self.stack.adjustSize()
        QTimer.singleShot(1000, self._callback_pt3)

    def _callback_pt3(self):
        # re-enable the button on completion
        self.state = 'incomplete'
