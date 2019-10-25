import csv
import logging
import os
import random

from functools import partial
from pkg_resources import resource_filename

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIntValidator
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, EmbrSection, RadioGroupQ
from embr_survey.dvs.base_block import StackedDV
from embr_survey.dvs.base_block import BaseDV
from embr_survey.dvs.dv11 import NameInput


class TextInput(qtw.QWidget):
    def __init__(self, prompt):
        super().__init__()
        prompt = JustText(prompt)
        layout = qtw.QVBoxLayout()
        layout.addWidget(prompt, alignment=Qt.AlignVCenter)
        self.name_input = qtw.QLineEdit()
        self.name_input.setMaximumWidth(800)
        fnt = self.name_input.font()
        fnt.setPointSize(26)
        self.name_input.setFont(fnt)
        layout.addWidget(self.name_input, alignment=Qt.AlignVCenter)
        self.setLayout(layout)

    def get_responses(self):
        return self.name_input.text().strip(' ')

    def all_ans(self):
        name = self.get_responses()
        return name != ''

class Debriefing(StackedDV):
    long_name = 'debriefing'
    name = 'debriefing'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        translation = {k: translation[k][lang] for k in translation.keys()}

        # pg 1
        self.q_purpose = TextInput(translation['q_purpose'])
        # pg 2
        self.q_related = RadioGroupQ(translation['q_related'], translation['q_related_ans'])
        #
        self.q_related_how = TextInput(translation['q_how'])
        # 
        self.q_influence = RadioGroupQ(translation['q_influence'], translation['q_related_ans'])
        # 
        self.q_how_influence = TextInput(translation['q_how_influence'])
        # 
        self.fin = JustText(translation['fin'])
        self.q_data = RadioGroupQ('', translation['q_related_ans'][:2])
        self.fin2 = JustText(translation['fin2'])

        wid = qtw.QWidget()
        lyt = qtw.QVBoxLayout()
        lyt.addWidget(self.fin)
        lyt.addWidget(self.q_data)
        lyt.addWidget(self.fin2)
        wid.setLayout(lyt)

        self.add_widgets([self.q_purpose, self.q_related, self.q_related_how,
                          self.q_influence, self.q_how_influence, wid])
            
        self.qs = [translation[x] for x in ['q_purpose', 'q_related', 'q_how', 'q_influence',
                                            'q_how_influence']]
        self.qs.append('save data?')

    def on_enter(self):
        # need to set each time, at least to keep connection alive
        self.device.level = 0
    
    def on_exit(self):
        self.device.level = 0
    
    def all_ans(self):
        # 
        return True

    def save_data(self):
        # write to csv
        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        ans = [x.get_responses() for x in [self.q_purpose, self.q_related, self.q_related_how,
                                           self.q_influence, self.q_how_influence, self.q_data]]
        lq = len(ans)
        data = {'participant_id': [settings['id']]*lq,
                'datetime_start_exp': [settings['datetime_start']]*lq,
                'datetime_start_block': [now]*lq,
                'datetime_end_block': [self._end_time.strftime('%y%m%d_%H%M%S')]*lq,
                'language': [settings['language']]*lq,
                'locale': [settings['locale']]*lq,
                'questions': self.qs,
                'responses': ans,
                'dv': [self.long_name]*lq,
                'block_number': [self.block_num]*lq,
                'embr_temperature': [0]*lq
                }
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
