# intro screen

# pg 1. big paragraph
# pg 2. Small paragraph
# 3. Currently too cold, hot, ...
# 4. Max heat 10s
# 5. Max cool 10s
# 6. working?
# 7. If not working, please find experimenter
# 8. Embr Wave will continue...

import csv
import logging
import os
import random

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion
from embr_survey.dvs.base_block import StackedDV


class ComfortQuestion(qtw.QWidget):
    def __init__(self, prompt, header, question):
        super().__init__()
        txt = JustText(prompt)
        self.question = SingleQuestion(header, question)
        layout = qtw.QVBoxLayout()
        layout.addWidget(txt)
        layout.addWidget(self.question)
        self.setLayout(layout)

    def get_responses(self):
        return self.question.get_responses()

    def all_ans(self):
        return all([x >= 1 for x in self.get_responses()])


class DV00Intro_1(StackedDV):
    long_name = 'dv00_intro'
    name = 'dv00'

    def __init__(self, device, settings):
        super().__init__(-1, device, 0, settings, None)
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        sec1 = JustText(translation['sec1'][lang])
        sec2 = JustText(translation['sec2'][lang])

        self.q = ComfortQuestion('', translation['q1_header'][lang], translation['q1'][lang])

        self.add_widgets([sec1, sec2, self.q])


class DV00Intro_2(StackedDV):
    long_name = 'dv00_intro'
    name = 'dv00'

    def __init__(self, device, settings):
        super().__init__(-1, device, 0, settings, None)
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        working = JustText(translation['confirm'][lang])
        continuing = JustText(translation['continue'][lang])

        self.add_widgets([working, continuing])
