# explicit import allegedly helps PyInstaller find the
# right dependencies
import PySide2

if __name__ == '__main__':
    from PySide2.QtWidgets import QApplication
    from embr_survey.window import MainWindow
    from embr_survey.intro_widgets import IntroDlg

    app = QApplication([])
    intro_dlg = IntroDlg()
    # note to self: need at least one widget to start
    # (though this is probably pretty easy to resolve)
    window = MainWindow([intro_dlg]) # intro_dlg is the true workhorse
    # all of the work is done by on_exit
    # of the IntroDlg
    # main loop
    app.exec_()
