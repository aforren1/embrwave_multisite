from embr_survey.dvs.base_dv import BaseDv
from embr_survey.question import QuestionBlock
from embr_survey.imgui_common import ok_button


class DV1SimilarityObjects(BaseDv):
    def __init__(self, win, settings):
        self.win = win
        self.settings = settings
        # TODO: load from external
        prompt = 'Next, we will present you with some pairs of objects. Please rate how similar or different they seem to you.'
        header = ['1\nVery Different', '2', '3', '4', '5', '6\nVery Similar']
        questions = ['whale-dolphin',
                     'white wine-red wine',
                     'bicycle-motorcycle',
                     'peach-nectarine',
                     'broccoli-zucchini',
                     'pen-pencil']
        self.qs = QuestionBlock(win, prompt,
                                header=header,
                                questions=questions)

    def run(self, temperature):
        done = False
        while not done:
            current_answers = self.qs.update()
            no_nones = not any(ca is None for ca in current_answers)
            done = ok_button(self.win.impl.reg_font, no_nones)
            self.win.flip()


if __name__ == '__main__':
    from embr_survey.window import ExpWindow
    win = ExpWindow()

    dv1 = DV1SimilarityObjects(win, None)
    dv1.run(0)
