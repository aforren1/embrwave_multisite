from PyQt5.QtCore import Qt
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
        self.state = 'neutral'
        self.setFixedHeight(0.1*height)
        self.setStyleSheet(base_style)
        self.stack = stack
        self.clicked.connect(partial(self._callback))

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
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
