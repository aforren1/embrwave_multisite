import csv
import os
import random
from datetime import datetime

from embr_survey.imgui_common import ok_button
from embr_survey.question import QuestionBlock
from pip._vendor import pytoml as toml


class BaseDv(object):
    def __init__(self, win, settings):
        # read images, ...
        pass

    def run(self, temperature):
        # event loop(s)
        pass


class SimpleDV(BaseDv):
    short_name = None
    name = None
    # for the pure survey ones

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
        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]
        # new ordering
        random.shuffle(self.questions)

        self.qs = QuestionBlock(win, prompt,
                                header=header,
                                questions=[q[1] for q in self.questions])

    def run(self, temperature):
        # two data files-- a CSV with:
        # participant ID, block ID (dv1_blah), block number (for ordering),
        # block time start, question text, question number

        # fade in
        now = datetime.now().strftime('%y%m%d-%H%M%S')
        done = False
        while not done:
            current_answers = self.qs.update()
            no_nones = not any(ca is None for ca in current_answers)
            done = ok_button(self.win.impl.reg_font, no_nones)
            self.win.flip()
        # save data, fade out
        settings = self.settings
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.short_name, now))
        num_q = len(self.questions)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'seed': num_q * [settings['seed']],
                'questions': [q[1] for q in self.questions],
                'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [temperature]}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
