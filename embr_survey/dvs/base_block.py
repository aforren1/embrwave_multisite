import csv
import os
import random
import logging

import PyQt5.QtWidgets as qtw
from pip._vendor import pytoml as toml
from PyQt5.QtCore import Qt, pyqtSignal
from embr_survey.common_widgets import MultiQuestion
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
        pass

    def on_exit(self):
        pass


class SimpleDV(BaseDV):
    name = 'Simple'
    long_name = 'Long Simple'

    def __init__(self, block_num, device, temperature, settings):
        super().__init__(block_num, device, temperature, settings)
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.short_name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]
        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]
        random.shuffle(self.questions)

        layout = qtw.QVBoxLayout()
        self.qs = MultiQuestion(header, [q[1] for q in self.questions])
        head = qtw.QLabel(prompt)
        head.setStyleSheet('font-size:26pt;')
        head.setWordWrap(True)
        layout.addWidget(head)
        layout.addWidget(self.qs)
        self.setLayout(layout)

    def on_enter(self):
        self.device.level = self.temperature
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def save_data(self):
        current_answers = self.qs.get_responses()
        current_answers = [ca if ca >= 0 else None for ca in current_answers]
        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.short_name, now))
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


if __name__ == '__main__':
    from datetime import datetime
    from embr_survey.window import MainWindow
    from embr_survey import setup_logger
    from embr_survey.common_widgets import JustText, EmbrSection
    from embr_survey.embrwave import DummyWave
    from embr_survey.dvs import DV01SimilarityObjects

    settings = {'language': 'en', 'translation_dir': './translations/',
                'data_dir': './data/', 'id': 'test',
                'datetime_start': 0, 'locale': 'us'}
    setup_logger(settings['data_dir'], 0)
    logger = logging.getLogger('embr_survey')
    logger.info('Starting experiment for %s' % settings['id'])
    logger.info('Datetime of start (YMD-HMS): %s' % 0)
    logger.info('Seed: %s' % 1)
    logger.info('Language: %s' % settings['language'])
    logger.info('Locale: %s' % settings['locale'])
    logger.info('----------')

    app = qtw.QApplication([])

    dev = DummyWave()

    start = JustText('start.')
    embr_sec = EmbrSection('Please wait.', dev)
    holder = JustText("In this next section, we will ask you to read several scenarios and indicate <b>your opinion</b> about them.")
    dv1 = DV01SimilarityObjects(1, dev, 9, settings)

    stack = [start, [embr_sec, holder, dv1]]
    window = MainWindow(stack)
    with dev:
        app.exec_()
