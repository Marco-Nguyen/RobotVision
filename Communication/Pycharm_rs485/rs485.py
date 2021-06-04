import minimalmodbus

instrument = minimalmodbus.Instrument(
    'COM4', 1, debug=True)
instrument.serial.baudrate = 9600
instrument.clear_buffers_before_each_transaction = True
instrument.serial.stopbits = 1
instrument.serial.timeout = 0.05
instrument.serial.port = 'COM4'
# print(instrument)
try:
    print(instrument.read_register(4143))
except IOError:
    print("Failed to read from instrument")
instrument.write_string(4113, "hello")
