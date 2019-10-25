from PySide2.QtCore import Qt
import PySide2.QtWidgets as qtw
from PySide2.QtGui import QPixmap, QImage
from functools import partial
from base_area import MainWindow
from my_widgets import MultiQuestion, SingleQuestion


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        qtw.QApplication.instance().quit()


if __name__ == '__main__':
    # main window (fullscreen)
    app = qtw.QApplication([])

    pic = QImage('dv5_1.png').scaledToHeight(1200, Qt.SmoothTransformation)
    pic_inst = qtw.QLabel()
    # pic_inst.setScaledContents(True)
    pic_inst.setAlignment(Qt.AlignCenter)
    pic_inst.setPixmap(QPixmap.fromImage(pic))
    pic_inst.setStyleSheet('border:2px solid rgb(0, 0, 0);border-radius:20px;')

    pic2 = qtw.QLabel()
    pic2.setPixmap(QPixmap.fromImage(pic))
    pic3 = qtw.QLabel()
    pic3.setPixmap(QPixmap.fromImage(pic))
    xxx = qtw.QWidget()
    #t0 = qtw.QVBoxLayout()
    t0 = qtw.QGridLayout()
    t0.addWidget(pic_inst, 0, 0, 1, 1, Qt.AlignCenter)
    t0.addWidget(pic2, 1, 0, 1, 1, Qt.AlignLeft)
    t0.addWidget(pic3, 2, 0, 1, 1, Qt.AlignCenter)
    xxx.setLayout(t0)
    header = ["1\nCompletely\ninappropriate", "2", "3", "4", "5", "6", "7\nCompletely\nappropriate"]
    questions = ["How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 """How likely is it that this person committed a premeditated crime? Here's even more text to see how things wrap...
                 
                 Newlines and all.""",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that <b>this person</b> committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?",
                 "How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?"]
    multi_q = MultiQuestion(header, questions)

    q1 = SingleQuestion(header, 'What is your name?')
    q2 = SingleQuestion(header, 'What is your quest?')
    single_q = qtw.QWidget()
    layout = qtw.QVBoxLayout()
    layout.addWidget(q1)
    layout.addWidget(q2)
    single_q.setLayout(layout)
    tmp2 = qtw.QLabel('BAR')
    tmp2.setAlignment(Qt.AlignRight | Qt.AlignBottom)
    stack = [[single_q, multi_q, xxx], pic_inst, tmp2]

    window = MainWindow(stack)

    app.exec_()
