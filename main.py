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

    try:
        device = EmbrWave()
        exception = None
    except Exception as e:
        exception = e
        device = DummyWave()

    atexit.register(device.close)
    # intro dialog--
    # - set participant ID
    # - set language
    # - set localization (i.e. different pics in DV5)
    #settings = intro_dlg(win)
    settings = {'id': 'test', 'language': 'en', 'locale': 'us'}
    settings['data_dir'] = os.path.join(application_path, 'data/%s' % settings['id'], '')
    settings['translation_dir'] = os.path.join(application_path, 'translations/')
    settings['locale_dir'] = os.path.join(application_path, 'locale/')
    settings['datetime_start'] = exp_start
    os.makedirs(settings['data_dir'], exist_ok=True)
    # can access logger using `my_logger = logging.getLogger('embr_survey')`
    # blocks have it built in as `self._log`
    setup_logger(settings['data_dir'], exp_start)
    # sanity check that all questions, values, images
    # are accounted for
    # + exp_start if want no chance of collision
    seed = md5(settings['id'].encode('utf-8')).hexdigest()
    random.seed(seed)
    settings['seed'] = seed

    logger = logging.getLogger('embr_survey')
    logger.info('Starting experiment for %s' % settings['id'])
    logger.info('Datetime of start (YMD-HMS): %s' % exp_start)
    logger.info('Seed: %s' % seed)
    logger.info('Language: %s' % settings['language'])
    logger.info('Locale: %s' % settings['locale'])
    logger.info('Device: %s' % device.name)

    logger.info('Device exception: %s' % exception)
    logger.info('Device ID, Firmware: %s, %s' % (device.device_id, device.firmware_version))
    logger.info('Device battery remaining: %s' % device.battery_charge)
    logger.info('----------')

    temps = random.choices([-9, -5, 5, 9], k=20)
    logger.info('Temperature progression: %s' % temps)
    # put all widgets in a list (stack)
    # each one ends up being at least a two-element list
    # [[embr_screen, dv1], [embr_screen, dv2_1, dv2_2], ...]
    start = JustText('Start by pressing the button below.')
    start.setAlignment(Qt.AlignCenter)
    ef = EmbrFactory('Please wait until the button below turns green.', device)
    dv1 = [ef.spawn(), dvs.DV01(1, device, temps[0], settings)]
    dv2 = [ef.spawn(), dvs.DV02(2, device, temps[1], settings)]
    dv3 = [ef.spawn(), dvs.DV03(3, device, temps[2], settings)]
    dv4 = [ef.spawn(), dvs.DV04(4, device, temps[3], settings)]
    dv5 = [ef.spawn(), dvs.DV05(5, device, temps[4], settings)]
    dv6 = [ef.spawn(), dvs.DV06(6, device, temps[5], settings)]
    dv7 = [ef.spawn(), dvs.DV07(7, device, temps[6], settings)]
    dv8 = [ef.spawn(), dvs.DV08(8, device, temps[7], settings)]
    dv9 = [ef.spawn(), dvs.DV09(9, device, temps[8], settings)]
    dv10 = [ef.spawn(), dvs.DV10(10, device, temps[9], settings)]
    dv11 = [ef.spawn(), dvs.DV11Part1(11, device, temps[10], settings),
            ef.spawn(), dvs.DV11Part2(11, device, temps[10], settings)]
    dv12 = [ef.spawn(), dvs.DV12(12, device, temps[11], settings)]
    dv13 = [ef.spawn(), dvs.DV13(13, device, temps[12], settings)]
    dv14 = [ef.spawn(), dvs.DV14(14, device, temps[13], settings)]
    #stack = [dv1, dv2, dv3, dv4, dv5, dv6, dv7, dv8, dv9, dv10]
    stack = [IntroDlg()]
    # shuffle around questions
    random.shuffle(stack)
    stack.insert(0, start)

    # stick the personal questionnaire at beginning or end of this stack
    # use random module

    window = MainWindow(stack)
    with device:
        app.exec_()
