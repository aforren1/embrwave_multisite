# NOTE: device only active for name-picking, not second part

import PySide2.QtWidgets as qtw
from embr_survey import app_path
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from embr_survey.common_widgets import JustText, MultiQuestion, SpecialStack

# part1, part2 share data


class NameInput(qtw.QWidget):
    def __init__(self, prompt):
        prompt = JustText(prompt)
        layout = qtw.QHBoxLayout()
        layout.addWidget(prompt, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.name_input = qtw.QLineEdit(self.name)
        layout.addWidget(self.name_input, alignment=Qt.AlignLeft | Qt.AlignVCenter)


class RelationshipQuestions(qtw.QWidget):
    def __init__(self, question_txt, image_path):
        # layout =
        pass


class DV11ThinkingAboutLovedOnes(SpecialStack):

    def all_ans(self):
        low_txt = self.name_input.text.lower()
        return low_txt != '' and low_txt not in self.prev_answers
