
import imgui
import logging


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
        self.states = [_state([False] * len(header)) for i in range(len(questions))]
        self.id = hash(''.join(questions) + ''.join(header))
        self._log = logging.getLogger('embr_survey')

    def update(self):
        # get current width
        total_wid = imgui.get_window_width() * 0.95
        text_wid = total_wid//4
        rest_wid = (3 * total_wid)//4
        ncol = len(self.header)
        sub_wid = rest_wid // ncol

        # prompt text
        imgui.begin_child('##title%s' % self.id, total_wid, height=160)
        with imgui.font(self.win.impl.bold_font):
            imgui.push_text_wrap_pos(total_wid//2)
            imgui.text(self.prompt)
            imgui.pop_text_wrap_pos()
        imgui.end_child()

        # add header
        header_height = 120
        imgui.begin_child('##header%s' % self.id, total_wid, height=header_height)
        with imgui.font(self.win.impl.reg_font):
            # TODO: may need to uniquely identify this?
            imgui.begin_child('##space%s' % self.id, width=text_wid - sub_wid//2,
                              height=header_height, border=True)
            imgui.end_child()
            imgui.same_line()
            for count, head in enumerate(self.header):
                imgui.begin_child('##%s%s%s' % (count, head, self.id),
                                  height=header_height, width=sub_wid, border=True)
                imgui.set_window_font_scale(0.8)
                imgui.push_text_wrap_pos()
                imgui.text(head)
                imgui.pop_text_wrap_pos()
                imgui.set_window_font_scale(1)
                imgui.end_child()
                imgui.same_line()
            imgui.new_line()
        imgui.end_child()

        # add checkboxes
        q_chk_height = 100
        hei = imgui.get_window_height()
        imgui.begin_child('##ans%s' % self.id, total_wid, height=q_chk_height*len(self.questions)*1.1)
        if imgui.is_window_hovered():
            imgui.set_scroll_y(imgui.get_scroll_y() -
                               imgui.get_io().mouse_wheel * 30)
        with imgui.font(self.win.impl.reg_font):
            for count, question in enumerate(self.questions):
                # question first (change color border)
                if any(self.states[count]):
                    col = 0.2, 0.9, 0.3, 1
                else:  # no answer
                    col = 0.9, 0.3, 0.2, 1
                imgui.push_style_color(imgui.COLOR_BORDER, *col)
                imgui.begin_child('##%s%stext%s' % (count, question, self.id),
                                  width=text_wid - sub_wid//2, height=q_chk_height,
                                  border=True, flags=imgui.WINDOW_NO_SCROLL_WITH_MOUSE)
                imgui.push_text_wrap_pos()
                imgui.set_window_font_scale(0.75)
                imgui.text(question)
                imgui.set_window_font_scale(1)
                imgui.pop_text_wrap_pos()
                imgui.end_child()  # end question
                imgui.same_line()
                # checkboxes
                for i in range(ncol):
                    tmp = '##%s%s%s%s' % (count, question, i, self.id)
                    imgui.begin_child(tmp,
                                      width=sub_wid, height=q_chk_height, flags=imgui.WINDOW_NO_SCROLL_WITH_MOUSE)
                    imgui.set_window_font_scale(2)
                    # try to center in child
                    font_height = imgui.get_text_line_height_with_spacing()
                    imgui.same_line(position=font_height//2)
                    _, enabled = imgui.checkbox(tmp + 'chk',
                                                self.states[count][i])
                    if enabled and not self.states[count][i]:
                        self._log.info('Question %i (%s), element %i selected' % (count, question, i))
                    elif not enabled and self.states[count][i]:
                        self._log.info('Question %i (%s), element %i deselected' % (count, question, i))
                    imgui.set_window_font_scale(1)
                    self.states[count][i] = enabled
                    imgui.end_child()  # end checkbox
                    imgui.same_line()
                imgui.pop_style_color(1)
                imgui.new_line()
        imgui.end_child()

        # return current state
        ans = []
        for state in self.states:
            try:
                # add one to match scoring (generally)
                ans.append(state.index(True) + 1)
            except ValueError:  # no Trues
                ans.append(None)
        return ans


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

    def index(self, val):
        return self.lst.index(val)


if __name__ == '__main__':
    from embr_survey.window import ExpWindow as Win
    from embr_survey.imgui_common import ok_button

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
                 'What is your favorite color?',
                 'What else is your favourite color?',
                 'It should be blue.']
    question_block = QuestionBlock(win, prompt=prompt,
                                   header=header,
                                   questions=questions)

    header2 = ['1', '2', '3']
    questions2 = ['Question 1', 'Question2', 'Question3']

    q2 = QuestionBlock(win, prompt='fooooo', header=header2, questions=questions2)

    done = False
    while not done:
        imgui.begin_child('foob')
        current_ans = question_block.update()
        q2.update()
        # print(current_ans)
        cat = not any(ca is None for ca in current_ans)
        done = ok_button(win.impl.reg_font, cat)
        imgui.end_child()
        win.flip()
