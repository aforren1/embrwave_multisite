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


class Question(object):
    def __init__(self, task_id, question_number, question_txt, n_answers):
        task_id = str(task_id)
        question_number = str(question_number)
        self._ids = []
        for i in range(n_answers):
            self._ids.append((('%s%s%s') % (task_id, question_number, i)))
        self.states = _state([False] * n_answers)

    def draw(self):
        # current idea:
        # make a new child window to contain buttons & text
        #
        # need to calculate the height of text
        pass
