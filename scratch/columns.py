
from radios import _state, loop, imgui


class CheckRow(object):
    def __init__(self, task_id, question_number, count=4):
        task_id = str(task_id)
        question_number = str(question_number)
        if len(task_id) > 3:
            raise ValueError('Task ID should be no more than 3 digits')
        if len(question_number) > 3:
            raise ValueError('Question number should be no more than 3 digits')
        task_id = task_id.zfill(3)
        question_number = question_number.zfill(3)

        self._ids = []
        for i in range(count):
            self._ids.append((('%s%s%s') % (task_id, question_number, i)))
        self.states = _state([False] * count)

    def update(self):
        ccp = imgui.get_window_content_region_width()
        style = imgui.get_style()
        imgui.set_window_font_scale(5)
        wh = imgui.get_font_size() + imgui.get_style().frame_padding[0] * 2
        foo = [0.1, 0.3, 0.5, 0.7, 0.9]
        for index in range(len(self.states)):
            # not *totally* sure why the next line works
            imgui.same_line(position=foo[index]*ccp - 0.4*wh)
            button_id = self._ids[index]
            state = self.states[index]
            _, enabled = imgui.checkbox('##%s' % button_id, state)
            self.states[index] = enabled

        # imgui.same_line(spacing=1/12)
        # imgui.new_line()
        print(self.states[:])
        imgui.set_window_font_scale(1)


button_row = CheckRow(task_id='a', question_number=12, count=5)
button_row2 = CheckRow(task_id='a', question_number=13, count=5)


def update(dt):
    imgui.new_frame()
    imgui.set_next_window_size(900, 600)
    imgui.begin('Check row test')
    imgui.separator()
    for i in range(5):
        imgui.spacing()
    button_row.update()
    imgui.new_line()
    imgui.separator()
    for i in range(5):
        imgui.spacing()
    button_row2.update()
    imgui.end()


# loop(update)
