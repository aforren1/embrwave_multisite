
import imgui


class QuestionBlock(object):
    # question region consists of:
    # - a prompt (potentially a big block of text)
    # - A header for the survey block (informs how many responses are possible)
    # - A list of questions
    def __init__(self, win, prompt, header, questions):
        self.win = win
        self.prompt = prompt
        self.header = header
        self.questions = questions
        self.states = [_state([False] * len(header)) for i in len(questions)]

    def update(self):
        #
        with imgui.font(self.win.impl.bold_font):
            imgui.push_text_wrap_pos(0)
            imgui.text(self.prompt)
            imgui.pop_text_wrap_pos()

        # get current width
        total_wid = imgui.get_window_width()

        # add columns
        with imgui.font(self.win.impl.reg_font):
            imgui.set_window_font_scale(0.75)
            imgui.spacing()
            rest_width = (2 * total_wid)//3
            num_headers = len(self.header)
            sub_width = rest_width // num_headers
            imgui.columns(num_headers+1)  # add one for padding
            imgui.set_column_offset(-1, total_wid//3 - 2*sub_width)
            imgui.next_column()
            imgui.push_text_wrap_pos(0)
            for count, head in enumerate(self.header):
                imgui.set_column_width(count, sub_width)
                imgui.text(head)
                if count < num_headers:
                    imgui.next_column()
            imgui.pop_text_wrap_pos()
            imgui.set_window_font_scale(1)

            imgui.columns(1)
            # add questions (leaving room for OK button)
            imgui.begin_child('foo', height=-120)
            for count, question in enumerate(self.questions):
                imgui.begin_child('##%s%s' % (count, question),
                                  height=150, width=total_wid//3 - 2*sub_width)
                imgui.push_text_wrap_pos()
                imgui.text('%s. %s' % (count+1, question))
                imgui.pop_text_wrap_pos()
                imgui.end_child()
                imgui.same_line()
                imgui.begin_child('##%s%s2' % (count, question),
                                  height=150, width=0)
                imgui.end_child()

            imgui.end_child()


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


if __name__ == '__main__':
    from embr_survey.window import ExpWindow as Win

    win = Win()

    prompt = """
This is a long question block.
Here are more lines.
Words and things
    """
    header = ['1\nLeast interested', '2', '3', '4\nHalfway interested', '5', '6', '7\nVery interested']

    # in the "real" thing, this will be drawn from a dict, e.g.
    # questions = question['en']
    questions = ['What is your name?',
                 'What is your quest?',
                 'What is your favorite color?']
    question_block = QuestionBlock(win, prompt=prompt,
                                   header=header,
                                   questions=questions)

    while True:
        current_ans = question_block.update()
        win.flip()
