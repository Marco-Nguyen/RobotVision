from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(303, 220)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Distance = QtWidgets.QLineEdit(self.centralwidget)
        self.Distance.setGeometry(QtCore.QRect(30, 60, 113, 20))
        self.Distance.setObjectName("Distance")
        self.Noti = QtWidgets.QLabel(self.centralwidget)
        self.Noti.setGeometry(QtCore.QRect(30, 150, 241, 21))
        self.Noti.setFrameShape(QtWidgets.QFrame.Panel)
        self.Noti.setText("")
        self.Noti.setObjectName("Noti")
        self.Theta = QtWidgets.QLineEdit(self.centralwidget)
        self.Theta.setGeometry(QtCore.QRect(30, 100, 113, 20))
        self.Theta.setObjectName("Theta")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(150, 20, 81, 91))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label.setObjectName("label")
        self.COM_set = QtWidgets.QLineEdit(self.centralwidget)
        self.COM_set.setGeometry(QtCore.QRect(30, 20, 113, 20))
        self.COM_set.setObjectName("COM_set")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(200, 20, 75, 23))
        self.pushButton.setObjectName("pushButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 303, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:14pt;\">Com</span></p><p><span style=\" font-size:14pt;\">Distance</span></p><p><span style=\" font-size:14pt;\">Theta</span></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Send"))





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
