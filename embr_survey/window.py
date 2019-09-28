import atexit
import platform
import sys

import pyglet
from pyglet import gl
import moderngl as mgl
import imgui
from embr_survey.imgui_common import ProgrammablePygletRenderer

if platform.system() == 'Darwin':
    pyglet.options['shadow_window'] = False


class ExpWindow(object):
    def __init__(self):
        self._background_color = 0.3, 0.3, 0.3, 1  # darkish gray
        config = gl.Config(depth_size=0, double_buffer=True,
                           alpha_size=8, sample_buffers=1,
                           samples=4, vsync=False,
                           major_version=3, minor_version=3)
        display = pyglet.canvas.get_display()
        screen = display.get_screens()[0]
        self._win = pyglet.window.Window(resizable=False, fullscreen=True,
                                         screen=screen, config=config,
                                         style='borderless', vsync=False)

        self._win.event(self.on_key_press)
        atexit.register(self._on_close)
        self.context = mgl.create_context(require=int('%i%i0' % (config.major_version,
                                                                 config.minor_version)))
        self.context.viewport = (0, 0, self.width, self.height)
        self.context.enable(mgl.BLEND)
        imgui.create_context()
        self.impl = ProgrammablePygletRenderer(self._win)
        self.impl.refresh_font_texture()
        imgui.new_frame()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self._on_close()
            sys.exit(1)

    def _on_close(self):
        if self._win.context:
            self._win.close()
        if hasattr(self, 'impl'):
            self.impl.shutdown()

    def flip(self):
        # we'll give flip some more responsibilities--
        # handle pyglet events, render/restart imgui things,
        # call glClear...
        self._win.switch_to()
        self._win.dispatch_events()
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        self._win.flip()
        self.context.clear(*self._background_color)
        imgui.new_frame()

    @property
    def width(self):
        return self._win.width

    @property
    def height(self):
        return self._win.height

    def close(self):
        self._on_close()


if __name__ == '__main__':
    win = ExpWindow()

    while True:
        imgui.show_demo_window()
        win.flip()
