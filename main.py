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
    from datetime import datetime
    from embr_survey.window import ExpWindow
    import embr_survey.dvs
    win = ExpWindow()

    # intro dialog--
    # - set participant ID
    # - set language
    # - set localization (i.e. different pics in DV5)
    settings = intro_dlg(win)
    settings['data_dir'] = os.path.join(application_path, 'data/')
    # sanity check that all questions, values, images
    # are accounted for

    exp_start = datetime.now().strftime('%y%m%d-%H%M%S')
    seed = hash(settings['id'] + exp_start)
    random.seed(seed)

    # TODO: generate all DVs
    dvs = [d(win, block_num, settings) for block_num, d in enumerate(dvs)]

    # set the order
    random.shuffle(dvs)

    # generate heat/cool levels
    temperature_levels = random.choices([-9, -5, 0, 5, 9], k=len(dvs))

    # TODO: intro text

    # run all DVs
    for dv, temp_level in zip(dvs, temperature_levels):
        # TODO please wait
        # set temperature level for next dv
        dv.run(temp_level)

    # post-questionnaire (TODO: note about also including pre-)
    post_questions(settings)
