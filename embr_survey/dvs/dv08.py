import csv
import logging
import os
import random
from pkg_resources import resource_filename
import itertools

import PyQt5.QtWidgets as qtw
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion, MultiQuestion, SpecialStack
from embr_survey.dvs.base_block import BaseDV


class DV08BrandPersonality(SpecialStack):
    long_name = 'dv08_brand_personality'
    name = 'dv08'
    _log = logging.getLogger('embr_survey')
    auto_continue = True  # control whether button auto-enabled

    def __init__(self, block_num, device, temperature, settings):
        super().__init__()
        self.settings = settings
        self.device = device
        self.block_num = block_num
        self.temperature = temperature
        self._count = 0
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]  # in this next section,...
        prompt2 = translation['prompt2'][lang]  # Please answer the following...

        warm = translation['warm'][lang]
        warm_header = translation['warm_header'][lang]
        friendly = translation['friendly'][lang]
        friendly_header = translation['friendly_header'][lang]

        rest_header = translation['rest_header'][lang]
        intentions = translation['intentions'][lang]
        public_interest = translation['public_interest'][lang]
        rugged = translation['rugged'][lang]
        competence = translation['competence'][lang]
        aggressive = translation['aggressive'][lang]

        # Fixed for now
        brands = ['ADIDAS', 'NIKE', 'REEBOK']
        random.shuffle(brands)

        self.qs = []  # container for button groups
        self.questions = []  # actual question text
        self.brand_col = []  # convenience
        self._prompt = JustText(prompt)
        for brand in brands:
            tw = qtw.QWidget()
            tw.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
            # two sets of single Qs (different header)
            # these won't end up aligning very well
            warm_q = SingleQuestion(warm_header, warm)
            friendly_q = SingleQuestion(friendly_header, friendly)
            # One MultiQuestion (same header)
            multi_q = MultiQuestion(rest_header,
                                    [intentions, public_interest, rugged,
                                     competence, aggressive])

            txt = JustText(prompt2 % brand)  # Please answer the following...
            lt = qtw.QVBoxLayout()
            lt.addWidget(txt)
            lt.addWidget(warm_q)
            lt.addWidget(friendly_q)
            lt.addWidget(multi_q)
            tw.setLayout(lt)
            self.addWidget(tw)
            self.brand_col.extend([brand]*7)
            self.qs.append([warm_q, friendly_q, multi_q])
            self.questions.extend([warm, friendly, intentions, public_interest,
                                   rugged, competence, aggressive])

        desktop = qtw.QDesktopWidget().screenGeometry()
        self.setFixedWidth(1.2*desktop.height())
        self.currentWidget().setSizePolicy(qtw.QSizePolicy.Preferred,
                                           qtw.QSizePolicy.Preferred)
        self.adjustSize()

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for sublist in self.qs for x in sublist]
        current_answers = [x for sublist in current_answers for x in sublist]
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
                'questions': [q[:30] + '...' for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'brands': self.brand_col}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        cw = self.currentIndex()
        res = []
        for question_sec in self.qs[cw]:
            for x in question_sec.get_responses():
                res.append(x >= 0)
        return all(res)

    def on_enter(self):
        self.device.level = self.temperature
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def on_exit(self):
        pass
