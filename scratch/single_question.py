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


class QuestionRegion(object):
    # question region consists of:
    # - a prompt (potentially a big block of text)
    # - A header for the survey block (informs how many responses are possible)
    # - A list of questions

    def __init__(self, prompt, header, questions):
