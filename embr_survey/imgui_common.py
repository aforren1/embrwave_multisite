import imgui
from imgui.integrations import compute_fb_scale
from imgui.integrations.opengl import ProgrammablePipelineRenderer
from imgui.integrations.pyglet import PygletMixin, PygletRenderer
from pkg_resources import resource_filename
from pyglet import gl


class ProgrammablePygletRenderer(PygletMixin, ProgrammablePipelineRenderer):
    def __init__(self, window, attach_callbacks=True):
        super().__init__()
        window_size = window.get_size()
        viewport_size = window.get_viewport_size()

        io = imgui.get_io()

        io.display_size = window_size
        io.display_fb_scale = compute_fb_scale(window_size, viewport_size)

        # pick something relatively large so we don't have
        font_size_pix = 32
        font_scale_factor = 1.0
        font_size = font_size_pix * font_scale_factor

        ubuntu_mono_b = resource_filename('embr_survey', 'fonts/UbuntuMono-B.ttf')
        ubuntu_mono_r = resource_filename('embr_survey', 'fonts/UbuntuMono-R.ttf')
        self.reg_font = io.fonts.add_font_from_file_ttf(ubuntu_mono_r, font_size)
        self.bold_font = io.fonts.add_font_from_file_ttf(ubuntu_mono_b, font_size)
        # TODO try to scale fonts in high DPI situations
        io.font_global_scale /= font_scale_factor

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
