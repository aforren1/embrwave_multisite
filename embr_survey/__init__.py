# get this stuff out of the way so that when we create the window,
# we don't end up with programmable/fixed-function conflict
import pyglet
import OpenGL
OpenGL.ERROR_CHECKING = False
pyglet.options['debug_gl'] = False
