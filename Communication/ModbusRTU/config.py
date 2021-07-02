import serial


class HyperParams():
    com = 'COM4'
    slaveaddress = 1

    baudrate = 9600
    bytesize = 8
    stopbits = 1
    parity = serial.PARITY_NONE
    timeout = 1
    write_timeout = 0.2
    debug = True
