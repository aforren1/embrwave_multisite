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

from embr_survey.common_widgets import JustText, MultiQuestion, SpecialStack


class CriminalQuestion(qtw.QWidget):
    def __init__(self, img_name, questions):
        pass


class DV06CriminalRating(SpecialStack):
    long_name = 'dv06_criminal_rating'
    name = 'dv06'
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

        # load images
        # TODO: shuffle images?
        img_names = ['dv6_%i.png' % i for i in range(1, 9, 1)]
        self.img_names = [resource_filename('embr_survey', 'images/%s' % img) for img in img_names]

        self.prompt = translation['prompt'][lang]
        header = translation['header'][lang]

        self.qs = []
        self.questions = []
        # GUI stuff
        self._prompt = JustText(self.prompt)
        for img in self.img_names:
            tw = qtw.QWidget()  # temporary widget to hold layout
            tw.setSizePolicy(qtw.QSizePolicy.Ignored,
                             qtw.QSizePolicy.Ignored)
            img_holder = qtw.QLabel()
            img = QPixmap(img)
            img_holder.setPixmap(img.scaled(800, 500, Qt.KeepAspectRatio))
            img_holder.setAlignment(Qt.AlignCenter)
            qtext = [q[lang] for q in translation['question']]
            self.questions.extend(qtext)
            qs = MultiQuestion(header, qtext)
            lt = qtw.QVBoxLayout()
            lt.addWidget(img_holder)
            lt.addWidget(qs)
            tw.setLayout(lt)
            self.addWidget(tw)
            self.qs.append(qs)

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
        rep_img_names = list(itertools.chain.from_iterable(itertools.repeat(os.path.basename(x), 2) for x in self.img_names))
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': [q[:30] + '...' for q in self.questions],
                # 'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'images': rep_img_names}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
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
