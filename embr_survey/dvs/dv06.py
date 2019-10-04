import csv
import os
import random
import imgui
import itertools
from datetime import datetime
from pkg_resources import resource_filename

from embr_survey import get_texture_id
from embr_survey.dvs.base_dv import BaseDv
from embr_survey.imgui_common import ok_button
from embr_survey.question import QuestionBlock
from pip._vendor import pytoml as toml


class DV06CriminalRating(BaseDv):
    short_name = 'dv06'
    name = 'dv06_criminal_rating'

    def __init__(self, win, block_num, settings):
        self.win = win
        self.settings = settings
        self.block_num = block_num
        # TODO: load from external?
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.short_name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        # load images
        # TODO: shuffle images?
        img_names = ['dv6_%i.png' % i for i in range(1, 9, 1)]
        self.img_names = [resource_filename('embr_survey', 'images/%s' % img) for img in img_names]
        self.images = [get_texture_id(pth, win.context) for pth in self.img_names]

        self.prompt = translation['prompt'][lang]
        header = translation['header'][lang]

        self.qblocks = []
        self.questions = []
        # we need to add extra ID for questions
        for count, img in enumerate(img_names):
            qs = [('q%i_%i' % (i, count), q[lang]) for i, q in enumerate(translation['question'])]
            self.questions.extend(qs)
            self.qblocks.append(QuestionBlock(win, '', header=header,
                                              questions=[q[1] for q in qs],
                                              extra_id=img))

    def run(self, temperature):
        now = datetime.now().strftime('%y%m%d-%H%M%S')
        answers = []
        done = False
        while not done:
            imgui.text(self.prompt)
            done = ok_button(self.win.impl.reg_font, True)
            self.win.flip()
        # 1 page per mug
        for count, qblock in enumerate(self.qblocks):
            done = False
            self._log.info('Starting image %s.' % self.img_names[count])
            while not done:
                imgui.image(self.images[count], 400, 400)  # TODO: height fixed, width based on original aspect ratio
                current_answers = qblock.update()
                no_nones = not any(ca is None for ca in current_answers)
                done = ok_button(self.win.impl.reg_font, no_nones)
                self.win.flip()
            # TODO: fade between questions
            answers.extend(current_answers)
        # save data, fade out
        settings = self.settings
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.short_name, now))
        num_q = len(self.questions)
        rep_img_names = list(itertools.chain.from_iterable(itertools.repeat(os.path.basename(x), 2) for x in self.img_names))
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': ['...' + q[1][-20:] for q in self.questions],
                'question_original_order': [q[0] for q in self.questions],
                'responses': answers,
                'dv': num_q * [self.name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [temperature],
                'images': rep_img_names}
        keys = sorted(data.keys())
        with open(csv_name, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
