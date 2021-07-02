import minimalmodbus

import easymodbus.modbusClient

from config import *
from modbus_exception import *


class ModbusRTU(object):
    def __init__(self, args):
        self.com = args.com
        self.slaveadress = args.slaveaddress
        self.mode = args.mode
        self.is_connected = False
        self.modbus = None
        try:
            self.modbus = minimalmodbus.Instrument(self.com, slaveaddress=self.slaveadress, mode=self.mode)
            self.modbus.serial.baudrate = args.baudrate
            self.modbus.serial.parity = args.parity
            self.modbus.serial.bytesize = args.bytesize
            self.modbus.serial.stopbits = args.stopbits
            self.modbus.serial.timeout = args.timeout
            self.modbus.serial.write_timeout = args.write_timeout
            self.is_connected = True
        except Exception as e:
            # ModbusException(expression, message)
            raise e

    def close(self):
        self.modbus.serial.close()

    def read_coil(self, start_coil):
        if self.is_connected:
            try:
                values = self.modbus.read_bit(registeraddress=start_coil)
                self.close()
                return values
            except Exception as e:
                raise ModbusException(e, e)
        else:
            raise SerialPortNotOpenedException("Serial is not opened", '')

    def read_coils(self, start_coil, end_coil):
        if self.is_connected:
            try:
                values = self.modbus.read_bits(registeraddress=start_coil, number_of_bits=(end_coil - start_coil))
                self.close()
                return values
            except Exception as e:
                raise ModbusException(e, e)
        else:
            raise SerialPortNotOpenedException("Serial is not opened", '')


if __name__ == "__main__":
    args = HyperParams()
    myModbus = ModbusRTU(args)
    # myModbus.close()
    print(myModbus.read_coils(0, 12), myModbus.is_connected)
    # myClient = easymodbus.modbusClient.ModbusClient('COM4')
    # if (not myClient.is_connected()):
    #     myClient.connect()
    # print(myClient.read_coils(1, 11))
