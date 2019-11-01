import atexit
import signal
from functools import partial
import logging
import os
from collections import Counter
from functools import partial
from datetime import datetime
from glob import glob

import PySide2.QtWidgets as qtw
from embr_survey import application_path
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt, QTimer
from embr_survey.embrwave import PreEmbr, DummyPreEmbr
from embr_survey.pygatt.exceptions import NotConnectedError
from embr_survey.embrwave import EmbrWave, DummyWave, gatt_ble
import serial
from serial.tools import list_ports

base_style = '''
QPushButton {border:4px solid rgb(0, 0, 0);
             border-radius:10px;
             font: bold 26px;padding: 24px;}
QPushButton:pressed {border-style:inset;}
QPushButton {background-color: rgb(255, 140, 0);}
QPushButton:pressed {background-color: rgb(255, 165, 0);}
'''

green_style = '''
QPushButton {border:4px solid rgb(0, 0, 0); 
             border-radius:10px;
             font: bold 26px;padding: 24px;}
QPushButton:pressed {border-style:inset;}
QPushButton {background-color: rgb(120, 255, 0);}
QPushButton:pressed {background-color: rgb(120, 255, 0);}

'''


def count_language_keys(files, ref):
    # must have *all* language keys to work (otherwise, ignore)
    total_keys = []
    final_round = []
    languages = []  # final product (list of languages)
    for tf in files:
        with open(tf, 'r', encoding='utf8') as f:
            dat = toml.load(f)
        for a in dat.keys():
            if isinstance(dat[a], list):
                for v in dat[a]:
                    total_keys.extend(list(v.keys()))
            else:
                total_keys.extend(list(dat[a].keys()))
        # number of occurrence (en as reference)
        counts = Counter(total_keys)
        count_en = counts[ref]
        for lang in counts:
            if counts[lang] == count_en:
                final_round.append(lang)
    final_c = Counter(final_round)
    count_en = final_c[ref]
    for lang in final_c:
        if final_c[lang] == count_en:
            languages.append(lang)
    return languages


def check_locale_keys(files, ref):
    # must have *at least one* locale key present
    # defaults to 'us' (or whatever the default ends up being)
    # if the chosen key doesn't have an entry
    total_keys = []
    for tf in files:
        with open(tf, 'r', encoding='utf8') as f:
            dat = toml.load(f)
        for a in dat.keys():
            if isinstance(dat[a], list):
                for v in dat[a]:
                    total_keys.extend(list(v.keys()))
            else:
                total_keys.extend(list(dat[a].keys()))
    # get uniques
    res = list(set(total_keys))
    return res  # TODO: sort by count?


def on_activated(self, idx):
    try:
        new_lang = self.lang.currentText()
        self.id_label.setText(self.translations['participant'][new_lang])
        self.lang_label.setText(self.translations['language'][new_lang])
        self.locale_label.setText(self.translations['locale'][new_lang])
        self._button.incomplete_txt = self.translations['incomplete'][new_lang]
        self._button.setText(self.translations['next'][new_lang])
    except AttributeError:
        pass


def on_blink(sel):
    sel.pre_embr.scan()

    dev = sel.device.currentText()
    if dev:
        sel.pre_embr.blink(sel.device.currentText())
    sel.device.clear() # TODO: why was this here?
    sel.device.addItems(sel.pre_embr.addrs)


class IntroDlg(qtw.QWidget):
    _log = logging.getLogger('embr_survey')
    auto_continue = True  # control whether button auto-enabled

    def __init__(self):
        super().__init__()
        self._window = None  # patched in later (reference to MainWindow)
        self._device = DummyWave()
        self._is_connected = False

        if not gatt_ble:
            self.pre_embr = DummyPreEmbr()
        else:
            self.pre_embr = PreEmbr()

        # id, language, locale
        self.settings = {}
        self.settings['translation_dir'] = os.path.join(application_path, 'translations/')
        self.settings['locale_dir'] = os.path.join(application_path, 'locale/')
        self.settings['app_path'] = application_path  # allows searching relative
        # to the location of the executable
        # check all translation files, and list only complete ones

        translation_files = glob(os.path.join(self.settings['translation_dir'], '*.toml'))

        # figure out complete translations, using english as ref
        languages = count_language_keys(translation_files, 'en')
        # now same with localization
        # I think it's "more" ok to have missing keys in localization files,
        # and if the locale has *any* keys it should be allowed (and the default
        # subbed in if missing)
        locale_files = glob(os.path.join(self.settings['locale_dir'], '*.toml'))
        locales = check_locale_keys(locale_files, 'us')

        # translations for *this* widget
        translation_path = os.path.join(self.settings['translation_dir'], 'misc.toml')
        with open(translation_path, 'r', encoding='utf8') as f:
            self.translations = toml.load(f)

        # widgets and layout
        layout = qtw.QGridLayout()

        self.id = qtw.QLineEdit()
        self.lang = qtw.QComboBox()
        fnt = self.lang.font()
        fnt.setPointSize(26)
        self.lang.setFont(fnt)
        self.lang.currentIndexChanged.connect(partial(on_activated, self))
        self.locale = qtw.QComboBox()
        self.locale.setFont(fnt)
        self.device = qtw.QComboBox()
        self.device.setFont(fnt)
        self.device.addItems(self.pre_embr.addrs)

        self.id.setFont(fnt)

        # TODO: these *also* need to be translated...
        self.id_label = JustText(self.translations['participant']['en'])
        self.lang_label = JustText(self.translations['language']['en'])
        self.locale_label = JustText(self.translations['locale']['en'])
        self.device_label = JustText('Embr Wave ID')
        self.dev_instr = JustText(self.translations['dev_instr']['en'])

        # default to english/us, which *should* exist & be complete
        self.lang.addItems(languages)
        self.lang.setCurrentText('en')
        self.locale.addItems(locales)
        self.locale.setCurrentText('us')

        self.blinker = qtw.QPushButton('Blink')
        self.blinker.clicked.connect(partial(on_blink, self))

        self.connector = qtw.QPushButton('Connect (will freeze\ntemporarily)')
        self.connector.clicked.connect(self.try_connect)

        self.blinker.setStyleSheet(base_style)
        self.connector.setStyleSheet(base_style)

        layout.addWidget(self.id_label, 0, 0, Qt.AlignCenter)
        layout.addWidget(self.id, 0, 1, Qt.AlignCenter | Qt.AlignLeft)
        layout.addWidget(self.lang_label, 1, 0, Qt.AlignCenter)
        layout.addWidget(self.lang, 1, 1, Qt.AlignCenter | Qt.AlignLeft)
        layout.addWidget(self.locale_label, 2, 0, Qt.AlignCenter)
        layout.addWidget(self.locale, 2, 1, Qt.AlignCenter | Qt.AlignLeft)
        layout.addWidget(self.device_label, 3, 0, Qt.AlignCenter)
        layout.addWidget(self.device, 3, 1, Qt.AlignCenter | Qt.AlignLeft)
        layout.addWidget(self.dev_instr, 5, 0, Qt.AlignCenter)
        layout.addWidget(self.blinker, 5, 1, Qt.AlignCenter | Qt.AlignLeft)
        layout.addWidget(self.connector, 5, 1, Qt.AlignCenter)

        self.setLayout(layout)

    # TODO: on exit, should do everything currently done in main-- adding widgets to the stack
    # with proper settings,
    def all_ans(self):
        return self.id.text() != ''

    def try_connect(self):
        if not self._is_connected:
            self.connector.setText('Connecting...\n(frozen)')
            QTimer.singleShot(50, self._single_shot)

    def _single_shot(self):
        try:
            # connect to the device
            # blocks progression (TODO: add a note)
            if not self._is_connected:
                device = EmbrWave(self.device.currentText())
                atexit.register(device.close)
                signal.signal(signal.SIGINT, partial(handle_sig, device))
                self._is_connected = True
                self._device = device
                self.connector.setText('Connected.')
                self.connector.setStyleSheet(green_style)
                self.layout().addWidget(JustText('<b>Battery level: %i</b>' % device.battery_charge), 6, 0, 2, 2, Qt.AlignCenter)
        except Exception as e:
            self.connector.setText('Connection failed.\nTry to click again\n(or restart program)?')
            self._is_connected = False
            self._log.warn(repr(e))

    def on_exit(self):
        from embr_survey import application_path
        from embr_survey import setup_logger
        from embr_survey._version import __version__
        from hashlib import md5
        import random
        from time import time
        from embr_survey.common_widgets import EmbrFactory, EmbrSection
        import embr_survey.dvs as dvs

        # we should now have sufficient info to start the experiment
        exp_start = datetime.now().strftime('%y%m%d-%H%M%S')
        settings = {'id': self.id.text(),
                    'language': self.lang.currentText(),
                    'locale': self.locale.currentText(),
                    'device_addr': self.device.currentText()}
        settings['data_dir'] = os.path.join(application_path, 'data/%s' % settings['id'], '')
        settings['translation_dir'] = os.path.join(application_path, 'translations/')
        settings['locale_dir'] = os.path.join(application_path, 'locale/')
        settings['datetime_start'] = exp_start

        os.makedirs(settings['data_dir'], exist_ok=True)
        setup_logger(settings['data_dir'], exp_start)
        seed = int(time()) # seconds since Unix epoch
        random.seed(seed)
        settings['seed'] = seed
        logger = logging.getLogger('embr_survey')
        logger.info('Starting experiment for %s' % settings['id'])
        logger.info('Datetime of start (YMD-HMS): %s' % exp_start)
        logger.info('Seed: %s' % seed)
        logger.info('Language: %s' % settings['language'])
        logger.info('Locale: %s' % settings['locale'])
        logger.info('embr_survey version: %s' % __version__)
        logger.info('----------')
        device = self._device
        logger.info('Device: %s' % device.name)
        logger.info('Device ID, Firmware: %s, %s' % (device.device_id, device.firmware_version))
        logger.info('Device battery remaining: %s' % device.battery_charge)
        logger.info('----------')

        # finally good to go

        temps = random.choices([-9, -5, 5, 7], k=14)
        dv_order = list(range(14))
        random.shuffle(dv_order)
        temps2 = [temps[val] for val in dv_order]
        self._log.info('Temperature progression: %s' % temps2)

        # TODO: feed in locale
        lang = settings['language']
        ef = EmbrFactory(self.translations['wait_until_green'][lang], device)
        # +1 is to make block numbering 1-based in data
        dv0 = [dvs.DV00Intro_1(device, settings),
               EmbrSection(self.translations['wait_until_green'][lang], device, 7, 10000),
               EmbrSection(self.translations['wait_until_green'][lang], device, -9, 10000),
               dvs.DV00Intro_2(device, settings)]
        dv1 = [ef.spawn(), dvs.DV01(dv_order.index(0) + 1, device, temps2[0], settings)]
        dv2 = [ef.spawn(), dvs.DV02(dv_order.index(1) + 1, device, temps2[1], settings)]
        dv3 = [ef.spawn(), dvs.DV03(dv_order.index(2) + 1, device, temps2[2], settings)]
        dv4 = [ef.spawn(), dvs.DV04(dv_order.index(3) + 1, device, temps2[3], settings)]
        dv5 = [ef.spawn(), dvs.DV05(dv_order.index(4) + 1, device, temps2[4], settings)]
        dv6 = [ef.spawn(), dvs.DV06(dv_order.index(5) + 1, device, temps2[5], settings)]
        dv7 = [ef.spawn(), dvs.DV07(dv_order.index(6) + 1, device, temps2[6], settings)]
        dv8 = [ef.spawn(), dvs.DV08(dv_order.index(7) + 1, device, temps2[7], settings)]
        dv9 = [ef.spawn(), dvs.DV09(dv_order.index(8) + 1, device, temps2[8], settings)]
        dv10 = [ef.spawn(), dvs.DV10(dv_order.index(9) + 1, device, temps2[9], settings)]
        dv11 = [ef.spawn(), dvs.DV11Part1(dv_order.index(10) + 1, device, temps2[10], settings),
                ef.spawn(), dvs.DV11Part2(dv_order.index(10) + 1, device, temps2[10], settings)]
        dv12 = [ef.spawn(), dvs.DV12(dv_order.index(11) + 1, device, temps2[11], settings)]
        dv13 = [ef.spawn(), dvs.DV13(dv_order.index(12) + 1, device, temps2[12], settings)]
        dv14 = [ef.spawn(), dvs.DV14(dv_order.index(13) + 1, device, temps2[13], settings)]

        efficacy = dvs.EfficacyBlock(device, settings)
        # Parts 5 and 6 depend on answers to part 4
        is_end = random.choice([0, 1])
        block_num = 0
        if is_end:
            block_num = 15

        individ_diffs = [dvs.IndividualDifferencesPart1(block_num, device, settings),
                         dvs.IndividualDifferencesPart2(block_num, device, 0, settings),
                         dvs.IndividualDifferencesPart3(block_num, device, 0, settings),
                         dvs.IndividualDifferencesPart4(block_num, device, settings)]

        debriefing = dvs.Debriefing(-1, device, 0, settings)
        stack = [dv1, dv2, dv3, dv4, dv5,
                 dv6, dv7, dv8, dv9, dv10,
                 dv11, dv12, dv13, dv14]
        # shuffle around questions
        stack2 = [stack[i] for i in dv_order]
        stack2.append(efficacy) # always right after DVs
        if is_end:
            stack2.extend(individ_diffs)
        else:
            stack2.insert(0, individ_diffs)
        stack2.append(debriefing)
        self._window.add_widgets([dv0]) # always first (sanity check)
        self._window.add_widgets(stack2)

def handle_sig(dev, *args):
    print('Premature CTRL+C.')
    dev.close()
    qtw.QApplication.instance().quit()
