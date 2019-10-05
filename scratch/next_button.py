from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from functools import partial

base_style = '''
QPushButton {border:4px solid rgb(0, 0, 0); 
             border-radius:10px;
             font: bold 40px;padding: 24px;}
QPushButton:pressed {border-style:inset;}
'''

no_resp_style = '''
QPushButton {background-color: rgb(255, 140, 0);}
QPushButton:pressed {background-color: rgb(255, 165, 0);}
'''

resp_style = '''
QPushButton {background-color: rgb(0,255,127);}
QPushButton:pressed {background-color: rgb(0,230,134);}
'''

block_style = '''
QPushButton {background-color: rgb(120, 120, 120);font-color:rgb(40,40,40);}
'''


class NextButton(qtw.QWidget):
    def __init__(self, stack):
