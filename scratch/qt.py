import sys
from PySide2.QtCore import Qt, QMargins
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QRadioButton, QGridLayout, QCheckBox, QSizePolicy, QButtonGroup, QDesktopWidget
from PySide2.QtGui import QPixmap
from functools import partial


def _exit_on_esc(e):
    if e.key() == Qt.Key_Escape:
        QApplication.instance().quit()


if __name__ == '__main__':
    app = QApplication([])

    window = QWidget()
    wg = QGridLayout()
    rect = QDesktopWidget().screenGeometry()
    window.setFixedSize(rect.width(), rect.height())
    window.showFullScreen()
    window.keyPressEvent = _exit_on_esc
    grid = QGridLayout()
    surv = QWidget()
    surv.setFixedSize(rect.width()//2, rect.height()//4)
    wg.addWidget(surv)
    # grid.setVerticalSpacing(0)
    # grid.setContentsMargins(0, 0, 0, 0)

    dv5_1 = QPixmap('dv5_1.png')

    grid.addWidget(QLabel('Reserved'), 0, 0)
    header = ["1\nCompletely\ninappropriate", "2", "3", "4", "5", "6", "7\nCompletely\nappropriate"]
    for count, head in enumerate(header):
        h = QLabel(head)
        h.setAlignment(Qt.AlignCenter)
        grid.addWidget(h, 0, count+1, alignment=Qt.AlignCenter | Qt.AlignBottom)

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

    # for i in range(grid.rowCount()):
    #     grid.setRowStretch(i, 0.5)

    lab = QLabel()
    lab.setPixmap(dv5_1)
    grid.addWidget(lab, 0, 0)
    surv.setLayout(grid)
    window.setLayout(wg)
    window.show()

    app.exec_()
