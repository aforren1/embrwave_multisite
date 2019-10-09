import csv
import logging
import os
import random

import PySide2.QtWidgets as qtw
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion, SpecialStack
from embr_survey.dvs.base_block import BaseDV


class DV03Utilitarian(SpecialStack):
    long_name = 'dv03_utilitarian'
    name = 'dv03'
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

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]

        # questions
        self.questions = [('q%i' % i, pr[lang], q[lang]) for i, (pr, q) in enumerate(zip(translation['subprompt'], translation['question']))]

        # new ordering
        random.shuffle(self.questions)

        self.qs = []
        self._prompt = JustText(prompt)

        # self.addWidget(txt)
        for question in self.questions:
            tw = qtw.QWidget()  # temporary widget to hold layout
            tw.setSizePolicy(qtw.QSizePolicy.Ignored,
                             qtw.QSizePolicy.Ignored)
            jt = JustText(question[1])
            qs = SingleQuestion(header, question[2])
            lt = qtw.QVBoxLayout()
            lt.addWidget(jt)
            lt.addWidget(qs)
            tw.setLayout(lt)
            self.addWidget(tw)
            self.qs.append(qs)  # keep questions around in case of GC?

        desktop = qtw.QDesktopWidget().screenGeometry()
        self.setFixedWidth(1.2*desktop.height())
        self.currentWidget().setSizePolicy(qtw.QSizePolicy.Preferred,
                                           qtw.QSizePolicy.Preferred)
        self.adjustSize()

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.qs]
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
        cw = self.currentIndex()
        return all([x >= 0 for x in self.qs[cw].get_responses()])

    def on_enter(self):
        self.device.level = self.temperature
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def on_exit(self):
        pass
