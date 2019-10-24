import csv
import logging
import os
import random

from functools import partial
from pkg_resources import resource_filename

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIntValidator
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, MultiQuestion, EmbrSection, RadioGroupQ, DropDownQuestion
from embr_survey.dvs.base_block import StackedDV
from embr_survey.dvs.base_block import BaseDV


class ConditionalWidget(qtw.QWidget):
    # pair of widgets-- one "main" question, one hidden one
    # first one is always a QButtonGroup
    def __init__(self, main_widget, hidden_widget, valid):
        super().__init__()
        self.main_widget = main_widget
        self.valid = valid
        main_widget.resp.buttonClicked.connect(self.check_valid)
        self.hidden_widget = hidden_widget
        self.hidden_widget.setHidden(True)  # hide until resp
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.main_widget)
        layout.addWidget(self.hidden_widget)
        self.setLayout(layout)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
    
    def check_valid(self):
        val = self.main_widget.resp.checkedButton().text()
        if val in self.valid:
            self.hidden_widget.setHidden(False)
        else:
            self.hidden_widget.setHidden(True)
        self.parentWidget().parentWidget().adjustSize()
    
    # if not in valid range, return initial answer & None (always tuple)
    def get_responses(self):
        r1 = self.main_widget.get_responses()
        val = self.main_widget.resp.checkedButton().text()
        r2 = None
        if val in self.valid:
            r2 = self.hidden_widget.get_responses()
        return r1, r2

class ConditionalWidget2(qtw.QWidget):
    # pair of widgets-- one "main" question, one hidden one
    # first one is always a QButtonGroup
    def __init__(self, main_widget, hidden_widget1, hidden_widget2, valid):
        super().__init__()
        self.main_widget = main_widget
        self.valid = valid
        main_widget.resp.buttonClicked.connect(self.check_valid)
        self.hidden_widget1 = hidden_widget1
        self.hidden_widget1.setHidden(True)  # hide until resp
        self.hidden_widget2 = hidden_widget2
        self.hidden_widget2.setHidden(True)  # hide until resp
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.main_widget)
        layout.addWidget(self.hidden_widget1)
        layout.addWidget(self.hidden_widget2)
        self.setLayout(layout)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
    
    def check_valid(self):
        val = self.main_widget.resp.checkedButton().text()
        if val in self.valid:
            self.hidden_widget1.setHidden(False)
            self.hidden_widget2.setHidden(False)
        else:
            self.hidden_widget1.setHidden(True)
            self.hidden_widget2.setHidden(True)
        self.parentWidget().parentWidget().adjustSize()
    
    # if not in valid range, return initial answer & None (always tuple)
    def get_responses(self):
        r1 = self.main_widget.get_responses()
        val = self.main_widget.resp.checkedButton().text()
        r2 = None
        r3 = None
        if val in self.valid:
            r2 = self.hidden_widget1.get_responses()
            r3 = self.hidden_widget2.get_response()
        return r1, r2, r3

class Question12(qtw.QWidget):
    def __init__(self, prompt, headers, n_elements=6):
        super().__init__()
        layout2 = qtw.QVBoxLayout()
        
        grid_wid = qtw.QWidget()
        layout = qtw.QGridLayout()
        layout.addWidget(JustText(headers[0]), 0, 0, Qt.AlignCenter)
        layout.addWidget(JustText(headers[1]), 0, 1, Qt.AlignCenter)
        validator = QIntValidator(1, 1000)
        self.groups = []
        self.nums = []
        for i in range(n_elements):
            group_name = qtw.QLineEdit()
            group_name.setMaximumWidth(200)
            fnt = group_name.font()
            fnt.setPointSize(26)
            group_name.setFont(fnt)
            num_people = qtw.QLineEdit()
            num_people.setMaximumWidth(200)
            num_people.setFont(fnt)
            num_people.setValidator(validator)
            self.groups.append(group_name)
            self.nums.append(num_people)
            layout.addWidget(group_name, i + 1, 0, Qt.AlignCenter)
            layout.addWidget(num_people, i + 1, 1, Qt.AlignCenter)
        
        grid_wid.setLayout(layout)
        layout2.addWidget(JustText(prompt))
        layout2.addWidget(grid_wid)
        self.setLayout(layout2)
    
    def get_responses(self):
        return [(x.text(), y.text()) for x, y in zip(self.groups, self.nums)]



class IndividualDifferencesPart1(qtw.QWidget):
    # just 1 page
    # these are most of the conditional ones
    def __init__(self, block_num, device, settings):
        super().__init__()
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], 'individual_differences.toml')
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        # separate out the translation we care about
        translation = {k: translation[k][lang] for k in translation.keys()}
        self.block_num = block_num
        self.settings = settings
        self.device = device  # just to disable it
        layout = qtw.QVBoxLayout()

        layout.addWidget(JustText(translation['instructions'])) # this questionnaire...

        self.q1 = RadioGroupQ(translation['q1'], translation['q1_ans']) # marital
        self.q2 = RadioGroupQ(translation['q2'], translation['q2_ans']) # children
        self.q2a = RadioGroupQ(translation['q2a'], translation['q2_ans']) # talk to them
        # whenever q2 is clicked, check if index is valid; if so, show q2a
        self.q2grp = ConditionalWidget(self.q2, self.q2a, translation['q2_ans'][1:])
        self.q3 = RadioGroupQ(translation['q3'], translation['q3_ans'])
        self.q3a = RadioGroupQ(translation['q3a'], translation['q3_ans'])
        self.q3grp = ConditionalWidget(self.q3, self.q3a, translation['q3_ans'][1:])
        self.q4 = RadioGroupQ(translation['q4'], translation['q4_ans'])
        self.q4a = RadioGroupQ(translation['q4a'], translation['q3_ans'])
        self.q4grp = ConditionalWidget(self.q4, self.q4a, translation['q4_ans'][1:-1])
        self.q5 = RadioGroupQ(translation['q5'], translation['q2_ans'])
        self.q5a = RadioGroupQ(translation['q5a'], translation['q2_ans'])
        self.q5grp = ConditionalWidget(self.q5, self.q5a, translation['q2_ans'][1:])
        self.q6 = RadioGroupQ(translation['q6'], translation['q2_ans'])
        self.q6a = RadioGroupQ(translation['q6a'], translation['q2_ans'])
        self.q6grp = ConditionalWidget(self.q6, self.q6a, translation['q2_ans'][1:])
        self.q7 = RadioGroupQ(translation['q7'], translation['q7_ans'])
        self.q7a = RadioGroupQ(translation['q7a'], translation['q2_ans'])
        self.q7grp = ConditionalWidget(self.q7, self.q7a, translation['q7_ans'][1])
        self.q8 = RadioGroupQ(translation['q8'], translation['q7_ans'])
        self.q8a = RadioGroupQ(translation['q8a'], translation['q2_ans'])
        self.q8grp = ConditionalWidget(self.q8, self.q8a, translation['q7_ans'][1])

        # q9 is special (*two* optional responses)
        self.q9 = RadioGroupQ(translation['q9'], translation['q9_ans'])
        self.q9a = RadioGroupQ(translation['q9a'], translation['q2_ans'])
        self.q9b = RadioGroupQ(translation['q9b'], translation['q2_ans'])
        self.q9grp = ConditionalWidget2(self.q9, self.q9a, self.q9b, translation['q2_ans'][1:])

        self.q10 = RadioGroupQ(translation['q10'], translation['q2_ans'])

        self.q11 = RadioGroupQ(translation['q11'], translation['q7_ans'])
        self.q11a = RadioGroupQ(translation['q11a'], translation['q2_ans'])
        self.q11grp = ConditionalWidget(self.q11, self.q11a, translation['q7_ans'][1])

        self.q12 = RadioGroupQ(translation['q12'], translation['q7_ans'])
        self.q12a = Question12(translation['q12a'], translation['q12a_header'], 6)
        self.q12grp = ConditionalWidget(self.q12, self.q12a, translation['q7_ans'][1])

        layout.addWidget(self.q1)
        layout.addWidget(self.q2grp)
        layout.addWidget(self.q3grp)
        layout.addWidget(self.q4grp)
        layout.addWidget(self.q5grp)
        layout.addWidget(self.q6grp)
        layout.addWidget(self.q7grp)
        layout.addWidget(self.q8grp)
        layout.addWidget(self.q9grp)
        layout.addWidget(self.q10)
        layout.addWidget(self.q11grp)
        layout.addWidget(self.q12grp)
        self.setLayout(layout)

    def on_enter(self):
        # need to set each time, at least to keep connection alive
        self.device.level = 0
    
    def on_exit(self):
        self.device.level = 0
    
    def all_ans(self):
        # 
        pass

    def save_data(self):
        # write to csv
        pass


class IndividualDifferencesPart2(BaseDV):
    long_name = 'individual_differences_relationships'
    name = 'ind_diff_rel'

    def __init__(self, block_num, device, temperature, settings):
        super().__init__(block_num, device, temperature, settings)
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], 'individual_differences.toml')
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        prompt = translation['intimate_prompt'][lang]
        header = translation['intimate_header'][lang]
        self.questions = [('q%i' % i, q) for i, q in enumerate(translation['relationship_qs'][lang])]
        random.shuffle(self.questions)

        layout = qtw.QVBoxLayout()
        self.qs = MultiQuestion(header, [q[1] for q in self.questions])
        head = qtw.QLabel(prompt)
        head.setStyleSheet('font-size:26pt;')
        head.setWordWrap(True)
        layout.addWidget(head)
        layout.addWidget(self.qs)
        self.setLayout(layout)

    def save_data(self):
        current_answers = self.qs.get_responses()
        current_answers = [ca if ca >= 1 else None for ca in current_answers]
        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(self.questions)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': [q[1][:40] + '...' for q in self.questions],
                'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        return all([x >= 1 for x in self.qs.get_responses()])
