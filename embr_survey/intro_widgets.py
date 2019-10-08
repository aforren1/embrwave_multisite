import os
from PyQt5.QtCore import Qt, QTimer
import PyQt5.QtWidgets as qtw
from functools import partial
import logging
from pkg_resources import resource_filename
from embr_survey import app_path
from glob import glob
from pip._vendor import pytoml as toml
from collections import Counter
application_path = app_path()


def count_keys(files, ref):
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
        # number of occurrence (en as reference)
        counts = Counter(total_keys)
        count_en = counts['en']
        for lang in counts:
            if counts[lang] == count_en:
                final_round.append(lang)

    final_c = Counter(final_round)
    count_en = final_c['en']
    for lang in final_c:
        if final_c[lang] == count_en:
            languages.append(lang)
    return languages


class IntroDlg(qtw.QWidget):
    _log = logging.getLogger('embr_survey')
    auto_continue = True  # control whether button auto-enabled

    def __init__(self):
        super().__init__()

        # id, language, locale
        self.settings = {}
        self.settings['translation_dir'] = os.path.join(application_path, 'translations/')
        self.settings['locale_dir'] = os.path.join(application_path, 'locale/')
        # check all translation files, and list only complete ones

        translation_files = glob(os.path.join(self.settings['translation_dir'], 'd*.toml'))

        # figure out complete translations, using english as ref
        languages = count_keys(translation_files, 'en')
        # now same with localization
        locale_files = glob(os.path.join(self.settings['locale_dir'], 'd*.toml'))
        locales = count_keys(locale_files, 'eu')
