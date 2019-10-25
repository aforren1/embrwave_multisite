import csv
import logging
import os
import random

import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from pip._vendor import pytoml as toml

from embr_survey.common_widgets import JustText, SingleQuestion, EmbrSection
from embr_survey.dvs.base_block import StackedDV
import random

# idle (5s)
# 1. Too cold/too hot (1-7)
# 2. Max heat or max cool for 10 sec (please wait)
# 3. A this moment, what temp does the room feel like? (numeric resp) (still heating/cooling)
# 4. (Embr idle) How hot or cold did device feel?
#    Was the Embr Wave comfortable...
# idle (5s)
# repeat 1-4 for opposite temperature

class HeatQuestions(qtw.QWidget):
    # how hot or cold did the device feel, and
    # was it comfortable?
    def __init__(self, header1, question1, header2, question2):
        super().__init__()
        self.q1 = SingleQuestion(header1, question1)
        self.q2 = SingleQuestion(header2, question2)
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.q1)
        layout.addWidget(self.q2)
        self.setLayout(layout)
    
    def get_responses(self):
        return [self.q1.get_responses()[0], self.q2.get_responses()[0]]
    
    def all_ans(self):
        return all([x >= 1 for x in self.get_responses()])

class CurrentTempQuestion(qtw.QWidget):
    # Question + spinbox
    def __init__(self, text, units, device):
        super().__init__()
        self.device = device
        prompt = JustText(text)
        layout = qtw.QVBoxLayout()
        layout.addWidget(prompt, alignment=Qt.AlignVCenter)
        self.temp_input = qtw.QSpinBox()
        if units == 'C':
            minmax = (0, 100)
            default = 21
        elif units == 'F':
            minmax = (32, 212)
            default = 70
        self.temp_input.setRange(*minmax)
        self.temp_input.setSingleStep(1)
        self.temp_input.setSuffix('°' + units)
        self.temp_input.setValue(default)
        fnt = self.temp_input.font()
        fnt.setPointSize(26)
        self.temp_input.setFont(fnt)
        layout.addWidget(self.temp_input, alignment=Qt.AlignVCenter)
        self.setLayout(layout)

    def all_ans(self):
        return True
    
    def get_responses(self):
        return self.temp_input.value()
    
    def on_exit(self):
        self.device.level = 0

class EmbrSection2(JustText):
    auto_continue = False

    def __init__(self, text, device, temperature=0, duration=5000):
        super().__init__(text)
        self.device = device
        self.setAlignment(Qt.AlignCenter)
        self.temp = temperature
        self.dur = duration

    def on_enter(self):
        # button ref is injected
        self._button.state = 'neutral'
        QTimer.singleShot(self.dur, self._enable)
        self.device.level = self.temp

    def _enable(self):
        self._button.state = 'complete'


class EfficacyBlock(StackedDV):
    long_name = 'embrwave_efficacy'
    name = 'efficacy'

    def __init__(self, device, settings):
        super().__init__(15, device, 0, settings, None)
        lang = settings['language']
        locale = settings['locale']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        translation_path = os.path.join(self.settings['translation_dir'], 'misc.toml')
        with open(translation_path, 'r', encoding='utf8') as f:
            misc_translations = toml.load(f)

        locale_path = os.path.join(settings['locale_dir'], '%s.toml' % self.name)

        with open(locale_path, 'r', encoding='utf8') as f:
            locale_settings = toml.load(f)
        
        try:
            temperature_units = locale_settings['units'][locale]
        except KeyError:
            temperature_units = locale_settings['units']['us']

        first = random.choice([-9, 7])
        second = [-9, 7]
        second.remove(first)
        second = second[0]
        temp_q = translation['temp_q'][lang]
        temp_header = translation['temp_header'][lang]
        room_q = translation['room_q'][lang]
        hot_cold = translation['hot_cold'][lang]
        hot_cold_header = translation['hot_cold_header'][lang]
        comfort_q = translation['comfort_q'][lang]
        comfort_header = translation['comfort_header'][lang]
        
        self.comfort1 = SingleQuestion(temp_header, temp_q)
        self.wait1 = EmbrSection2(misc_translations['wait_until_green'][lang], device, first, 10000)
        self.current_temp1 = CurrentTempQuestion(room_q, temperature_units, device) # resets to 0 at end
        self.heatqs1 = HeatQuestions(hot_cold_header, hot_cold, comfort_header, comfort_q)
        self.idle1 = EmbrSection2(misc_translations['wait_until_green'][lang], device, 0, 5000)
        # part 2 (opposite temperature)
        self.comfort2 = SingleQuestion(temp_header, temp_q)
        self.wait2 = EmbrSection2(misc_translations['wait_until_green'][lang], device, second, 10000)
        self.current_temp2 = CurrentTempQuestion(room_q, temperature_units, device) # resets to 0 at end
        self.heatqs2 = HeatQuestions(hot_cold_header, hot_cold, comfort_header, comfort_q)

        self.add_widgets([self.comfort1, self.wait1, self.current_temp1, self.heatqs1, self.idle1,
                          self.comfort2, self.wait2, self.current_temp2, self.heatqs2])
        self.q_temp_pairs = [(temp_q, first), (room_q, first), (hot_cold, first), (comfort_q, first),
                             (temp_q, second), (room_q, second), (hot_cold, second), (comfort_q, second)]
    
    def save_data(self):
        resp_heat1 = self.heatqs1.get_responses()
        resp_heat1 = [ca if ca >= 1 else None for ca in resp_heat1]
        resp_heat2 = self.heatqs2.get_responses()
        resp_heat2 = [ca if ca >= 1 else None for ca in resp_heat2]
        current_answers = [self.comfort1.get_responses()[0], self.current_temp1.get_responses(),
                           resp_heat1[0], resp_heat1[1],
                           self.comfort2.get_responses()[0], self.current_temp2.get_responses(),
                           resp_heat2[0], resp_heat2[1]]
        temps = [v[1] for v in self.q_temp_pairs]
        qs = [v[0] for v in self.q_temp_pairs]
        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(temps)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': [q + '...' for q in qs],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': temps}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))

    def all_ans(self):
        return True