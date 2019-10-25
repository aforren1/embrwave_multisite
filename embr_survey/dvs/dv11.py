# NOTE: device only active for name-picking, not second part
import os
import csv
import PySide2.QtWidgets as qtw
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from embr_survey.common_widgets import JustText, SingleQuestion
from embr_survey.dvs.base_block import StackedDV


# part1, part2 share data


class NameInput(qtw.QWidget):
    def __init__(self, prompt, names=None):
        super().__init__()
        self.prev_answers = names
        prompt = JustText(prompt)
        layout = qtw.QVBoxLayout()
        layout.addWidget(prompt, alignment=Qt.AlignVCenter)
        self.name_input = qtw.QLineEdit()
        self.name_input.setMaximumWidth(300)
        fnt = self.name_input.font()
        fnt.setPointSize(26)
        self.name_input.setFont(fnt)
        layout.addWidget(self.name_input, alignment=Qt.AlignVCenter)
        self.setLayout(layout)

    def all_ans(self):
        name = self.name_input.text().strip(' ')
        tmp = [x.lower() for x in self.prev_answers]
        low_txt = name.lower()
        if low_txt != '' and low_txt not in tmp:
            self.prev_answers.append(name)
            return True
    
    def get_responses(self):
        name = self.name_input.text().strip(' ')
        return name


class RelationshipQuestion(qtw.QWidget):
    def __init__(self, img_name, header, question):
        super().__init__()
        img = QPixmap(img_name)
        img_holder = qtw.QLabel()
        img_holder.setPixmap(img.scaled(1000, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_holder.setAlignment(Qt.AlignCenter)
        self.question = SingleQuestion(header, question)
        layout = qtw.QVBoxLayout()
        layout.addWidget(img_holder)
        layout.addWidget(self.question)
        self.setLayout(layout)

    def get_responses(self):
        return self.question.get_responses()

    def all_ans(self):
        return all([x >= 1 for x in self.get_responses()])


class DV11Part1(StackedDV):
    long_name = 'dv11_thinkingaboutlovedones'
    name = 'dv11'

    # no data to save for this one, just data to share
    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        self.passed_data = []  # hopefully, this will percolate until part 2
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        q1_part1 = [translation['q1'][lang]]  # think of someone you know
        q2_part1 = [translation['q2'][lang]]*4  # think of someone else

        q1_part1.extend(q2_part1)
        widgets = []
        for num, q in enumerate(q1_part1):
            widgets.append(NameInput(('%i. ' % (num+1)) + q, self.passed_data))
        self.add_widgets(widgets)

    def on_exit(self):
        # get all the names
        self.passed_data = [w.name_input.text().strip(' ') for w in self.widgets]


class DV11Part2(StackedDV):

    long_name = 'dv11_thinkingaboutlovedones'
    name = 'dv11'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, 0, settings, widgets)
        self.temperature = temperature  # we set the device temp to 0, but record the prev

    def on_enter(self):
        # load settings from external TOML
        settings = self.settings
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        circle_img = resource_filename('embr_survey', 'images/dv11_1.png')
        q1_part2 = translation['q_sub'][lang]
        header = translation['header'][lang]

        widgets = []
        self.questions = []
        for name in self.passed_data:
            q = q1_part2 % name
            widgets.append(RelationshipQuestion(circle_img, header, q))
            self.questions.append(q)
        self.add_widgets(widgets)
        # just to be explicit, I think inserting the
        # in-between section should already have disabled the device
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets]
        current_answers = [x for sublist in current_answers for x in sublist]
        current_answers = [ca if ca >= 1 else None for ca in current_answers]

        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(self.passed_data)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'names': self.passed_data,
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature]}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
