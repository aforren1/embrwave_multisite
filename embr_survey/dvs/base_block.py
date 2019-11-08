import csv
import os
import random
import logging

import PySide2.QtWidgets as qtw
from pip._vendor import pytoml as toml
from PySide2.QtCore import Qt
from embr_survey.common_widgets import MultiQuestion, SpecialStack
from embr_survey.next_button import NextButton


class BaseDV(qtw.QWidget):
    _log = logging.getLogger('embr_survey')
    auto_continue = True  # control whether button auto-enabled

    def __init__(self, block_num, device, temperature, settings):
        super().__init__()
        self.settings = settings
        self.device = device
        self.block_num = block_num
        self.temperature = temperature

    def save_data(self):
        pass

    def all_ans(self):
        # check if all answered (used by next_button)
        pass

    def on_enter(self):
        self.device.level = self.temperature
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def on_exit(self):
        pass


class StackedDV(SpecialStack):
    long_name = 'long_name'
    name = 'name'
    auto_continue = True  # control whether button auto-enabled
    _log = logging.getLogger('embr_survey')

    # abstract away the ugly stuff for having a nested DV
    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__()
        self.settings = settings
        self.device = device
        self.block_num = block_num
        self.temperature = temperature
        self.widgets = []
        # widget is a complete page
        # assumes widgets is a list/iterable
        if widgets:
            self.add_widgets(widgets)

    def add_widgets(self, widgets):
        for widget in widgets:
            widget.setSizePolicy(qtw.QSizePolicy.Ignored, qtw.QSizePolicy.Ignored)
            self.addWidget(widget)
        desktop = qtw.QDesktopWidget().screenGeometry()
        self.setFixedWidth(1.2*desktop.height())  # magic number to match host widget size
        # initial widget should be properly sized
        self.currentWidget().setSizePolicy(qtw.QSizePolicy.Expanding,
                                           qtw.QSizePolicy.Expanding)
        self.currentWidget().adjustSize()
        self.adjustSize()
        self.widgets.extend(widgets)  # add to list

    def all_ans(self):
        cw = self.currentWidget()  # current widget
        return cw.all_ans() if hasattr(cw, 'all_ans') else True

    def on_enter(self):
        self.device.level = self.temperature
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def on_exit(self):
        pass


class SimpleDV(BaseDV):
    name = 'Simple'
    long_name = 'Long Simple'

    def __init__(self, block_num, device, temperature, settings):
        super().__init__(block_num, device, temperature, settings)
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]
        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]
        random.shuffle(self.questions)

        layout = qtw.QVBoxLayout()
        self.qs = MultiQuestion(header, [q[1] for q in self.questions])
        head = qtw.QLabel(prompt)
        head.setStyleSheet('font-size:18pt;')
        head.setWordWrap(True)
        layout.addWidget(head)
        layout.addWidget(self.qs)
        self.setLayout(layout)

    def save_data(self):
        current_answers = self.qs.get_responses()
        current_answers = [ca if ca >= 1 else None for ca in current_answers]
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
                'questions': [q[1][:40] + '...' for q in self.questions],
                'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        return all([x >= 1 for x in self.qs.get_responses()])
