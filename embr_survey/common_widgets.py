from PySide2.QtCore import Qt, QTimer
import PySide2.QtWidgets as qtw
from functools import partial
import logging
from pkg_resources import resource_filename
# Multi-question questionnaire

no_ans = '''
border-radius: 10px;background-color: #ffa7a1;font-size:18pt;padding:5px;
'''

ans = '''
border-radius: 10px;background-color: #a1ffb2;font-size:18pt;padding:5px;
'''

log = logging.getLogger('embr_survey')


def deal_with_toggle(group_id, button_grp, q_text, button):
    log.info('Button %s in group %s (question: %s) pressed.' % (button_grp.checkedId(),
                                                                group_id,
                                                                q_text.text()))
    q_text.setStyleSheet(ans)


class SpecialStack(qtw.QStackedWidget):
    def sizeHint(self):
        if self.count() > 0:
            return self.currentWidget().sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        if self.count() > 0:
            return self.currentWidget().minimumSizeHint()
        return super().minimumSizeHint()


class JustText(qtw.QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet('font-size:20pt;')
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)  # allow HTML


class EmbrFactory(object):
    def __init__(self, text, device):
        self.device = device
        self.text = text

    def spawn(self):
        return EmbrSection(self.text, self.device)


class EmbrSection(JustText):
    auto_continue = False

    def __init__(self, text, device):
        super().__init__(text)
        self.device = device
        self.setAlignment(Qt.AlignCenter)

    def on_enter(self):
        # button ref is injected
        log.info('Entering neutral EmbrWave section & disabling "next" for 5 seconds.')
        self._button.state = 'neutral'
        QTimer.singleShot(5000, self._enable)
        self.device.stop()

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
            q = qtw.QLabel()
            q.setWordWrap(True)
            q.setStyleSheet(no_ans)
            q.setTextFormat(Qt.RichText)
            q.setText(quest)
            grid.addWidget(q, i+1, 0)
            qbg = qtw.QButtonGroup()
            qbg.buttonClicked.connect(partial(deal_with_toggle, i, qbg, q))
            qbgs.append(qbg)
            chk_pth = resource_filename('embr_survey', 'images/radio_checked.png')
            unchk_pth = resource_filename('embr_survey', 'images/radio_unchecked.png')
            chk_pth = chk_pth.replace('\\', '/')
            unchk_pth = unchk_pth.replace('\\', '/')
            style = 'QRadioButton::indicator{width:80px; height:80px; image:url(%s);} QRadioButton::indicator::checked{image:url(%s);}' % (unchk_pth, chk_pth)
            for count in range(len(header)):
                rad = qtw.QRadioButton()
                rad.setStyleSheet(style)
                qbg.addButton(rad, count)
                grid.addWidget(rad, i+1, count+1, alignment=Qt.AlignCenter)

        self.qbgs = qbgs
        self.setLayout(grid)

    def get_responses(self):
        resps = [bg.checkedId() + 1 for bg in self.qbgs]
        return resps


class SingleQuestion(MultiQuestion):
    def __init__(self, header, question):
        super().__init__(header, [question])
