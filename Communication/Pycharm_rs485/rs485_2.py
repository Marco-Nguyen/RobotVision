from types import ModuleType
import easymodbus.modbusClient
modbus_client = easymodbus.modbusClient.ModbusClient('COM4')
modbus_client.connect()
modbus_client.write_multiple_coils(123, '01 02')
modbus_client.close()
