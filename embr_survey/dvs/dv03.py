import csv
import logging
import os
import random

import PySide2.QtWidgets as qtw
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion
from embr_survey.dvs.base_block import StackedDV


class UtilitarianQuestion(qtw.QWidget):
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


class DV03Utilitarian(StackedDV):
    long_name = 'dv03_utilitarian'
    name = 'dv03'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]

        # questions
        self.questions = [('q%i' % i, pr[lang], q[lang]) for i, (pr, q) in enumerate(zip(translation['subprompt'], translation['question']))]

        # new ordering
        random.shuffle(self.questions)

        prompt = JustText(prompt)
        widgets = []
        widgets.append(prompt)
        for question in self.questions:
            widgets.append(UtilitarianQuestion(question[1], header, question[2]))
        self.add_widgets(widgets)

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets[1:]]
        current_answers = [x for sublist in current_answers for x in sublist]
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
