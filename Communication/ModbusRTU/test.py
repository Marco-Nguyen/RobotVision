import sys

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(466, 299)
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # Radio button for male
        self.radioButton_male = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_male.setGeometry(QtCore.QRect(180, 120, 95, 20))

        # adding signal and slot
        self.radioButton_male.toggled.connect(self.maleselected)

        # Radio button for female
        self.radioButton_female = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_female.setGeometry(QtCore.QRect(180, 150, 95, 20))

        # adding signal and slot
        self.radioButton_female.toggled.connect(self.femaleselected)

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(170, 90, 211, 20))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def maleselected(self, selected):
        if selected:
            self.label.setText("You are male")

    def femaleselected(self, selected):
        if selected:
            self.label.setText("You are female")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.radioButton_male.setText(_translate("MainWindow", "Male"))
        self.label.setText(_translate("MainWindow", "Select your gender:"))
        self.radioButton_female.setText(_translate("MainWindow", "Female"))


# Driver Code
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
