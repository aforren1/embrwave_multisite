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
        self.qblocks = []
        for (count, subprompt, question) in self.questions:
            self.qblocks.append(QuestionBlock(win, subprompt, header=header,
                                              questions=[question]))

    def run(self, temperature):
        # fade in
        now = datetime.now().strftime('%y%m%d-%H%M%S')
        answers = []
        for qblock in self.qblocks:
            done = False
            while not done:
                current_answers = qblock.update()  # in this case, should just be one
                no_nones = not any(ca is None for ca in current_answers)
                done = ok_button(self.win.impl.reg_font, no_nones)
                self.win.flip()
            # TODO: fade between questions
            answers.extend(current_answers)
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
                'responses': answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [temperature]}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
