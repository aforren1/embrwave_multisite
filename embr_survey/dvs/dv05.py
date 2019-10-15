import csv
import os
import random
from datetime import datetime
from pkg_resources import resource_filename

import PySide2.QtWidgets as qtw
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt
from pip._vendor import pytoml as toml
from embr_survey.common_widgets import JustText, MultiQuestion
from embr_survey.dvs.base_block import BaseDV
from embr_survey import application_path


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
        try:
            images = locale_settings['house_photos'][locale]
        except KeyError:
            # use default locale (US)
            images = locale_settings['house_photos']['us']
        # now handle localized image location
        for count, img in enumerate(images):
            # if locale has path specified, look relative to exe location
            if os.path.split(img)[0] != '':
                # TODO: verify this is the right pattern
                images[count] = os.path.join(application_path, img)
            else:
                # no path for locale, assume it's one of the baked-in ones
                images[count] = resource_filename('embr_survey', 'images/%s' % img)

        # read in translations, also plugging in locale-specific info
        self.prompt = translation['prompt'][lang]
        self.preprompt = translation['preprompt'][lang]
        self.big_title = translation['big_title'][lang]

        try:
            cost = locale_settings['house_cost'][locale]
        except KeyError:
            cost = locale_settings['house_cost']['us']
        self.background = translation['background'][lang] % cost
        self.subtitle = translation['subtitle'][lang]

        self.floor1 = translation['f1'][lang]
        try:
            floor_label = locale_settings['floor_label'][locale]
        except KeyError:
            floor_label = locale_settings['floor_label']['us']
        self.floor2 = translation['f2'][lang] % floor_label[0]
        self.floor3 = translation['f3'][lang] % floor_label[1]

        prompt2 = translation['prompt2'][lang]
        header = translation['header'][lang]

        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]
        random.shuffle(self.questions)

        # now set up gui
        self.images = {os.path.basename(n): QPixmap(n) for n in images}
        for img in self.images:
            ql = qtw.QLabel()
            ql.setPixmap(self.images[img].scaled(800, 500, Qt.KeepAspectRatio))
            self.images[img] = ql

        layout = qtw.QVBoxLayout()
        layout.addWidget(JustText(self.prompt))  # next, we are going to present...
        layout.addWidget(JustText(self.preprompt))  # what do you think..
        layout.addWidget(self.images['dv5_1.png'], alignment=Qt.AlignCenter)  # initial image
        layout.addWidget(JustText('<b>%s</b>' % self.big_title))  # general info
        layout.addWidget(JustText(self.background))  # General info...
        layout.addWidget(JustText(self.subtitle))  # the resale value...
        layout.addWidget(JustText(self.floor1))
        layout.addWidget(JustText(self.floor2))
        layout.addWidget(JustText(self.floor3))
        layout.addWidget(self.images['dv5_2.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_3.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_4.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_5.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_6.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_7.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_8.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_9.png'], alignment=Qt.AlignCenter)
        layout.addWidget(self.images['dv5_10.png'], alignment=Qt.AlignCenter)
        layout.addWidget(JustText(prompt2))

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
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        return all([x >= 0 for x in self.qs.get_responses()])
