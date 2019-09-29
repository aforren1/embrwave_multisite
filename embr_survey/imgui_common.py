import imgui
from imgui.integrations import compute_fb_scale
from imgui.integrations.opengl import ProgrammablePipelineRenderer
from imgui.integrations.pyglet import PygletMixin, PygletRenderer
from pkg_resources import resource_filename
from pyglet import gl
from timeit import default_timer


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


def ok_button(font, sure):
    imgui.new_line()
    imgui.same_line(imgui.get_window_width() - 200)
    ans = False
    if sure:
        colo = 0.2, 0.9, 0.2
        hover_color = 0.2, 0.6, 0.2
    else:
        colo = 0.7, 0.7, 0.3
        hover_color = 0.8, 0.5, 0.3
    with imgui.istyled(imgui.STYLE_BUTTON_TEXT_ALIGN, (0.5, 0.5),
                       imgui.STYLE_FRAME_ROUNDING, 6, imgui.STYLE_FRAME_BORDERSIZE, 4), imgui.colored(imgui.COLOR_BUTTON, *colo), imgui.colored(imgui.COLOR_BORDER, 0.1, 0.5, 0.2), imgui.colored(imgui.COLOR_TEXT, 1, 1, 1), imgui.colored(imgui.COLOR_BUTTON_HOVERED, *hover_color):
        with imgui.font(font):
            imgui.set_window_font_scale(2)
            if imgui.button('Next'):
                if not sure:
                    imgui.open_popup('sure?')
                else:
                    ans = True

            if imgui.begin_popup_modal('sure?')[0]:
                if imgui.button('OK'):
                    ans = True
                    imgui.close_current_popup()
                imgui.same_line()
                if imgui.button('Back'):
                    imgui.close_current_popup()
                imgui.end_popup()

            imgui.set_window_font_scale(1)

    return ans
