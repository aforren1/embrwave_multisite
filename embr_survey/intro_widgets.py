import logging
import os
from collections import Counter
from functools import partial
from glob import glob

import PySide2.QtWidgets as qtw
from embr_survey import app_path
from embr_survey.common_widgets import JustText
from pip._vendor import pytoml as toml
from pkg_resources import resource_filename
from PySide2.QtCore import Qt, QTimer
from embr_survey.embrwave import PreEmbr, DummyPreEmbr
from embr_survey.pygatt.exceptions import NotConnectedError

application_path = app_path()


def count_language_keys(files, ref):
    # must have *all* language keys to work (otherwise, ignore)
    total_keys = []
    final_round = []
    languages = []  # final product (list of languages)
    for tf in files:
        with open(tf, 'r') as f:
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
        with open(tf, 'r') as f:
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
    new_lang = self.lang.currentText()
    self.id_label.setText(self.translations['participant'][new_lang])
    self.lang_label.setText(self.translations['language'][new_lang])
    self.locale_label.setText(self.translations['locale'][new_lang])


def on_blink(sel):
    dev = sel.device.currentText()
    if dev:
        sel.pre_embr.blink(sel.device.currentText())
    sel.pre_embr.scan()
    # sel.device.clear() # TODO: why was this here?


class IntroDlg(qtw.QWidget):
    _log = logging.getLogger('embr_survey')
    auto_continue = True  # control whether button auto-enabled

    def __init__(self):
        super().__init__()

        try:
            self.pre_embr = PreEmbr()
        except NotConnectedError:
            # no adapter, so no devices
            # TODO: log failure (though should be obvious?)
            self.pre_embr = DummyPreEmbr()
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
        with open(translation_path, 'r') as f:
            self.translations = toml.load(f)

        # widgets and layout
        layout = qtw.QGridLayout()

        self.id = qtw.QLineEdit()
        self.lang = qtw.QComboBox()
        self.lang.currentIndexChanged.connect(partial(on_activated, self))
        self.locale = qtw.QComboBox()
        self.device = qtw.QComboBox()
        self.device.addItems(self.pre_embr.addrs)

        # TODO: these *also* need to be translated...
        self.id_label = JustText(self.translations['participant']['en'])
        self.lang_label = JustText(self.translations['language']['en'])
        self.locale_label = JustText(self.translations['locale']['en'])
        self.device_label = JustText('Embr Wave ID')

        # default to english/us, which *should* exist & be complete
        self.lang.addItems(languages)
        self.lang.setCurrentText('en')
        self.locale.addItems(locales)
        self.locale.setCurrentText('us')

        self.blinker = qtw.QPushButton()
        self.blinker.clicked.connect(partial(on_blink, self))

        layout.addWidget(self.id_label, 0, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.id, 0, 1, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.lang_label, 1, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.lang, 1, 1, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.locale_label, 2, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.locale, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.device_label, 3, 0, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.device, 3, 1, Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.blinker, 3, 2, Qt.AlignLeft | Qt.AlignVCenter)

        self.setLayout(layout)

    # TODO: on exit, should do everything currently done in main-- adding widgets to the stack
    # with proper settings,
    def all_ans(self):
        return self.id.text() != ''
