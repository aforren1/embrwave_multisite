import csv
import logging
import os
import random
from pkg_resources import resource_filename
import itertools

import PySide2.QtWidgets as qtw
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion, SpecialStack
from embr_survey.dvs.base_block import StackedDV


class PerceptualQuestion(qtw.QWidget):
    def __init__(self, img_name, header, question):
        super().__init__()
        img = QPixmap(img_name)
        img_holder = qtw.QLabel()
        img_holder.setPixmap(img.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_holder.setAlignment(Qt.AlignCenter)
        self.question = SingleQuestion(header, question)
        layout = qtw.QVBoxLayout()
        layout.addWidget(img_holder)
        layout.addWidget(self.question)
        self.setLayout(layout)

    def get_responses(self):
        return self.question.get_responses()

    def all_ans(self):
        return all([x >= 1 for x in self.get_responses()])


class DV07PerceptualFocus(StackedDV):
    long_name = 'dv07_perceptual_focus'
    name = 'dv07'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        # load images
        img_names = ['dv7_%i.png' % i for i in range(1, 8, 1)]
        if lang == 'fr':
            self.img_names = [os.path.join(settings['translation_dir'], 'fr/%s' % x) for x in img_names]
        else: # english
            self.img_names = [resource_filename('embr_survey', 'images/%s' % img) for img in img_names]
        random.shuffle(self.img_names)

        self.prompt = translation['prompt'][lang]
        self.prompt2 = translation['prompt2'][lang]
        header = ['A', 'B']
        question = translation['question'][lang]
        self.qs = []
        self.questions = []
        # GUI stuff
        widgets = []
        widgets.append(JustText(self.prompt))
        for img in self.img_names:
            widgets.append(PerceptualQuestion(img, header, question))
            self.questions.append(question)
            self.qs.append(widgets[-1])  # keep questions in separate list of easy checking

        widgets.insert(2, JustText(self.prompt2))
        self.add_widgets(widgets)

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.qs]
        current_answers = [x for sublist in current_answers for x in sublist]
        current_answers = [ca if ca >= 1 else None for ca in current_answers]
        # Convert from 0/1 to A/B
        for count, ca in enumerate(current_answers):
            if ca is not None:
                current_answers[count] = 'A' if not ca else 'B'

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
                'questions': self.questions,
                # 'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'images': [os.path.basename(i) for i in self.img_names]}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
