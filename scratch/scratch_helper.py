import sys
import pyglet
import OpenGL
OpenGL.ERROR_CHECKING = False
pyglet.options['debug_gl'] = False
if True:
    from pyglet import gl
    import imgui
    from imgui.integrations.pyglet import PygletRenderer

    from imgui.integrations import compute_fb_scale

    from imgui.integrations.pyglet import PygletMixin
    from imgui.integrations.opengl import ProgrammablePipelineRenderer


class ProgrammablePygletRenderer(PygletMixin, ProgrammablePipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super(ProgrammablePygletRenderer, self).__init__()
        window_size = window.get_size()
        viewport_size = window.get_viewport_size()

        self.io.display_size = window_size
        self.io.display_fb_scale = compute_fb_scale(window_size, viewport_size)
        # try to scale fonts in high DPI situations
        self.io.font_global_scale = 1.0/self.io.display_fb_scale[0]

        self._map_keys()

        if attach_callbacks:
            window.push_handlers(
                self.on_mouse_motion,
                self.on_key_press,
                self.on_key_release,
                self.on_text,
                self.on_mouse_drag,
                self.on_mouse_press,
                self.on_mouse_release,
                self.on_mouse_scroll,
                self.on_resize,
            )


config = gl.Config(depth_size=0, double_buffer=True,
                   alpha_size=8, sample_buffers=1,
                   samples=4, vsync=False,
                   major_version=3, minor_version=3)
display = pyglet.canvas.get_display()
screen = display.get_screens()[0]
win = pyglet.window.Window(resizable=False, fullscreen=True,
                           screen=screen, config=config,
                           style='borderless', vsync=True)
gl.glClearColor(0.5, 0.5, 0.5, 1)
imgui.create_context()
impl = ProgrammablePygletRenderer(win)


@win.event
def on_draw():
    win.clear()
    imgui.render()
    impl.render(imgui.get_draw_data())


def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        impl.shutdown()
        sys.exit(0)


win.event(on_key_press)


def loop(update):
    while True:
        pyglet.clock.tick()
        win.switch_to()
        win.dispatch_events()
        update(1/60)
        win.dispatch_event('on_draw')
        win.flip()
