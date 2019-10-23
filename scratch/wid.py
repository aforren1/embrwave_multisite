import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from pkg_resources import resource_filename


class JustText(qtw.QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet('font-size:20pt;')
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)  # allow HTML


class RadioGroupQ(qtw.QWidget):
    def __init__(self, question, answers):
        super().__init__()
        q_txt = JustText(question)
        self.resp = qtw.QButtonGroup()
        chk_pth = resource_filename('embr_survey', 'images/radio_checked.png')
        unchk_pth = resource_filename('embr_survey', 'images/radio_unchecked.png')
        chk_pth = chk_pth.replace('\\', '/')
        unchk_pth = unchk_pth.replace('\\', '/')
        style = 'QRadioButton::indicator{width:60px; height:60px; image:url(%s);} QRadioButton::indicator::checked{image:url(%s);};' % (unchk_pth, chk_pth)
        self.resp = qtw.QButtonGroup()
        layout = qtw.QVBoxLayout()
        # add question to stretch across top
        layout.addWidget(q_txt)
        for count in range(len(answers)):
            rad = qtw.QRadioButton()
            fnt = rad.font()
            fnt.setPointSize(26)
            rad.setFont(fnt)
            rad.setText(answers[count])
            rad.setStyleSheet(style)
            self.resp.addButton(rad)
            layout.addWidget(rad)

        self.setLayout(layout)

class ConditionalWidget(qtw.QWidget):
    # pair of widgets-- one "main" question, one hidden one
    def __init__(self, main_widget, hidden_widget, valid):
        super().__init__()
        self.main_widget = main_widget
        self.valid = valid
        main_widget.resp.buttonClicked.connect(self.check_valid)
        self.hidden_widget = hidden_widget
        self.hidden_widget.setHidden(True)  # hide until resp
        layout = qtw.QVBoxLayout()
        layout.addWidget(self.main_widget)
        layout.addWidget(self.hidden_widget)
        self.setLayout(layout)
        self.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Expanding)
    
    def check_valid(self):
        val = self.main_widget.resp.checkedButton().text()
        print(val)
        if val in self.valid:
            self.hidden_widget.setHidden(False)
        else:
            self.hidden_widget.setHidden(True)
        self.parentWidget().parentWidget().adjustSize()


if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    from embr_survey.window import MainWindow

    app = QApplication([])
    intro_dlg = RadioGroupQ('What is your name?', ['0', '1', '2', '3', '4', '5', '6', '7+'])
    optional = RadioGroupQ('What is your quest?', ['Grail', 'Jelly Doughnut'])
    # note to self: need at least one widget to start
    # (though this is probably pretty easy to resolve)
    both = ConditionalWidget(intro_dlg, optional, valid = ['1', '2', '3', '4', '5', '6', '7+'])

    foob = RadioGroupQ('What is your favorite number?', ['A', 'B', 'C'])
    opt2 = RadioGroupQ('Are you sure?', ['Yes', 'No'])
    both2 = ConditionalWidget(foob, opt2, valid=['C'])
    combo = qtw.QWidget()
    layout = qtw.QVBoxLayout()
    layout.addWidget(both)
    layout.addWidget(both2)
    combo.setLayout(layout)
    window = MainWindow([combo])
    # all of the work is done by on_exit
    # of the IntroDlg
    # main loop
    app.exec_()
