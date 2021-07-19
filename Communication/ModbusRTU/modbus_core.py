import os
import random
import sys
import time

import pandas as pd

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QTableWidgetItem
from easymodbus.modbusClient import ModbusClient

from GUI.modbus_gui_lite import Ui_MainWindow


class ModbusApp(Ui_MainWindow, QtWidgets.QWidget):
    def __init__(self, MainWindow):
        super().__init__()
        self.setupUi(MainWindow)

        self.connected = False
        self.is_error = False
        self.is_init_table = True
        self.is_auto = True
        self.is_rtu = True

        self.connectButton.clicked.connect(self.connect_app)
        self.set_all_values.clicked.connect(self.update_all_values)
        self.startRunning.clicked.connect(self.start_running)
        self.stopRunning.clicked.connect(self.stop_running)
        self.read1time.clicked.connect(self.update_tracking_table)
        self.openFiles.clicked.connect(self.open_files)

        # control block
        self.ctrl_left_button.clicked.connect(self.turn_left)
        self.ctrl_right_button.clicked.connect(self.turn_right)
        self.ctrl_forward_button.clicked.connect(self.move_forward)
        self.ctrl_backward_button.clicked.connect(self.move_backward)
        self.ctrl_stop_button.clicked.connect(self.stop_moving)
        # select block
        self.auto_mode.toggled.connect(self.select_auto)
        self.manual_mode.toggled.connect(self.select_manual)
        self.tcp_mode.toggled.connect(self.select_tcp)
        self.rtu_mode.toggled.connect(self.select_rtu)

        self.set_random()
        # time for the reading step
        self.timer = QtCore.QTimer()
        # database to save all value from 3 csv files
        self.database = {'setpoints': {},
                         'trackdevice': {},
                         'values_update': {},
                         'control': {}}
        self.settings = {'minAlpha': 5,
                         'minDis': 1000,
                         'samplingRate': 0.14,
                         'movement': {}}

    def popup_msg(self, msg, src_msg='', type_msg='error'):
        """Create popup window to the ui

        Args:
            msg (str): message you want to show to the popup window
            src_msg (str, optional): source of the message. Defaults to ''.
            type_msg (str, optional): type of popup. Available: warning, error, information. Defaults to 'error'.
        """
        try:
            self.popup = QMessageBox()
            if type_msg.lower() == 'warning':
                self.popup.setIcon(QMessageBox.Warning)
            elif type_msg.lower() == 'error':
                self.popup.setIcon(QMessageBox.Critical)
                self.is_error = True
            elif type_msg.lower() == 'info':
                self.popup.setIcon(QMessageBox.Information)

            self.popup.setText(f"[{type_msg.upper()}] -> From: {src_msg}\nDetails: {msg}")
            self.popup.setStandardButtons(QMessageBox.Ok)
            self.popup.exec_()
            print(f'[{type_msg.upper()}]: {msg} from {src_msg}')
        except Exception as e:
            print('-> From: popup_msg', e)
        pass
    # ==========================================================================================================================/

    def open_files(self):
        """open file when pressing edit files
        """
        try:
            filename = QFileDialog.getOpenFileNames(self, caption='Open File', directory='backup')
            for file in list(filename[0]):
                f = os.path.join("backup/", os.path.split(file)[1])
                # print(filename)
                command = f'notepad.exe {f}'
                os.system(command)
        except Exception as e:
            self.popup_msg(e, src_msg='open file', type_msg='info')
        # read and write to database format using pandas

    def read_table_data(self, table_name, format_='csv'):
        """Read data from csv file and save in the database

        Args:
            table_name (str): name of csv file. Available: 'setpoints', 'trackdevice', 'values_update'
        """
        try:
            PATH = f'backup/{table_name}.{format_}'
            if os.path.isfile(PATH):
                if format_ == 'csv':
                    data = pd.read_csv(PATH)
                if table_name != 'movement':
                    self.database[table_name]['name'] = list(data['name'])
                    self.database[table_name]['type'] = list(data['type'])
                    self.database[table_name]['address'] = list(data['address'])
                    if table_name != 'trackdevice':
                        self.database[table_name]['value'] = list(data['value'])
                else:
                    for i in range(len(list(data['name']))):
                        self.settings[table_name][data['name'][i]] = [data['type'][i], data['address'][i]]

                print(f'read {format_} from {table_name}.{format_} done')

            else:
                self.popup_msg(f'{table_name}.{format_} not found', src_msg='read_table_data', type_msg='info')
                print(f'{table_name}.{format_} not found')
        except Exception as e:
            self.popup_msg(e, src_msg="read_table_data")

    def write_table_data(self, table_name, format_):
        try:
            df = pd.DataFrame.from_dict(self.database[table_name])
            PATH = f'backup/{table_name}.{format_}'
            if format_ == 'csv':
                df.to_csv(PATH, index=False)
            elif format_ == 'pkl':
                df.to_pickle(PATH, index=False)
        except Exception as e:
            self.popup_msg(e, src_msg='write_table_data')

    def import_settings(self):
        try:
            with open('backup/settings.txt', 'r') as f:
                settings = f.readlines()

            for line in settings:
                data = line.strip().split(' ')
                self.settings[data[0]] = float(data[1])

            self.read_table_data('movement')

        except Exception as e:
            self.popup_msg(e, src_msg='import settings')

    # ========================================================table display handling==================================================================/

    def update_all_values(self):
        """init all table and values when pressing set values
        """
        self.import_settings()
        self.check_set_values()
        if self.is_init_table:
            print('init')
            self.set_set_table(mode='init')
            self.set_tracking_table(mode='init')
            self.is_init_table = False
        else:
            self.set_set_table()
            self.set_tracking_table()

    # setpoints blocks

    def update_set_value(self):
        """update value from the set table in UI to the database
        """
        try:
            table = self.setValueTable
            # print(table)
            nrows = table.rowCount()
            for i in range(nrows):
                if not isinstance(table.item(i, 0), type(None)):
                    self.database['setpoints']['type'][i] = table.item(
                        i, 0).text()
                    self.database['setpoints']['value'][i] = table.item(
                        i, 1).text()
            print('Apply new set points')
            # pprint.pprint(self.database)
        except Exception as e:
            self.popup_msg(e, src_msg='update_set_value')

    def set_set_table(self, mode='update'):
        """read data from the setpoints csv file and update the table widget
        """
        try:
            table = self.setValueTable

            if mode != 'init':
                # reset table
                nrows = table.rowCount()
                table.setVerticalHeaderLabels(tuple(["newRow"] * nrows))  # set name
                table.clearContents()

            # update data
            self.read_table_data('setpoints')
            self.check_if_expanding('setpoints')

            for i in range(len(self.database['setpoints']['name'])):
                table.setVerticalHeaderItem(i, QtWidgets.QTableWidgetItem(self.database['setpoints']['name'][i]))
                table.setItem(i, 0, QTableWidgetItem(
                    f"{self.database['setpoints']['type'][i]}"))
                table.setItem(i, 1, QTableWidgetItem(
                    f"{self.database['setpoints']['value'][i]}"))
        except Exception as e:
            self.popup_msg(e, src_msg='set_set_table')

    # tracking block
    def set_tracking_table(self, mode='update'):
        """initialize the table widget to the tracking table in UI widget.
        """
        try:
            table = self.trackingTable
            if mode != 'init':
                # reset table
                nrows = table.rowCount()
                table.setVerticalHeaderLabels(tuple(["newRow"] * nrows))  # set name
                table.clearContents()

            self.read_table_data('trackdevice')
            self.check_if_expanding('trackdevice')
            table = self.trackingTable
            # update name and type of tracking params
            for i in range(len(self.database['trackdevice']['name'])):
                table.setVerticalHeaderItem(i, QtWidgets.QTableWidgetItem(self.database['trackdevice']['name'][i]))  # set name
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

    def check_if_expanding(self, table_name):
        """check whether we need more rows to display database
        """
        try:
            if table_name == 'setpoints':
                table = self.setValueTable
            elif table_name == 'trackdevice':
                table = self.trackingTable
            n_rows = table.rowCount()
            data_length = len(self.database[table_name]['name'])
            gap = data_length - n_rows
            if gap > 0:
                for i in range(n_rows, data_length):
                    table.insertRow(i)

        except Exception as e:
            self.popup_msg(e, src_msg='check_if_expanding', type_msg='error')

    # ==========================================================run contiunous block===============================================================/

    def start_running(self):
        """connect to the start button, if pressed, run the writting to PLC and updating tracking table contiunously.
        """
        correction_value = 0.14  # delay time
        try:
            if self.connected:
                self.check_set_values()
                self.sr = int((self.self.settings['samplingRate'] - correction_value) * 1000)
                print("SamplingRate: ", self.self.settings['samplingRate'])  # change to miliseconds
                self.running = True
                # run timer to read and write each sample time
                if not self.is_error:
                    self.timer.timeout.connect(self._running)
                    self.timer.start(self.self.settings['samplingRate'])
            else:
                self.popup_msg("Com is not connect", src_msg='start_running', type_msg='warning')
        except Exception as e:
            self.popup_msg(e, src_msg='start_running')

    def stop_running(self):
        print('>> stop running')
        self.running = False

    def _running(self):
        """run both reading and writting process
        """
        if self.running:
            print('\n>> still running ================================== <<')
            start_time = time.time()
            self._reading()
            read_time = time.time()
            self._writing()
            write_time = time.time()
            print(f'Executing time: read {read_time - start_time}s write {write_time - read_time}s total {time.time() - start_time}s')
        else:
            print('Not running')
            self.timer.stop()
            pass
        color = 'green' if self.running else 'red'
        self.set_led_on(1, color)

    def _reading(self):
        """read from PLC and update tracking table
        """
        try:
            self.update_tracking_table()
        except Exception as e:
            self.popup_msg(e, src_msg='_reading')

    def _writing(self):
        """get value from csv update value and write to PLC
        read 2 csv file transfrom data from 2 values distance and theta to coil state, save to control csv and write from that csv to plc
        """
        try:
            if self.connected:
                self.read_table_data('values_update')
                self.read_table_data('control')
                self.transform_data()
                self.write_to_PLC(mode='control')
            else:
                self.popup_msg("Com is not connect", src_msg='_writing', type_msg='warning')
        except Exception as e:
            self.popup_msg(e, src_msg='_writing')
        pass
    # ==========================================================run selecting block===============================================================/

    def select_auto(self, selected):
        if selected:
            self.is_auto = True
            print(">> Automatically mode:", self.is_auto)

    def select_manual(self, selected):
        if selected:
            self.is_auto = False
            print(">> Automatically mode:", self.is_auto)

    def select_tcp(self, selected):
        if selected:
            self.is_rtu = False
            print(">> Connecting by RTU:", self.is_rtu)

    def select_rtu(self, selected):
        if selected:
            self.is_rtu = True
            print(">> Connecting by RTU:", self.is_rtu)

    # ==========================================================run controller block===============================================================/

    def move_forward(self):
        if not self.is_auto:
            t = self.settings['movement']['forward'][0]
            a = self.settings['movement']['forward'][1]
            v = 1
            self.write_to_PLC_core(t, a, v)

    def move_backward(self):
        if not self.is_auto:
            t = self.settings['movement']['backward'][0]
            a = self.settings['movement']['backward'][1]
            v = 1
            self.write_to_PLC_core(t, a, v)

    def turn_left(self):
        if not self.is_auto:
            t = self.settings['movement']['left'][0]
            a = self.settings['movement']['left'][1]
            v = 1
            self.write_to_PLC_core(t, a, v)

    def turn_right(self):
        if not self.is_auto:
            t = self.settings['movement']['right'][0]
            a = self.settings['movement']['right'][1]
            v = 1
            self.write_to_PLC_core(t, a, v)

    def stop_moving(self):
        if not self.is_auto:
            for move in self.settings['movement']:
                t = move[0]
                a = move[1]
                v = 0
                self.write_to_PLC_core(t, a, v)
    # ==========================================================================================================================/

    def check_set_values(self):
        """Check all set values in all lineEdit if they are not set, set by defined values
        """
        ip_default = True
        port_default = True

        try:
            self.tcp_ip = str(self.ipAddress.text())
            ip_default = False
        except Exception:
            pass
        try:
            self.port_set = str(self.Port.text())
            port_default = False
        except Exception:
            pass

        if ip_default:
            self.tcp_ip = '127.0.0.1'
            self.ipAddress.setText(QtCore.QCoreApplication.translate("MainWindow", f'{self.tcp_ip}'))
        if port_default:
            self.port_set = '502'
            self.ipAddress.setText(QtCore.QCoreApplication.translate("MainWindow", f'{self.port_set}'))

    def transform_data(self):
        """transform values from update csv file to coil state with the define rules"""
        try:
            dis = self.database['values_update']['value'][0]
            theta = self.database['values_update']['value'][1]
            dump_coils = list(self.database['control']['value'])
            # rules
            dump_coils[0] = theta > self.settings['minAlpha']
            dump_coils[1] = theta < -self.settings['minAlpha']
            dump_coils[2] = not(dump_coils[0] or dump_coils[1])
            dump_coils[3] = dis > self.self.settings['minDis']
            dump_coils[4] = not dump_coils[3]
            # change values in  database
            for i in range(len(dump_coils)):
                self.database['control']['value'][i] = int(dump_coils[i])
            # write to csv
            self.write_table_data(table_name='control', format_='csv')

        except Exception as e:
            self.popup_msg(e, src_msg='transform_data', type_msg='warning')
        pass

    # ===============================================reading and writing to PLC=========================================================/
    def write_to_PLC_core(self, type_, address, value):
        try:
            #  check connection
            try:
                if self.is_rtu:
                    plc = ModbusClient(f'COM{self.com_set}')
                else:
                    plc = ModbusClient(self.tcp_ip, self.port_set)
            except Exception as e:
                print("Error", e)
            if not plc.is_connected():
                plc.connect()
            if plc.is_connected():
                print("PlC is connected, writing_time")
                self.connected = True

            if type_ == 'coil':
                plc.write_single_coil(address, value)
            elif type_ == 'reg':
                plc.write_single_register(address, value)
        except Exception as e:
            self.popup_msg(msg=e, src_msg='write_to_PLC_core', type_msg='warning')
            self.connected = False

    def write_to_PLC(self, mode='init'):
        """Connect to PLC and write data to PLC based on mode defined

        Args:
            mode (str, optional): Available: init, update.
            init mode is for writting initial value from setpoints.csv,
            update mode is for writting updated value from setpoints.csv.
            Defaults to 'init'.
        """
        values, types, address = [], [], []
        try:

            if mode == 'init':
                table_name = 'setpoints'
            elif mode == 'update':
                table_name = 'values_update'
            elif mode == 'control':
                table_name = 'control'

            try:
                values = list(self.database[table_name]['value'])
                types = list(self.database[table_name]['type'])
                address = list(self.database[table_name]['address'])
            except Exception as e:
                self.popup_msg(msg=e, src_msg='write_to_PLC', type_msg='info')
            # print(values, types, address)
            try:
                for v, a, t in zip(values, address, types):
                    self.write_to_PLC_core(t, a, v)
                print(f"write {mode} done")
            except Exception as e:
                self.popup_msg(msg=e, src_msg='write_to_PLC', type_msg='warning')
                self.connected = False

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
            if self.is_rtu:
                plc = ModbusClient(f'COM{self.com_set}')
            else:
                plc = ModbusClient(self.tcp_ip, self.port_set)

            if not plc.is_connected():
                plc.connect()
            if type_.strip() == 'hr':
                return plc.read_holdingregisters(address, 1)[0]

            if type_.strip() == 'ir':
                return plc.read_inputregisters(address, 1)[0]

            if type_.strip() == 'coil':
                return plc.read_coils(address, 1)[0]
        except Exception as e:
            self.popup_msg(e, src_msg='read_from_PLC')

    # ====================================================== connect block=========================================/
    def connect_app(self):
        """connect to the com port with com set and baud rate selected in UI"""
        try:
            self.com_set = self.spinBox.value()
            self.baudrate_set = self.comboBox.currentText()
            self.check_set_values()
            # connect plc
            if self.is_rtu:
                plc = ModbusClient(f'COM{self.com_set}')
                msg = f"COM{self.com_set} at {self.baudrate_set}"
            else:
                plc = ModbusClient(self.tcp_ip, self.port_set)
                msg = f"IP: {self.tcp_ip} //Port: {self.port_set}"
            if not plc.is_connected():
                plc.connect()
                # print("is connected")
                self.connected = True
            # update values from set value table and write to plc
            plc.close()
            self.update_set_value()
            self.write_to_PLC('init')

            if self.connected:
                print('Connected with', msg)
                self.connectButton.setStyleSheet("background-color : green")
            else:
                self.connectButton.setStyleSheet("background-color : red")
                print('Disconnect with', msg)
        except Exception as e:
            self.connectButton.setStyleSheet("background-color : red")
            self.popup_msg(e, src_msg='connect_app')

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
        k = random.sample(range(3, 10), 3)
        self.set_led_on(k, 'green')


def run():
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = ModbusApp(MainWindow=MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
