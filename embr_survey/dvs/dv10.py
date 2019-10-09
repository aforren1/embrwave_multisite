import csv
import os
import random
from datetime import datetime
from pkg_resources import resource_filename

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt
from pip._vendor import pytoml as toml
from embr_survey.common_widgets import JustText, SingleQuestion
from embr_survey.dvs.base_block import BaseDV


class DV10WillingnessToForgive(BaseDV):
    name = 'dv10'
    long_name = 'dv10_willingnesstoforgive'

    def __init__(self, block_num, device, temperature, settings):
        super().__init__(block_num, device, temperature, settings)
        lang = settings['language']

        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        self.question = translation['question'][lang]
        header = translation['header'][lang]

        layout = qtw.QVBoxLayout()
        layout.addWidget(JustText(prompt))

        self.qs = SingleQuestion(header, self.question)
        layout.addWidget(self.qs)

        self.setLayout(layout)

    def save_data(self):
        current_answers = self.qs.get_responses()
        current_answers = [ca if ca >= 0 else None for ca in current_answers]
        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        data = {'participant_id': [settings['id']],
                'datetime_start_exp': [settings['datetime_start']],
                'datetime_start_block': [now],
                'datetime_end_block': [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': [settings['language']],
                'locale': [settings['locale']],
                'questions': [self.question[:30]],
                'responses': current_answers,
                'dv': [self.name],
                'block_number': [self.block_num],
                'embr_temperature': [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        ff = [x >= 0 for x in self.qs.get_responses()]
        return all(ff)
