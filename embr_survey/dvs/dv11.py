# NOTE: device only active for name-picking, not second part
import os
import PySide2.QtWidgets as qtw
from embr_survey import app_path
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from embr_survey.common_widgets import JustText, MultiQuestion
from embr_survey.dvs.base_block import StackedDV


# part1, part2 share data


class NameInput(qtw.QWidget):
    def __init__(self, prompt):
        prompt = JustText(prompt)
        layout = qtw.QHBoxLayout()
        layout.addWidget(prompt, alignment=Qt.AlignRight | Qt.AlignVCenter)
        self.name_input = qtw.QLineEdit(self.name)
        layout.addWidget(self.name_input, alignment=Qt.AlignLeft | Qt.AlignVCenter)

    def all_ans(self):
        low_txt = self.name_input.text.lower()
        return low_txt != '' and low_txt not in self.prev_answers


class RelationshipQuestions(qtw.QWidget):
    def __init__(self, question_txt, image_path):
        # layout =
        pass


class DV11Part1(StackedDV):
    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        q1_part1 = translation['q1'][lang]  # think of someone you know
        q2_part1 = [translation['q2'][lang]]*4

        qs = q1_part1.extend(q2_part1)
        widgets = []
        for q in qs:
            widgets.append(NameInput(q))


class DV11Part2(StackedDV):

    long_name = 'dv11_thinkingaboutlovedones'
    name = 'dv11'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        circle_img = resource_filename('embr_survey', 'images/dv11_1.png')
        q1_part2 = translation['qsub'][lang]

    def on_enter(self):
        self.device.level = 0
        self._log.info('Temperature set to %i for %s' % (self.temperature,
                                                         self.long_name))
