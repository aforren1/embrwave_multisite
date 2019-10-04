import sys
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QGridLayout, QCheckBox, QSizePolicy, QButtonGroup
from PyQt5.QtGui import QPixmap
from functools import partial


if __name__ == '__main__':
    app = QApplication([])

    window = QWidget()
    policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    grid = QGridLayout()

    dv5_1 = QPixmap('dv5_1.png')

    grid.addWidget(QLabel('Reserved'), 0, 0)
    header = ["1\nCompletely\ninappropriate", "2", "3", "4", "5", "6", "7\nCompletely\nappropriate"]
    for count, head in enumerate(header):
        grid.addWidget(QLabel(head), 0, count+1, alignment=Qt.AlignCenter | Qt.AlignBottom)

    questions = ["How likely is it that this person committed a premeditated crime?",
                 "How likely is it that this person committed an impulsive crime?"]
    for i, ques in enumerate(questions):
        q = QLabel(ques)
        q.setWordWrap(True)
        grid.addWidget(q, i+1, 0)
        qbg = QButtonGroup()
        for count in range(len(header)):
            rad = QRadioButton('')
            rad.setStyleSheet('QRadioButton::indicator{width:60px; height:60px;}')
            qbg.addButton(rad)
            grid.addWidget(rad, i+1, count+1, alignment=Qt.AlignCenter)

    lab = QLabel()
    lab.setPixmap(dv5_1)
    grid.addWidget(lab, 0, 0)
    window.setLayout(grid)
    window.show()

    app.exec()
