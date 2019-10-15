import atexit
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
from embr_survey.embrwave import EmbrWave, DummyWave


class ConnectDevice(qtw.QWidget):
    _log = logging.getLogger('embr_survey')
    auto_continue = True

    def __init__(self, settings):
        super().__init__()
        self._settings = settings
        # need to try to connect to the device,
        # TODO: layout
        layout = qtw.QVBoxLayout()
        self.addr = settings['device_addr']
        lang = settings['language']
        translation_path = os.path.join(settings['translation_dir'], 'misc.toml')
        with open(translation_path, 'r') as f:
            self.translations = toml.load(f)
        txt = JustText(self.translations['connect_device'][lang])
        self.connect_text = JustText(self.translations['is_connected'][lang])
        self.connect_text.setStyleSheet('color: red;')
        self._is_connected = False

        layout.addWidget(txt)
        layout.addWidget(self.connect_text)
        self.setLayout(layout)

        # every second, try to connect to the device
        # if successful, continue immediately
        # if failure, feed in DummyWave
        self.device = DummyWave()
        self.timer = QTimer()
        self.timer.timeout.connect(self.try_connect_device)
        self.timer.start(1000)

    def try_connect_device(self):
        #
        try:
            # connect to the device
            if not self._is_connected:
                self.timer.stop()
                device = EmbrWave(self.addr)
                atexit.register(device.close)
                self._log.info('Device: %s' % device.name)
                self._log.info('Device ID, Firmware: %s, %s' % (device.device_id, device.firmware_version))
                self._log.info('Device battery remaining: %s' % device.battery_charge)
                self._log.info('----------')
                self.connect_text.setStyleSheet('color: green;')
                self._is_connected = True
        except Exception as e:
            self._log.warn(e)
            self.timer.start(1000)

    def all_ans(self):
        return self._is_connected

    def on_exit(self):
        import random
        from embr_survey.common_widgets import EmbrFactory
        import embr_survey.dvs as dvs
        # finally good to go

        temps = random.choices([-9, -5, 5, 9], k=14)
        dv_order = list(range(14))
        random.shuffle(dv_order)
        temps = [temps[val] for val in dv_order]
        self._log.info('Temperature progression: %s' % temps)

        # TODO: feed in locale
        device = self.device
        settings = self._settings
        lang = settings['language']
        ef = EmbrFactory(self.translations['wait_until_green'][lang], device)
        dv1 = [ef.spawn(), dvs.DV01(dv_order[0], device, temps[0], settings)]
        dv2 = [ef.spawn(), dvs.DV02(dv_order[1], device, temps[1], settings)]
        dv3 = [ef.spawn(), dvs.DV03(dv_order[2], device, temps[2], settings)]
        dv4 = [ef.spawn(), dvs.DV04(dv_order[3], device, temps[3], settings)]
        dv5 = [ef.spawn(), dvs.DV05(dv_order[4], device, temps[4], settings)]
        dv6 = [ef.spawn(), dvs.DV06(dv_order[5], device, temps[5], settings)]
        dv7 = [ef.spawn(), dvs.DV07(dv_order[6], device, temps[6], settings)]
        dv8 = [ef.spawn(), dvs.DV08(dv_order[7], device, temps[7], settings)]
        dv9 = [ef.spawn(), dvs.DV09(dv_order[8], device, temps[8], settings)]
        dv10 = [ef.spawn(), dvs.DV10(dv_order[9], device, temps[9], settings)]
        dv11 = [ef.spawn(), dvs.DV11Part1(dv_order[10], device, temps[10], settings),
                ef.spawn(), dvs.DV11Part2(dv_order[10], device, temps[10], settings)]
        dv12 = [ef.spawn(), dvs.DV12(dv_order[11], device, temps[11], settings)]
        dv13 = [ef.spawn(), dvs.DV13(dv_order[12], device, temps[12], settings)]
        dv14 = [ef.spawn(), dvs.DV14(dv_order[13], device, temps[13], settings)]
        stack = [dv1, dv2, dv3, dv4, dv5,
                 dv6, dv7, dv8, dv9, dv10,
                 dv11, dv12, dv13, dv14]
        # shuffle around questions
        stack2 = [stack[i] for i in dv_order]
        self._window.add_widgets(stack2[:2])
