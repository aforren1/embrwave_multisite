import os
import sys

# figure out if we're a script or exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
else:
    raise ValueError('No idea if this is running as a script or under pyinstaller!')


if __name__ == '__main__':
    import random
    from hashlib import md5
    from datetime import datetime
    from embr_survey.window import ExpWindow
    import embr_survey.dvs as dvs
    from embr_survey import setup_logger
    import logging

    exp_start = datetime.now().strftime('%y%m%d-%H%M%S')
    win = ExpWindow()

    # intro dialog--
    # - set participant ID
    # - set language
    # - set localization (i.e. different pics in DV5)
    #settings = intro_dlg(win)
    settings = {'id': 'test', 'language': 'en', 'locale': 'us'}
    settings['data_dir'] = os.path.join(application_path, 'data/%s' % settings['id'], '')
    settings['translation_dir'] = os.path.join(application_path, 'translations/')
    settings['datetime_start'] = exp_start
    os.makedirs(settings['data_dir'], exist_ok=True)
    # can access logger using `my_logger = logging.getLogger('embr_survey')`
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
    logger.info('----------')

    # TODO: generate all DVs
    dvs = [getattr(dvs, d) for d in dir(dvs) if d.startswith('DV')]
    dvs = [d(win, block_num, settings) for block_num, d in enumerate(dvs)]

    # set the order
    random.shuffle(dvs)

    # generate heat/cool levels
    temperature_levels = random.choices([-9, -5, 0, 5, 9], k=len(dvs))

    # TODO: intro text

    # run all DVs
    for dv, temp_level in zip(dvs, temperature_levels):
        # TODO please wait
        logger.info('Setting Embr Wave temperature to %i' % temp_level)
        # set temperature level for next dv
        dv.run(temp_level)

    # post-questionnaire (TODO: note about also including pre-)
    # post_questions(settings)
