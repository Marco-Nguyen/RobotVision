# run testing file

import sys

from GUI.modbus_gui_lite import Ui_MainWindow
from PyQt5 import QtWidgets


# check ui
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
