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
from embr_survey.dvs.base_block import StackedDV
from embr_survey.common_widgets import JustText, MultiQuestion


class CriminalQuestion(qtw.QWidget):
    def __init__(self, img_name, header, questions):
        super().__init__()
        img = QPixmap(img_name)
        img_holder = qtw.QLabel()
        img_holder.setPixmap(img.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_holder.setAlignment(Qt.AlignCenter)
        self.question = MultiQuestion(header, questions)
        layout = qtw.QVBoxLayout()
        layout.addWidget(img_holder)
        layout.addWidget(self.question)
        self.setLayout(layout)

    def get_responses(self):
        return self.question.get_responses()

    def all_ans(self):
        return all([x >= 1 for x in self.get_responses()])


class DV06CriminalRating(StackedDV):
    long_name = 'dv06_criminal_rating'
    name = 'dv06'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        # load images
        # TODO: shuffle images?
        img_names = ['dv6_%i.png' % i for i in range(1, 9, 1)]
        self.img_names = [resource_filename('embr_survey', 'images/%s' % img) for img in img_names]

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]
        qtext = [q[lang] for q in translation['question']]

        widgets = []
        widgets.append(JustText(prompt))
        self.questions = []
        for img in self.img_names:
            self.questions.extend(qtext)
            widgets.append(CriminalQuestion(img, header, qtext))
        self.add_widgets(widgets)  # add_widgets also adds to internal list `self.widgets`

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets[1:]]
        current_answers = [x for sublist in current_answers for x in sublist]
        current_answers = [ca if ca >= 1 else None for ca in current_answers]

        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(self.questions)
        rep_img_names = list(itertools.chain.from_iterable(itertools.repeat(os.path.basename(x), 2) for x in self.img_names))
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': ['...' + q[-40:] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'images': rep_img_names}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
