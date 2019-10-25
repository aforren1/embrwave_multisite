import os
import csv
import random
import itertools
import PySide2.QtWidgets as qtw
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from embr_survey.common_widgets import JustText
from embr_survey.dvs.base_block import StackedDV
from embr_survey import application_path
# use QDoubleValidator to make it numbers-only
from PySide2.QtGui import QDoubleValidator


class ImageNQuestions(qtw.QWidget):
    def __init__(self, img_name, questions):
        super().__init__()
        layout = qtw.QVBoxLayout()
        img = QPixmap(img_name)
        img_holder = qtw.QLabel()
        img_holder.setPixmap(img.scaled(800, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        img_holder.setAlignment(Qt.AlignCenter)
        self.edit_boxes = []
        layout.addWidget(img_holder)
        for q in questions:
            wid = qtw.QWidget()
            hlay = qtw.QHBoxLayout()
            txt = JustText(q)
            ebox = qtw.QLineEdit()
            # not sure how many digits to allow depending on currency
            ebox.setValidator(QDoubleValidator(0, 10000, 2))
            ebox.setMaximumWidth(200)
            fnt = ebox.font()
            fnt.setPointSize(26)
            ebox.setFont(fnt)
            ebox.setStyleSheet('QLineEdit {background-color: yellow; border: 2px solid gray;}')
            self.edit_boxes.append(ebox)
            hlay.addWidget(txt, Qt.AlignRight | Qt.AlignVCenter)
            hlay.addWidget(ebox, Qt.AlignLeft | Qt.AlignVCenter)
            wid.setLayout(hlay)
            layout.addWidget(wid)
        self.setLayout(layout)

    def get_responses(self):
        return [x.text() for x in self.edit_boxes]

    def all_ans(self):
        vals = self.get_responses()
        return all([v != '' for v in vals])

# DV13_willingness_to_pay


class DV13WillingnessToPay(StackedDV):
    long_name = 'dv13_willingness_to_pay'
    name = 'dv13'

    def __init__(self, block_num, device, temperature, settings, widgets=None):
        super().__init__(block_num, device, temperature, settings, widgets)
        # load settings from external TOML
        lang = settings['language']
        locale = settings['locale']
        translation_path = os.path.join(settings['translation_dir'], '%s.toml' % self.name)
        with open(translation_path, 'r', encoding='utf8') as f:
            translation = toml.load(f)

        # we want to be able to localize the batteries
        locale_path = os.path.join(settings['locale_dir'], '%s.toml' % self.name)

        with open(locale_path, 'r', encoding='utf8') as f:
            locale_settings = toml.load(f)
        
        # load images
        try:
            battery_name = locale_settings['battery_photo'][locale]
        except KeyError:
            # default locale
            battery_name = locale_settings['battery_photo']['us']
        
        if os.path.split(battery_name)[0] != '':
            battery_path = os.path.join(application_path, battery_name)
        else:
            battery_path = resource_filename('embr_survey', 'images/%s' % battery_name)

        cake_path = resource_filename('embr_survey', 'images/dv13_cake.png')

        q1 = translation['q1'][lang]  # how much would you pay?
        q2 = translation['q2'][lang]  # how much do you think it retails for?
        battery_txt = translation['battery'][lang]
        cake_txt = translation['cake'][lang]

        images = [(battery_txt, battery_path), (cake_txt, cake_path)]
        random.shuffle(images)
        self.img_names = [i[1] for i in images]
        widgets = []
        self.questions = []
        try:
            currency = locale_settings['currency'][locale]
        except KeyError:
            currency = locale_settings['currency']['us']
        for img in images:
            quests = [(q % img[0]) + (' (%s)' % currency) for q in [q1, q2]]
            self.questions.extend(quests)
            widgets.append(ImageNQuestions(img[1], quests))
        self.add_widgets(widgets)

    def save_data(self):
        # flatten out responses
        current_answers = [x.get_responses() for x in self.widgets]
        current_answers = [x for sublist in current_answers for x in sublist]
        current_answers = [float(ca) if (ca != '' and float(ca) >= 1) else None for ca in current_answers]

        settings = self.settings
        now = self._start_time.strftime('%y%m%d_%H%M%S')
        csv_name = os.path.join(settings['data_dir'], '%s_%s.csv' % (self.name, now))
        num_q = len(self.questions)
        rep_img_names = list(itertools.chain.from_iterable(itertools.repeat(os.path.basename(x), 2) for x in self.img_names))
        data = {'participant_id': num_q * [settings['id']],
                'datetime_start_exp': num_q * [settings['datetime_start']],
                'datetime_start_block': num_q * [now],
                'datetime_end_block': num_q * [self._end_time.strftime('%y%m%d_%H%M%S')],
                'language': num_q * [settings['language']],
                'locale': num_q * [settings['locale']],
                'questions': [q[:40] + '...' for q in self.questions],
                # 'question_original_order': [q[0] for q in self.questions],
                'responses': current_answers,
                'dv': num_q * [self.long_name],
                'block_number': num_q * [self.block_num],
                'embr_temperature': num_q * [self.temperature],
                'images': rep_img_names}
        keys = sorted(data.keys())
        with open(csv_name, 'w', newline='\n', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(keys)
            writer.writerows(zip(*[data[key] for key in keys]))
