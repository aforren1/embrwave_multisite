import csv
import logging
import os
import random

from functools import partial
from pkg_resources import resource_filename

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion, EmbrSection
from embr_survey.dvs.base_block import StackedDV
import random


class ConditionalWidget(qtw.QWidget):
    # pair of widgets-- one "main" question, one hidden one
    def __init__(self, main_widget, hidden_widget, callback):
        super().__init__()
        self.main_widget = main_widget
        self.hidden_widget = hidden_widget
        self.hidden_widget.setHidden(True)  # hide until resp


class RadioGroupQ(qtw.QWidget):
    def __init__(self, question, answers):
        super().__init__()
        q_txt = JustText(question)
        self.resp = qtw.QButtonGroup()
        chk_pth = resource_filename('embr_survey', 'images/radio_checked.png')
        unchk_pth = resource_filename('embr_survey', 'images/radio_unchecked.png')
        chk_pth = chk_pth.replace('\\', '/')
        unchk_pth = unchk_pth.replace('\\', '/')
        style = 'QRadioButton::indicator{width:60px; height:60px; image:url(%s);} QRadioButton::indicator::checked{image:url(%s);}' % (unchk_pth, chk_pth)
        layout = qtw.QGridLayout()
        # add question to stretch across top
        layout.addWidget(q_txt, 0, 0, 2, 1, Qt.AlignLeft)
        for count in range(len(answers)):
            rad = qtw.QRadioButton()
            rad.setStyleSheet(style)
            fnt = rad.font()
            fnt.setPointSize(26)
            rad.setFont(fnt)
            self.resp.addButton(rad)
            # add button and text
            layout.addWidget(rad, -1, 0, 1, 1, Qt.AlignCenter)
            layout.addWidget(JustText(answers[count]), -1, 1, 1, 1, Qt.AlignLeft)
        self.setLayout(layout)

# def deal_with_toggle(slf, ):


class IndividualDifferencesPt1(qtw.QWidget):
    # just 1 page
    # these are most of the conditional ones
    def __init__(self, block_num, device, settings):
        super().__init__()
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], 'individual_differences.toml')
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        self.block_num = block_num
        self.settings = settings
        self.device = device  # just to disable it
        layout = qtw.QVBoxLayout()

        layout.addWidget(JustText(translation['instructions'][lang]))
        self.q1 = RadioGroupQ(translation['q1'], translation['q1_ans'])

        self.q2 = RadioGroupQ(translation['q2'], translation['q2_ans'])
        self.q2a = RadioGroupQ(translation['q2a'], translation['q2_ans'])
        # whenever q2 is clicked, check if index is valid; if so, show q2a
        self.q2.resp.buttonClicked.connect(partial(deal_with_toggle))

    def on_enter(self):
        self.device.level = 0
