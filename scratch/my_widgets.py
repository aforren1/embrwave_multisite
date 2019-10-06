from PyQt5.QtCore import Qt
import PyQt5.QtWidgets as qtw
from functools import partial
# Multi-question questionnaire


def deal_with_toggle(group_id, button):
    print('group: %s, button: %s' % (group_id, button.checkedId()))


class MultiQuestion(qtw.QWidget):
    # TODO: logging responses
    def __init__(self, header, questions):
        super().__init__()
        grid = qtw.QGridLayout()
        for count, head in enumerate(header):
            h = qtw.QLabel(head)
            h.setAlignment(Qt.AlignCenter)
            grid.addWidget(h, 0, count + 1,
                           alignment=Qt.AlignCenter | Qt.AlignBottom)
        qbgs = []
        for i, quest in enumerate(questions):
            q = qtw.QLabel(quest)
            q.setWordWrap(True)
            q.setStyleSheet('border-radius: 8px;border: 2px solid #4A0C46;font-size:12pt;')
            q.setTextFormat(Qt.RichText)
            grid.addWidget(q, i+1, 0)
            qbg = qtw.QButtonGroup()
            qbg.buttonClicked.connect(partial(deal_with_toggle, i, qbg))
            qbgs.append(qbg)
            for count in range(len(header)):
                rad = qtw.QRadioButton()
                rad.setStyleSheet('QRadioButton::indicator{width:60px; height:60px;}')
                qbg.addButton(rad, count)
                grid.addWidget(rad, i+1, count+1, alignment=Qt.AlignCenter)

        self.qbgs = qbgs
        self.setLayout(grid)

    def save_data(self):
        # temporarily called save_data; should be something like get_responses?
        resps = [bg.checkedId() for bg in self.qbgs]
        print(resps)
        return(resps)
