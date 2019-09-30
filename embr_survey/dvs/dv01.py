
from embr_survey.dvs.base_dv import SimpleDV


class DV01SimilarityObjects(SimpleDV):
    short_name = 'dv01'
    name = 'dv01_similarity_objects'


if __name__ == '__main__':
    from embr_survey.window import ExpWindow
    win = ExpWindow()

    dv1 = DV01SimilarityObjects(win, 1, {'language': 'en',
                                         'translation_dir': 'translations/'})
    dv1.run(0)
