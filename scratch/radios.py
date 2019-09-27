
from scratch_helper import win, impl, imgui, loop


class _state(object):
    def __init__(self, lst=None):
        self.lst = lst

    def __setitem__(self, index, val):
        if val:
            for item in range(len(self.lst)):
                self.lst[item] = False
            self.lst[index] = bool(val)
        else:
            self.lst[index] = val

    def __getitem__(self, index):
        return self.lst[index]

    def __len__(self):
        return len(self.lst)


class ButtonRow(object):
    def __init__(self, task_id, question_number, count=4):
        # task id should be 3 digits (unique to the task)
        # question number should be less than 999
        # count is the number of options in this row
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
        for index in range(len(self.states)):
            button_id = self._ids[index]
            state = self.states[index]
            wh = imgui.get_font_size() + imgui.get_style().frame_padding[1] * 2
            if imgui.radio_button('##%s' % (button_id), state):
                self.states[index] = not self.states[index]
            imgui.next_column()


button_row = ButtonRow(task_id='a', question_number=12, count=5)
button_row2 = ButtonRow(task_id='a', question_number=13, count=5)


def update(dt):
    imgui.new_frame()
    imgui.begin('Radio row test')
    imgui.columns(5, 'test')
    imgui.set_column_offset(1, 50)
    imgui.set_column_offset(3, 100)
    button_row.update()
    imgui.new_line()
    imgui.separator()
    button_row2.update()
    imgui.end()


# loop(update)
