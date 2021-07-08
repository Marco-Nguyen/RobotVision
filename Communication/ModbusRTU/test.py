
import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(300, 200))
        self.setWindowTitle("PyQt messagebox example - pythonprogramminglanguage.com")

        pybutton = QPushButton('Show messagebox', self)
        pybutton.clicked.connect(self.clickMethod)
        pybutton.resize(200, 64)
        pybutton.move(50, 50)

    def clickMethod(self):
        msg = QMessageBox()
        # msg.about(self, "Title", "Message")
        msg.setText('error')
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.exec_()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
