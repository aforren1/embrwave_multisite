import csv
import os
import random
from datetime import datetime
from pkg_resources import resource_filename

import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from pip._vendor import pytoml as toml
from embr_survey.common_widgets import JustText, MultiQuestion
from embr_survey.dvs.base_block import BaseDV


class DV05HousesHomelikeness(BaseDV):
    name = 'dv05'
    long_name = 'dv05_houses_homelikeness'

    def __init__(self, block_num, device, temperature, settings):
        super().__init__(block_num, device, temperature, settings)

        lang = settings['language']
        locale = settings['locale']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        locale_path = os.path.join(settings['locale_dir'], '%s.toml' % self.name)

        with open(locale_path, 'r') as f:
            locale_settings = toml.load(f)

        # read in all images
        images = locale_settings['house_photos'][locale]
        images = [resource_filename('embr_survey', 'images/%s' % img) for img in images]

        # read in translations, also plugging in locale-specific info
        self.prompt = translation['prompt'][lang]
        self.preprompt = translation['preprompt'][lang]
        self.big_title = translation['big_title'][lang]

        self.background = translation['background'][lang] % locale_settings['house_cost'][locale]
        self.subtitle = translation['subtitle'][lang]

        self.floor1 = translation['f1'][lang]
        self.floor2 = translation['f2'][lang] % locale_settings['floor_label'][locale][0]
        self.floor3 = translation['f3'][lang] % locale_settings['floor_label'][locale][1]

        prompt2 = translation['prompt2'][lang]
        header = translation['header'][lang]

        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]
        random.shuffle(self.questions)

        # now set up gui
        self.images = {os.path.basename(n): QPixmap(n) for n in images}
        for img in self.images:
            ql = qtw.QLabel()
            ql.setPixmap(self.images[img].scaled(800, 500, Qt.KeepAspectRatio))
            # ql.setScaledContents(True)

            self.images[img] = ql

        layout = qtw.QVBoxLayout()

        layout.addWidget(JustText(self.preprompt))  # what do you think..
        layout.addWidget(self.images['dv5_1.png'])
        layout.addWidget(JustText('<b>%s</b>' % self.big_title))
        layout.addWidget(JustText(self.background))  # General info...
        layout.addWidget(JustText(self.subtitle))  # the resale value...
        layout.addWidget(JustText(self.floor1))
        layout.addWidget(JustText(self.floor2))
        layout.addWidget(JustText(self.floor3))
        layout.addWidget(self.images['dv5_2.png'])
        layout.addWidget(self.images['dv5_3.png'])
        layout.addWidget(self.images['dv5_4.png'])
        layout.addWidget(self.images['dv5_5.png'])
        layout.addWidget(self.images['dv5_6.png'])
        layout.addWidget(self.images['dv5_7.png'])
        layout.addWidget(self.images['dv5_8.png'])
        layout.addWidget(self.images['dv5_9.png'])
        layout.addWidget(self.images['dv5_10.png'])

        self.qs = MultiQuestion(header, [q[1] for q in self.questions])
        layout.addWidget(self.qs)
        self.setLayout(layout)

    # copied from base
    def save_data(self):
        current_answers = self.qs.get_responses()
        current_answers = [ca if ca >= 0 else None for ca in current_answers]
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
                'questions': [q[1][:30] + '...' for q in self.questions],
                'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        return all([x >= 0 for x in self.qs.get_responses()])
