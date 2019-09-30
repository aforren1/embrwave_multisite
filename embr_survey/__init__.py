# get this stuff out of the way so that when we create the window,
# we don't end up with programmable/fixed-function conflict
import pyglet
import OpenGL
OpenGL.ERROR_CHECKING = False
pyglet.options['debug_gl'] = False


def setup_logger(pth):
    import os
    import logging
    embr_logger = logging.getLogger('embr_survey')
    embr_logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(pth, 'log.log'))
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    embr_logger.addHandler(fh)
