import PySide2.QtWidgets as qtw
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QIntValidator
from pkg_resources import resource_filename

no_ans = '''
border-radius: 10px;background-color: #ffa7a1;font-size:18pt;padding:5px;
'''

ans = '''
border-radius: 10px;background-color: #a1ffb2;font-size:18pt;padding:5px;
'''


class JustText(qtw.QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet('font-size:20pt;')
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)  # allow HTML

class DropDownQuestion(qtw.QWidget):
    def __init__(self, question, answers):
        super().__init__()
        layout = qtw.QHBoxLayout()
        q = JustText(question)
        self.answer = qtw.QComboBox()
        fnt = self.answer.font()
        fnt.setPointSize(26)
        self.answer.setFont(fnt)
        self.answer.addItems(answers)
        self._default_ans = answers[0]
        layout.addWidget(q, Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.answer, Qt.AlignLeft | Qt.AlignCenter)
        self.setLayout(layout)

    def get_responses(self):
        return self.answer.currentText()

class RadioGroupQ(qtw.QWidget):
    def __init__(self, question, answers):
        super().__init__()
        q_txt = JustText(question)
        q_txt.setStyleSheet(no_ans)
        self.resp = qtw.QButtonGroup()
        chk_pth = resource_filename('embr_survey', 'images/radio_checked.png')
        unchk_pth = resource_filename('embr_survey', 'images/radio_unchecked.png')
        chk_pth = chk_pth.replace('\\', '/')
        unchk_pth = unchk_pth.replace('\\', '/')
        style = 'QRadioButton::indicator{width:60px; height:60px; image:url(%s);} QRadioButton::indicator::checked{image:url(%s);};' % (unchk_pth, chk_pth)
        self.resp = qtw.QButtonGroup()
        self.resp.buttonClicked.connect(self.grn_txt)
        self.q_txt = q_txt
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
    
    def grn_txt(self):
        self.q_txt.setStyleSheet(ans)
    
    def get_responses(self):
        return self.resp.checkedId() + 1

class ConditionalWidget(qtw.QWidget):
    # pair of widgets-- one "main" question, one hidden one
    # first one is always a QButtonGroup
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
        if val in self.valid:
            self.hidden_widget.setHidden(False)
        else:
            self.hidden_widget.setHidden(True)
        self.parentWidget().parentWidget().adjustSize()
    
    # if not in valid range, return initial answer & None (always tuple)
    def get_responses(self):
        r1 = self.main_widget.get_responses()
        val = self.main_widget.resp.checkedButton().text()
        r2 = None
        if val in self.valid:
            r2 = self.hidden_widget.get_responses()
        return r1, r2

class Question12(qtw.QWidget):
    def __init__(self, prompt, headers, n_elements=6):
        super().__init__()
        layout2 = qtw.QVBoxLayout()
        
        grid_wid = qtw.QWidget()
        layout = qtw.QGridLayout()
        layout.addWidget(JustText(headers[0]), 0, 0, Qt.AlignCenter)
        layout.addWidget(JustText(headers[1]), 0, 1, Qt.AlignCenter)
        validator = QIntValidator(1, 1000)
        self.groups = []
        self.nums = []
        for i in range(n_elements):
            group_name = qtw.QLineEdit()
            group_name.setMaximumWidth(200)
            fnt = group_name.font()
            fnt.setPointSize(26)
            group_name.setFont(fnt)
            num_people = qtw.QLineEdit()
            num_people.setMaximumWidth(200)
            num_people.setFont(fnt)
            num_people.setValidator(validator)
            self.groups.append(group_name)
            self.nums.append(num_people)
            layout.addWidget(group_name, i + 1, 0, Qt.AlignCenter)
            layout.addWidget(num_people, i + 1, 1, Qt.AlignCenter)
        
        grid_wid.setLayout(layout)
        layout2.addWidget(JustText(prompt))
        layout2.addWidget(grid_wid)
        self.setLayout(layout2)
    
    def get_responses(self):
        return [(x.text(), y.text()) for x, y in zip(self.groups, self.nums)]


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

    q12 = Question12('Big long prompt<br>that is long',
                     ['Group Name', 'Total number of<br>group members<br>you talk to'])
    layout.addWidget(q12)
    
    ages = ['Prefer not to answer']
    ages.extend([str(i) for i in range(50)])
    age = DropDownQuestion('What is your age?', ages)
    layout.addWidget(age)
    combo.setLayout(layout)
    window = MainWindow([combo])
    # all of the work is done by on_exit
    # of the IntroDlg
    # main loop
    app.exec_()
