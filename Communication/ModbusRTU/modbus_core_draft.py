from easymodbus.modbusClient import ModbusClient


import pandas as pd
import pprint
import random
import sys


from GUI.modbus_gui_lite import Ui_MainWindow
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem


class ModbusApp(Ui_MainWindow):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)
        self.stop_update = False
        self.connected = False
        self.is_error = False

        self.connectButton.clicked.connect(self.connect_app)
        self.resetValues.clicked.connect(self.reset_set_table)
        self.Watch.clicked.connect(self.init_tracking_table)
        self.startRunning.clicked.connect(self.start_running)
        self.stopRunning.clicked.connect(self.stop_running)
        self.read1time.clicked.connect(self.update_set_value)
        self.read1time.clicked.connect(self.update_tracking_table)

        self.set_random()
        # time for the reading step
        self.timer = QtCore.QTimer()
        # database to save all value from 3 csv files
        self.database = {'setpoints': {},
                         'trackdevice': {}, 'values_update': {}}

    def popup_msg(self, msg, src_msg='', type_msg='error'):
        """Create popup window to the ui

        Args:
            msg (str): message you want to show to the popup window
            src_msg (str, optional): source of the message. Defaults to ''.
            type_msg (str, optional): type of popup. Available: warning, error, infor. Defaults to 'error'.
        """
        try:
            self.popup = QMessageBox()
            if type_msg.lower() == 'warning':
                self.popup.setIcon(QMessageBox.Warning)
            elif type_msg.lower() == 'error':
                self.popup.setIcon(QMessageBox.Critical)
                self.is_error = True
            elif type_msg.lower() == 'infor':
                self.popup.setIcon(QMessageBox.Information)

            self.popup.setText(f"[{type_msg}]: from {src_msg}\n{msg}")
            self.popup.setStandardButtons(QMessageBox.Ok)
            self.popup.exec_()
            print(msg)
        except Exception as e:
            print('from popup_msg', e)
        pass

    def read_csv_data(self, table_name):
        """Read data from csv file and save in the database

        Args:
            table_name (str): name of csv file. Available: 'setpoints', 'trackdevice', 'values_update'
        """
        try:
            data = pd.read_csv(f'backup/{table_name}.csv')

            self.database[table_name]['name'] = list(data['name'])
            self.database[table_name]['type'] = list(data['type'])
            self.database[table_name]['address'] = list(data['address'])
            if table_name != 'trackdevice':
                self.database[table_name]['value'] = list(data['value'])

            print(f'read csv from {table_name} done')
            pprint.pprint(self.database)
        except Exception as e:
            self.popup_msg(e, src_msg="read_csv_data")

    # setpoints blocks
    def update_set_value(self):
        """update value from the set table in UI to the database
        """
        try:
            table = self.setValueTable
            nrows = table.rowCount()
            for i in range(nrows):
                if not isinstance(table.item(i, 0), type(None)):
                    self.database['setpoints']['type'][i] = table.item(
                        i, 0).text()
                    self.database['setpoints']['value'][i] = table.item(
                        i, 1).text()
            print('new setpoints:')
            pprint.pprint(self.database)
        except Exception as e:
            self.popup_msg(e, src_msg='update_set_value')

    def reset_set_table(self):
        """read data from the setpoints csv file and update the table widget
        """
        try:
            _translate = QtCore.QCoreApplication.translate
            self.read_csv_data('setpoints')
            for i in range(len(self.database['setpoints']['name'])):
                table = self.setValueTable
                table.verticalHeaderItem(i).setText(_translate(
                    "MainWindow", self.database['setpoints']['name'][i]))  # set name
                table.setItem(i, 0, QTableWidgetItem(
                    f"{self.database['setpoints']['type'][i]}"))
                table.setItem(i, 1, QTableWidgetItem(
                    f"{self.database['setpoints']['value'][i]}"))
        except Exception as e:
            self.popup_msg(e, src_msg='reset_set_table')

    # control tracking table
    def init_tracking_table(self):
        """initialize the table widget to the tracking table in UI widget.
        """
        try:
            _translate = QtCore.QCoreApplication.translate
            self.read_csv_data('trackdevice')
            table = self.trackingTable
            # update name and type of tracking params
            for i in range(len(self.database['trackdevice']['name'])):
                table.verticalHeaderItem(i).setText(_translate(
                    "MainWindow", f"{self.database['trackdevice']['name'][i]}"))  # set name
                table.setItem(i, 0, QTableWidgetItem(
                    f"{self.database['trackdevice']['type'][i]}"))
            print('init tracking table done')
        except Exception as e:
            self.popup_msg(e, src_msg='init_tracking_table')

    def update_tracking_table(self):
        """Read data from PLC and update the tracking table widget in UI widget.
        """
        try:
            if self.connected:
                table = self.trackingTable
                # read value from plc and update tracking values
                for i in range(len(self.database['trackdevice']['name'])):
                    idx = int(self.database['trackdevice']['address'][i])
                    values = self.read_from_PLC(
                        self.database['trackdevice']['type'][i], idx)
                    table.setItem(i, 1, QTableWidgetItem(f"{values}"))
            else:
                self.popup_msg("Com is not connect", src_msg='update_tracking_table', type_msg='warning')
        except Exception as e:
            self.popup_msg(e, src_msg='update_tracking_table')

    # =================================================================================================================================/
    # run contiunous block

    def start_running(self):
        """connect to the start button, if pressed, run the writting to PLC and updating tracking table contiunously.
        """
        try:
            if self.connected:
                self.sr = 0.14 if isinstance(self.samplingRate.text(), str) else int(
                    self.samplingRate.text())  # how many second read again
                self.samplingRate.setText(
                    QtCore.QCoreApplication.translate("MainWindow", f'{self.sr}'))
                self.sr *= 1000  # change to miliseconds
                self.running = True
                self.set_led_on(1, 'green')
                # run timer to read and write each sample time
                if not self.is_error:
                    self.timer.connect(self._running)
                    self.timer.start(self.sr)
            else:
                self.popup_msg("Com is not connect", src_msg='start_running', type_msg='warning')
        except Exception as e:
            self.popup_msg(e, src_msg='start_running')

    def stop_running(self):
        self.set_led_on(1, 'red')
        self.running = False

    def _running(self):
        """run both reading and writting process
        """
        if self.running:
            self._reading()
            self._writing()
        else:
            pass

    def _reading(self):
        """read from PLC and update tracking table
        """
        try:
            self.update_tracking_table()
        except Exception as e:
            self.popup_msg(e, src_msg='_reading')

    def _writing(self):
        """get value from csv update value and write to PLC
        """
        try:
            if self.connected:
                self.read_csv_data('values_update')
                self.write_to_PLC(mode='update')
            else:
                self.popup_msg("Com is not connect", src_msg='_writing', type_msg='warning')
        except Exception as e:
            self.popup_msg(e, src_msg='_writing')
        pass

    # ==========================================================================================================================/
    # reading and writing to PLC

    def write_to_PLC(self, mode='init'):
        """Connect to PLC and write data to PLC based on mode defined

        Args:
            mode (str, optional): Available: init, update.
            init mode is for writting initial value from setpoints.csv,
            update mode is for writting updated value from setpoints.csv.
            Defaults to 'init'.
        """
        try:
            plc = ModbusClient(f'COM{self.com_set}')
            if not plc.is_connected():
                plc.connect()

            if mode == 'init':
                table_name = 'setpoints'
            elif mode == 'update':
                table_name = 'values_update'

            values = self.database[table_name]['value']
            types = self.database[table_name]['type']
            address = self.database[table_name]['address']

            for v, a, t in zip(values, types, address):
                if t == 'coil':
                    v = 1 if int(v) != 0 else 0
                    plc.write_single_coil(a, v)
                if t == 'reg':
                    v = int(v)
                    plc.write_single_register(a, v)

            print(f"write {mode} done")
        except Exception as e:
            self.popup_msg(e, src_msg='write_to_PLC')

    def read_from_PLC(self, type_, address):
        """read data from plc with type and address defined

        Args:
            type_ (str): type of reading functions. Available: hr, ir, coil.
            address (int): address of reading type. eg. 1, 2, 3.

        Returns:
            [list]: list of results
        """
        try:
            plc = ModbusClient(f'COM{self.com_set}')
            if not plc.is_connected():
                plc.connect()
            if type_.strip() == 'hr':
                return plc.read_holdingregisters(address, 1)

            if type_.strip() == 'ir':
                return plc.read_inputregisters(address, 1)

            if type_.strip() == 'coil':
                return plc.read_coils(address, 1)
        except Exception as e:
            self.popup_msg(e, src_msg='read_from_PLC')

    # connect block
    def connect_app(self):
        """connect to the com port with com set and baud rate selected in UI"""
        try:
            self.com_set = self.spinBox.value()
            self.baudrate_set = self.comboBox.currentText()
            try:
                # connect plc
                plc = ModbusClient(f'COM{self.com_set}')
                if not plc.is_connected():
                    plc.connect()
                self.connected = True
                # update values from set value table and write to plc
                self.update_set_value()
                self.write_to_PLC('init')
            except Exception as e:
                self.popup_msg(e, src_msg='connect_app')

            if self.connected:
                self.connection_status.setStyleSheet("background-color: rgb(0, 170, 0)")
                print('Connected with COM', self.com_set, 'at', self. baudrate_set)
        except Exception as e:
            self.popup_msg(e)

    # display led block
    def set_led_on(self, led_num, color):
        """turn on led with color defined in UI

        Args:
            led_num (int): index of led
            color (str): color to turn on
        """
        try:
            led_list = [self.led1, self.led2, self.led3, self.led4, self.led5,
                        self.led6, self.led7, self.led8, self.led9, self.led10]
            if isinstance(led_num, list):
                for idx in led_num:
                    led_list[idx - 1].setStyleSheet(f"background-color: {color}")
            elif isinstance(led_num, int):
                led_list[led_num - 1].setStyleSheet(f"background-color: {color}")
        except Exception as e:
            self.popup_msg(e, src_msg='led display')

    def set_random(self):
        k = random.sample(range(2, 10), 5)
        self.set_led_on(k, 'green')


def run():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ModbusApp(MainWindow=MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
