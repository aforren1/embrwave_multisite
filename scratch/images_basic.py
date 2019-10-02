import moderngl as mgl
import pyglet

if True:
    from scratch_helper import win, impl, imgui, loop

# load an image
ctx = mgl.create_context()
ctx.enable(mgl.BLEND)
dv5_1 = pyglet.image.load('dv5_1.png')
texture = ctx.texture((dv5_1.width, dv5_1.height), 4, dv5_1.get_data())
w, h = 3*texture.width, 3*texture.height
center_x, center_y = win.width//2, win.height//2
w2, h2 = center_x - w//2, center_y - h//2


def update(dt):
    imgui.new_frame()
    imgui.set_next_window_size(w+20, h+20)
    imgui.set_next_window_position(w2, h2)
    imgui.begin('Testing image loading')
    ww, wh = imgui.get_window_size()

    imgui.set_cursor_pos(((ww - w) * 0.5, (wh - h) * 0.5))
    imgui.image(texture.glo, w, h, border_color=(0.4, 1, 1, 1))
    imgui.end()


loop(update)
