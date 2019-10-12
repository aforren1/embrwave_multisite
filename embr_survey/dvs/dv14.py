import csv
import logging
import os
import random
from pkg_resources import resource_filename
import itertools

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt

from pip._vendor import pytoml as toml
from embr_survey.dvs.base_block import StackedDV
from embr_survey.common_widgets import JustText, SingleQuestion
# similar to DV06


class DropDownQuestion(qtw.QWidget):
    def __init__(self, question, answers):
        layout = qtw.QHBoxLayout()
        q = JustText(question)
        self.answer = qtw.QComboBox()
        self.answer.addItems(answers)
        self._default_ans = answers[0]
        layout.addWidget(q, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.answer, Qt.AlignLeft | Qt.AlignCenter)
        self.setLayout(layout)

    def get_responses(self):
        return self.answer.currentText()


class MovieQuestion(qtw.QWidget):
    def __init__(self, headers, questions, q3_ans, movie_info):
        super().__init__()
        self.question1 = SingleQuestion(headers[0], questions[0])
        self.question2 = SingleQuestion(headers[1], questions[1])
        self.question3 = DropDownQuestion(questions[2], q3_ans)

    def get_responses(self):
        return [self.question1.get_responses(),
                self.question2.get_responses(),
                self.question3.get_responses()]

    def all_ans(self):
        if (all(x >= 0 for x in self.question1.get_responses()) and
                all(x >= 0 for x in self.question2.get_responses()) and
                self.question3.get_responses() != self.question3._default_ans):
            return True
        return False
