import csv
import os
import random
from datetime import datetime

from embr_survey.dvs.base_dv import BaseDv
from embr_survey.imgui_common import ok_button
from embr_survey.question import QuestionBlock
from pip._vendor import pytoml as toml


class DV03Utilitarian(BaseDv):
    short_name = 'dv03'
    name = 'dv03_utilitarian'

    def __init__(self, win, block_num, settings):
        self.win = win
        self.settings = settings
        self.block_num = block_num
        # TODO: load from external?
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.short_name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]

        # questions
        self.questions = [('q%i' % i, pr[lang], q[lang]) for i, (pr, q) in enumerate(zip(translation['subprompt'], translation['question']))]

        # new ordering
        random.shuffle(self.questions)

        # one question block per page
