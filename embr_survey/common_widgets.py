from PySide2.QtCore import Qt, QTimer
import PySide2.QtWidgets as qtw
from functools import partial
import logging
# Multi-question questionnaire

no_ans = '''
border-radius: 10px;background-color: #ffa7a1;font-size:18pt;padding:5px;
'''

ans = '''
border-radius: 10px;background-color: #a1ffb2;font-size:18pt;padding:5px;
'''

log = logging.getLogger('embr_survey')


def deal_with_toggle(group_id, button, q_text):
    log.info('Button %s in group %s (question: %s) pressed.' % (button.checkedId(),
                                                                group_id,
                                                                q_text.text()))
    q_text.setStyleSheet(ans)


class SpecialStack(qtw.QStackedWidget):
    def sizeHint(self):
        return self.currentWidget().sizeHint()

    def minimumSizeHint(self):
        return self.currentWidget().minimumSizeHint()


class JustText(qtw.QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet('font-size:20pt;')
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)  # allow HTML


class EmbrFactory(object):
    def __init__(self, text, device):
        self.dev = device
        self.text = text

    def spawn(self):
        return EmbrSection(self.text, self.dev)


class EmbrSection(JustText):
    auto_continue = False

    def __init__(self, text, device):
        super().__init__(text)
        self.dev = device
        self.setAlignment(Qt.AlignCenter)

    def on_enter(self):
        # button ref is injected
        log.info('Entering neutral EmbrWave section & disabling "next" for 5 seconds.')
        self._button.state = 'neutral'
        QTimer.singleShot(5000, self._enable)
        self.dev.stop()

    def _enable(self):
        self._button.state = 'complete'


class MultiQuestion(qtw.QWidget):
    # TODO: logging responses
    def __init__(self, header, questions):
        super().__init__()
        grid = qtw.QGridLayout()
        for count, head in enumerate(header):
            h = qtw.QLabel(head)
            h.setStyleSheet('font-size:18pt;')
            h.setAlignment(Qt.AlignCenter)
            grid.addWidget(h, 0, count + 1,
                           alignment=Qt.AlignCenter | Qt.AlignBottom)
        qbgs = []
        for i, quest in enumerate(questions):
            q = qtw.QLabel(quest)
            q.setWordWrap(True)
            q.setStyleSheet(no_ans)
            q.setTextFormat(Qt.RichText)
            grid.addWidget(q, i+1, 0)
            qbg = qtw.QButtonGroup()
            qbg.buttonClicked.connect(partial(deal_with_toggle, i, qbg, q))
            qbgs.append(qbg)
            for count in range(len(header)):
                rad = qtw.QRadioButton()
                rad.setStyleSheet('QRadioButton::indicator{width:60px; height:60px;}')
                qbg.addButton(rad, count)
                grid.addWidget(rad, i+1, count+1, alignment=Qt.AlignCenter)

        self.qbgs = qbgs
        self.setLayout(grid)

    def get_responses(self):
        resps = [bg.checkedId() for bg in self.qbgs]
        return resps


class SingleQuestion(MultiQuestion):
    def __init__(self, header, question):
        super().__init__(header, [question])
