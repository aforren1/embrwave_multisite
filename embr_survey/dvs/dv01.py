import random
from datetime import datetime
from embr_survey.dvs.base_dv import BaseDv
from embr_survey.question import QuestionBlock
from embr_survey.imgui_common import ok_button


class DV01SimilarityObjects(BaseDv):
    def __init__(self, win, block_num, settings):
        self.win = win
        self.settings = settings
        self.block_num = block_num
        # TODO: load from external?
        prompt = {'en': 'Next, we will present you with some pairs of objects. Please rate how similar or different they seem to you.'}
        header = {'en': ['1\nVery Different', '2', '3', '4', '5', '6\nVery Similar']}
        questions = {'en': ['whale-dolphin',
                            'white wine-red wine',
                            'bicycle-motorcycle',
                            'peach-nectarine',
                            'broccoli-zucchini',
                            'pen-pencil']}

        # get original list of
        questions_lang = list(enumerate(questions[settings['language']]))
        random.shuffle(questions_lang)

        self.qs = QuestionBlock(win, prompt[settings['language']],
                                header=header,
                                questions=questions)

    def run(self, temperature):
        # two data files-- a CSV with:
        # participant ID, block ID (dv1_blah), block number (for ordering),
        # block time start, question text, question number

        # fade in
        now = datetime.now().strftime('%y%m%d-%H%M%S')
        done = False
        while not done:
            current_answers = self.qs.update()
            no_nones = not any(ca is None for ca in current_answers)
            done = ok_button(self.win.impl.reg_font, no_nones)
            self.win.flip()
        # save data, fade out


if __name__ == '__main__':
    from embr_survey.window import ExpWindow
    win = ExpWindow()

    dv1 = DV1SimilarityObjects(win, 1, None)
    dv1.run(0)
