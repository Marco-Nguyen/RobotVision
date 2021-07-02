from easymodbus.modbusClient import ModbusClient

import os
import sys
import time

import pandas as pd
import random

from GUI.modbus_gui_lite import Ui_MainWindow
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout


class thread_update(QThread):
    update_table = pyqtSignal()

    def __init__(self):
        self.reading = True

    def run(self):

        while self.reading:
            pass

    def stop(self):
        self.reading = False


class ModbusApp(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)
        self.stop_update = False
        self.connected = False
        self.connectButton.clicked.connect(self.connect_app)
        self.resetValues.clicked.connect(self.reset_set_table)
        self.setValue.clicked.connect(self.write_to_PLC)
        # self.thread = thread_update()
        # self.thread.update_table.connect(self.start_reading)
        # self.startReading.clicked.connect(self.thread.start)
        self.startReading.clicked.connect(self.start_reading)
        self.stopReading.clicked.connect(self.stop_reading)
        self.set_random()

    def update_tracking_table(self, init=True):
        # base
        if init:
            _translate = QtCore.QCoreApplication.translate
            data = pd.read_csv('backup/trackdevice.csv')
            # print(data)
            self.name = list(data['name'])
            self.type_ = list(data['type'])
            self.address_track = list(data['address'])
            # print(self.setValueTable.columnCount())
            table = self.trackingTable
            for i in range(len(self.name)):

                table.verticalHeaderItem(i).setText(_translate("MainWindow", f"{self.name[i]}"))  # set name
                table.setItem(i, 0, QTableWidgetItem(f"{self.type_[i]}"))
        else:
            table = self.trackingTable
            for i in range(len(self.name)):
                idx = int(self.address_track[i])
                values = self.read_from_PLC(self.type_[i], idx)
                table.setItem(i, 1, QTableWidgetItem(f"{values[0]}"))
            pass

        pass

    def update_set_value(self):
        table = self.setValueTable
        nrows = table.rowCount()
        for i in range(nrows):
            if not isinstance(table.item(i, 0), type(None)):
                self.type_set[i] = table.item(i, 0).text()
                self.values_set[i] = table.item(i, 1).text()

        pass
    # @pyqtSlot()

    def start_reading(self):
        self.sr = 2 if isinstance(self.samplingRate.text(), str) else int(self.samplingRate.text())  # how many second read again
        self.reading = True
        self.update_tracking_table()
        # while self.reading:
        #     self.update_tracking_table(False)
        #     time.sleep(self.sr)
        self.update_tracking_table(False)

    def stop_reading(self):
        self.reading = False
        # self.thread.stop()

    def read_csv_data(self):
        data = pd.read_csv('backup/setpoints.csv')
        # print(data)
        self.name_set = list(data['name'])
        self.type_set = list(data['type'])
        self.values_set = list(data['value'])
        self.address_set = list(data['address'])

    def reset_set_table(self):
        _translate = QtCore.QCoreApplication.translate
        self.read_csv_data()
        try:
            for i in range(len(self.name_set)):
                table = self.setValueTable
                table.verticalHeaderItem(i).setText(_translate("MainWindow", self.name_set[i]))  # set name
                table.setItem(i, 0, QTableWidgetItem(f"{self.type_set[i]}"))
                table.setItem(i, 1, QTableWidgetItem(f"{self.values_set[i]}"))

        except Exception:
            pass

    def write_to_PLC(self):
        self.update_set_value()
        plc = ModbusClient(f'COM{self.com_set}')
        if not plc.is_connected():
            plc.connect()
        for v, a, t in zip(self.values_set, self.address_set, self.type_set):
            if t == 'coil':
                if int(v) != 0:
                    v = 1
                else:
                    v = 0
                plc.write_single_coil(a, v)
                pass
            if t == 'reg':
                v = int(v)
                plc.write_single_coil(a, v)
                pass
        pass

    def read_from_PLC(self, type_, address):
        plc = ModbusClient(f'COM{self.com_set}')
        if not plc.is_connected():
            plc.connect()
        if type_.strip() == 'hr':
            return plc.read_holdingregisters(address, 1)

        if type_.strip() == 'ir':
            return plc.read_inputregisters(address, 1)

        if type_.strip() == 'coil':
            return plc.read_coils(address, 1)

    def connect_app(self):
        self.connected = True
        self.com_set = self.spinBox.value()
        self.baudrate_set = self.comboBox.currentText()
        print(self.com_set, self.baudrate_set)
        if self.connected:
            self.connection_status.setStyleSheet("background-color: rgb(0, 170, 0)")
        pass

    def set_led_on(self, led_num, color):
        led_list = [self.led1, self.led2, self.led3, self.led4, self.led5, self.led6, self.led7, self.led8, self.led9, self.led10]
        led_list[led_num - 1].setStyleSheet("background-color: rgb(0, 170, 0)")

    def set_random(self):
        k = random.randint(1, 10)
        self.set_led_on(k, 'green')


def run():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ModbusApp(MainWindow=MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
