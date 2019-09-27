from scratch_helper import win, impl, imgui, loop
from columns import CheckRow

button_row = CheckRow(task_id='a', question_number=12, count=5)


def update(dt):
    imgui.new_frame()
    imgui.set_next_window_size(win.width*0.75, win.height*0.9)
    nws = win.width*0.75, win.height*0.9
    imgui.set_next_window_position((win.width - nws[0])//2,
                                   (win.height - nws[1])//2)
    imgui.begin("Example: child region")
    imgui.text('Here is a prompt')
    for i in range(4):
        imgui.spacing()
    imgui.begin_child('q', height=nws[1]*0.8, border=True)
    imgui.text('1.')
    imgui.same_line()
    ww, wh = imgui.get_window_size()
    with imgui.istyled(imgui.STYLE_CHILD_ROUNDING, 8), imgui.istyled(imgui.STYLE_CHILD_BORDERSIZE, 3), imgui.colored(imgui.COLOR_BORDER, 0.9, 0.2, 0.2, 1):
        imgui.begin_child("region", 0, 600, border=True)
        reg_wid = imgui.get_window_content_region_width()
        imgui.begin_child('inner', reg_wid/4, 0, border=True)
        imgui.push_text_wrap_pos()
        imgui.text("""Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. """)
        imgui.pop_text_wrap_pos()
        imgui.end_child()  # end text
        imgui.same_line()
        imgui.begin_child('inner2', 3*reg_wid/4, 0, border=True)
        button_row.update()
        imgui.end_child()
        imgui.end_child()
    for i in range(4):
        imgui.spacing()
    imgui.text('2.')
    imgui.same_line()
    with imgui.istyled(imgui.STYLE_CHILD_ROUNDING, 8), imgui.istyled(imgui.STYLE_CHILD_BORDERSIZE, 3), imgui.colored(imgui.COLOR_BORDER, 0.1, 0.9, 0.2, 1):
        imgui.begin_child("region2", 0, 200, border=True)
        imgui.text("inside region")
        imgui.end_child()
    imgui.end_child()
    imgui.text("outside region")
    imgui.end()


loop(update)
