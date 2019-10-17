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

from embr_survey.common_widgets import JustText, SingleQuestion, MultiQuestion
from embr_survey.dvs.base_block import StackedDV


class ThatsMyBrand(qtw.QWidget):
    def __init__(self, brand, subprompt, warm, friendly, rest_header, rest_qs):
        super().__init__()
        self.warm_q = SingleQuestion(*warm)
        self.friendly_q = SingleQuestion(*friendly)
        # One MultiQuestion (same header)
        self.multi_q = MultiQuestion(rest_header, rest_qs)

        txt = JustText(subprompt % brand)  # Please answer the following...
        lt = qtw.QVBoxLayout()
        lt.addWidget(txt)
        lt.addWidget(self.warm_q)
        lt.addWidget(self.friendly_q)
        lt.addWidget(self.multi_q)
        self.setLayout(lt)

    def get_responses(self):
        return [self.warm_q.get_responses(),
                self.friendly_q.get_responses(),
                self.multi_q.get_responses()]

    def all_ans(self):
        resps = self.get_responses()
        return all([x >= 1 for sublist in resps for x in sublist])


class DV08BrandPersonality(StackedDV):
    long_name = 'dv08_brand_personality'
    name = 'dv08'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]  # in this next section,...
        prompt2 = translation['prompt2'][lang]  # Please answer the following...

        warm = [translation['warm_header'][lang], translation['warm'][lang]]
        friendly = [translation['friendly_header'][lang], translation['friendly'][lang]]

        rest_header = translation['rest_header'][lang]
        rest_qs = [translation[x][lang] for x in ['intentions', 'public_interest', 'rugged', 'competence', 'aggressive']]

        # Fixed for now
        brands = ['ADIDAS', 'NIKE', 'REEBOK']
        random.shuffle(brands)

        self.questions = []  # actual question text
        self.brand_col = []  # convenience
        widgets = []
        widgets.append(JustText(prompt))
        for brand in brands:
            widgets.append(ThatsMyBrand(brand, prompt2, warm,
                                        friendly, rest_header, rest_qs))
            # two sets of single Qs (different header)
            # these won't end up aligning very well
            self.brand_col.extend([brand]*7)
            self.questions.extend([warm[1], friendly[1]])
            self.questions.extend(rest_qs)

        self.add_widgets(widgets)

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets[1:]]
        current_answers = [x for sublist in current_answers for x in sublist]
        res = []
        for sublist in current_answers:
            for subval in sublist:
                if subval >= 1:
                    res.append(subval)
                else:
                    res.append(None)
        current_answers = res

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
                'questions': [q[:40] + '...' for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'brands': self.brand_col}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
