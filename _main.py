
if __name__ == '__main__':
    # explicit import allegedly helps PyInstaller find the
    # right dependencies
    import PySide2
    import PySide2.QtWidgets as qtw
    from embr_survey.window import MainWindow
    from embr_survey.intro_widgets import IntroDlg

    app = qtw.QApplication([])
    intro_dlg = IntroDlg()

    # all of the work is done by on_exit
    # of the IntroDlg
    window = MainWindow([intro_dlg])
    app.exec_()
