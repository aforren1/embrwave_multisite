import csv
import os
import random
import imgui
from datetime import datetime
from pkg_resources import resource_filename

from embr_survey import get_texture_id
from embr_survey.dvs.base_dv import BaseDv
from embr_survey.imgui_common import ok_button
from embr_survey.question import QuestionBlock
from pip._vendor import pytoml as toml


class DV05HousesHomelikeness(BaseDv):
    short_name = 'dv05'
    name = 'dv05_houses_homelikeness'

    def __init__(self, win, block_num, settings):
        self.win = win
        self.settings = settings
        self.block_num = block_num
        # TODO: load from external?
        lang = settings['language']
        locale = settings['locale']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.short_name)
        with open(translation_path, 'r') as f:
            translation = toml.load(f)

        locale_path = os.path.join(settings['locale_dir'], '%s.toml' % self.short_name)

        with open(locale_path, 'r') as f:
            locale_settings = toml.load(f)

        # read in all images
        images = locale_settings['house_photos'][locale]
        images = [resource_filename('embr_survey', 'images/%s' % img) for img in images]
        self.images = [get_texture_id(pth, win.context) for pth in images]

        # read in translations, also plugging in locale-specific info
        self.prompt = translation['prompt'][lang]
        self.preprompt = translation['preprompt'][lang]
        self.big_title = translation['big_title'][lang]

        self.background = translation['background'][lang] % locale_settings['house_cost'][locale]
        self.subtitle = translation['subtitle'][lang]

        self.floor1 = translation['f1'][lang]
        self.floor2 = translation['f2'][lang] % locale_settings['floor_label'][locale][0]
        self.floor3 = translation['f3'][lang] % locale_settings['floor_label'][locale][1]

        prompt2 = translation['prompt2'][lang]
        header = translation['header'][lang]

        self.questions = [('q%i' % i, q[lang]) for i, q in enumerate(translation['question'])]

        # TODO: should this one be shuffled? Or which ones should?
        # random.shuffle(self.questions)

        self.qs = QuestionBlock(win, prompt2, header=header,
                                questions=[q[1] for q in self.questions])

    def run(self, temperature):
        now = datetime.now().strftime('%y%m%d-%H%M%S')
        done = False
        while not done:
            imgui.text(self.prompt)
            done = ok_button(self.win.impl.reg_font, True)
            self.win.flip()

        # main page
        done = False
        while not done:
            imgui.text(self.preprompt)
            imgui.image(self.images[0], 400, 400)  # make sure the images are in the right spots
            imgui.text(self.big_title)  # TODO: make bigger
            # TODO: place images in sensible places
            imgui.text(self.background)
            imgui.spacing()
            imgui.text(self.subtitle)
            imgui.text(self.floor1)

            imgui.text(self.floor2)

            imgui.text(self.floor3)

            for img in self.images[1:]:
                # TODO: position/center
                imgui.image(img, 400, 400)

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
                'questions': [q[1][:30] + '...' for q in self.questions],
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
