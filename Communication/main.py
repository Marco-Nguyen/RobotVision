import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import Qt
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from SerialConfig import SerialConfig
from senddata import Ui_MainWindow


class App(Ui_MainWindow, SerialConfig):
    def __init__(self, MainWindow):
        self.MainWindow = MainWindow
        self.setupUi(self.MainWindow)
        self.setup_box([self.Distance, self.COM_set, self.Theta], [3, 2, 5])
        self.Distance.textChanged.connect(self.get_distance)
        self.COM_set.textChanged.connect(self.get_com)
        self.Theta.textChanged.connect(self.get_theta)

        self.pushButton.clicked.connect(self.send)

    def get_com(self, com):
        self.com_ = com

    def get_distance(self, distance):
        self.distances_ = distance

    def get_theta(self, theta):
        self.theta_ = theta

    def setup_box(self, xs, length):
        for x, l in zip(xs, length):
            x.setValidator(QIntValidator())
            x.setMaxLength(l)
            x.setAlignment(Qt.AlignRight)
            x.setFont(QFont("Arial", 10))

    def send(self):
        print(f'Com: {self.com_}\nDistance: {self.distances_}m\nTheta: {self.theta_}')
        MySerial = SerialConfig(f'COM{self.com_}')
        state = MySerial.send_data(f'{self.distances_} {self.theta_}')
        if state:
            self.Noti.setText(QtCore.QCoreApplication.translate("MainWindow", f"Done"))
        else:
            self.Noti.setText(QtCore.QCoreApplication.translate("MainWindow", f"Cannot send, check all again!!"))
        MySerial.stop()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = App(MainWindow=MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
