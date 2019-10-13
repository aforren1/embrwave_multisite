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
        super().__init__()
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
        layout = qtw.QVBoxLayout()
        layout.addWidget(JustText(movie_info))
        layout.addWidget(self.question1)
        layout.addWidget(self.question2)
        layout.addWidget(self.question3)
        self.setLayout(layout)

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


class DV14RomanceMovies(StackedDV):
    long_name = 'dv14_romance_movies'
    name = 'dv14'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header1 = translation['header1'][lang]
        header2 = translation['header2'][lang]
        q1 = translation['question1'][lang]
        q2 = translation['question2'][lang]
        q3 = translation['question3'][lang]

        # excludes the default (none) response
        answers = [t[lang] for t in translation['ans']]
        answers.insert(0, '')

        movie_txt = [m[lang] for m in translation['movie']]

        widgets = []
        self.qs = []
        widgets.append(JustText(prompt))
        for mov in movie_txt:
            self.qs.extend([q1, q2, q3])
            widgets.append(MovieQuestion([header1, header2],
                                         [q1, q2, q3],
                                         answers,
                                         mov))
        self.add_widgets(widgets)

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets[1:]]
        current_answers = [x for sublist in current_answers for x in sublist]
        for count, ca in enumerate(current_answers):
            if isinstance(ca, list):
                current_answers[count] = ca[0] if ca[0] >= 0 else None

        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(self.qs)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': [q[:30] + '...' for q in self.qs],
                # 'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
