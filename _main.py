import os
import sys

if __name__ == '__main__':
    import PySide2
    import logging
    import random
    import PySide2.QtWidgets as qtw
    from PySide2.QtCore import Qt
    from hashlib import md5
    from datetime import datetime
    from embr_survey.window import MainWindow
    import embr_survey.dvs as dvs
    from embr_survey.intro_widgets import IntroDlg
    from embr_survey.embrwave import EmbrWave, DummyWave
    from embr_survey import setup_logger
    from embr_survey.common_widgets import JustText, EmbrFactory
    import atexit
    from embr_survey import app_path

    application_path = app_path()

    app = qtw.QApplication([])

    exp_start = datetime.now().strftime('%y%m%d-%H%M%S')

    intro_dlg = IntroDlg()
