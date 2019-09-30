import random
from datetime import datetime
from embr_survey.dvs.base_dv import BaseDv
from embr_survey.question import QuestionBlock
from embr_survey.imgui_common import ok_button
from pip._vendor import pytoml as toml
import os
import csv


class DV01SimilarityObjects(BaseDv):
    def __init__(self, win, block_num, settings):
        self.win = win
        self.settings = settings
        self.block_num = block_num
        # TODO: load from external?
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], 'dv01.toml')
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        prompt = translation['prompt'][lang]
        header = translation['header'][lang]
        self.questions = [q[lang] for q in translation['question']]
        # new ordering
        random.shuffle(self.questions)

        self.qs = QuestionBlock(win, prompt,
                                header=header,
                                questions=[q for q in self.questions])

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
        csv_name = os.path.join(settings['data_dir'], 'dv01_%s.csv' % now)
        num_q = len(self.questions)
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'seed': num_q * [settings['seed']],
                'questions': self.questions,
                'responses': current_answers,
                'dv': num_q * ['dv01_similarity_objects']}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))


if __name__ == '__main__':
    from embr_survey.window import ExpWindow
    win = ExpWindow()

    dv1 = DV01SimilarityObjects(win, 1, {'language': 'en',
                                         'translation_dir': 'translations/'})
    dv1.run(0)
