import serial
import random

#Sub Program
#CRC Calculation
def CRCcal(msg):
    #CRC (Cyclical Redundancy Check) Calculation
    CRC = 0xFFFF
    CRCHi = 0xFF
    CRCLo = 0xFF
    CRCLSB = 0x00
    for i in range(0, len(msg)-2,+1):
        CRC = (CRC ^ msg[i])
        for j in range(0, 8):
            CRCLSB = (CRC & 0x0001);
            CRC = ((CRC >> 1) & 0x7FFF)

            if (CRCLSB == 1):
                CRC = (CRC ^ 0xA001)
    CRCHi = ((CRC >> 8) & 0xFF)
    CRCLo = (CRC & 0xFF)
    return (CRCLo,CRCHi)  


#CRC Valdation
def CRCvalid(resp):
    CRC = CRCcal(resp)
    if (CRC[0]==resp[len(resp)-2]) & (CRC[1]==resp[len(resp)-1]):return True
    return False


#Modbus Function Code 16 = Preset Multiple Registers    
def Func16Modbus(slave,start,values):
    Slave_Address = slave
    Function = 16
    Starting_Address = start
    NumberofRegisters = len(values)
    Byte_Count = NumberofRegisters * 2
    message = [0 for i in range(9 + 2 * NumberofRegisters)]   

    #index0 = Slave Address
    message[0] = (Slave_Address & 0xFF)
    #index1 = Function
    message[1] = (Function & 0xFF)
    #index2 = Starting Address Hi
    message[2] = ((Starting_Address >> 8) & 0xFF)
    #index3 = Starting Address Lo
    message[3] = (Starting_Address & 0xFF)
    #index4 = Number of Registers Hi
    message[4] = ((NumberofRegisters >> 8) & 0xFF)
    #index5 = Number of Registers Lo
    message[5] = (NumberofRegisters & 0xFF)
    #index6 = Byte Count
    message[6] = (Byte_Count & 0xFF)

    for i in range(0, NumberofRegisters):
        #Data Hi, index7 and index9
        message[7 + 2 * i] = ((values[i] >> 8) & 0xFF)
        #Data Lo, index8 and index10
        message[8 + 2 * i] = values[i] & 0xFF

    #CRC (Cyclical Redundancy Check) Calculation
    CRC = CRCcal(message)
    
    #index11= CRC Lo
    message[len(message) - 2] = CRC[0]#CRCLo
    #index12 = CRC Hi
    message[len(message) - 1] = CRC[1]#CRCHi

    if ser.isOpen:        
        ser.write("".join(chr(h) for h in message)) 
        reading = ser.read(8)
        response = [0 for i in range(len(reading))] 
        for i in range(0, len(reading)):
            response[i] = ord(reading[i])

        if len(response)==8:
            CRCok = CRCvalid(response)
            if CRCok & (response[0]==slave) & (response[1]==Function):return True
    return False


#Modbus Function Code 03 = Read Holding Registers
def Func03Modbus(slave,start,NumOfPoints):
    #Function 3 request is always 8 bytes
    message = [0 for i in range(8)]  
    Slave_Address = slave
    Function = 3
    Starting_Address = start
    Number_of_Points = NumOfPoints

    #index0 = Slave Address
    message[0] = Slave_Address
    #index1 = Function
    message[1] = Function
    #index2 = Starting Address Hi
    message[2] = ((Starting_Address >> 8)& 0xFF)
    #index3 = Starting Address Lo
    message[3] = (Starting_Address& 0xFF)
    #index4 = Number of Points Hi
    message[4] = ((Number_of_Points >> 8)& 0xFF)
    #index5 = Number of Points Lo
    message[5] = (Number_of_Points& 0xFF)

    #CRC (Cyclical Redundancy Check) Calculation
    CRC = CRCcal(message)
    
    #index6= CRC Lo
    message[len(message) - 2] = CRC[0]#CRCLo
    #index7 = CRC Hi
    message[len(message) - 1] = CRC[1]#CRCHi
    
    if ser.isOpen:        
        ser.write("".join(chr(h) for h in message))
        responseFunc3total = 5 + 2 * Number_of_Points
        reading = ser.read(responseFunc3total)
        response = [0 for i in range(len(reading))] 
        for i in range(0, len(reading)):
            response[i] = ord(reading[i])
        
        if len(response)==responseFunc3total:
            CRCok = CRCvalid(response)
            if CRCok & (response[0]==slave) & (response[1]==Function):
                #Byte Count in index 3 = responseFunc3[2]
                #Number of Registers = byte count / 2 = responseFunc3[2] / 2
                registers = ((response[2] / 2)& 0xFF)
                values = [0 for i in range(registers)] 
                for i in range(0, len(values)):
                    #Data Hi and Registers1 from Index3
                    values[i] = response[2 * i + 3]
                    #Move to Hi
                    values[i] <<= 8
                    #Data Lo and Registers1 from Index4
                    values[i] += response[2 * i + 4]
                    negatif = values[i]>>15
                    if negatif==1:values[i]=values[i]*-1
                return values
    return ()


#Main Program
#Serial Port 9600,8,E,1
#Serial Open
try:
        ser = serial.Serial(
                port = '/dev/ttyAMA0',
                baudrate = 9600,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_EVEN,
                stopbits = serial.STOPBITS_ONE,
                timeout = 0.2
        )
except Exception, e:
        raise ValueError(e)


print "START"
while 1:        
    #Serial Open Check
    if not ser.isOpen:ser.open()

    #Read of Registers
    Func03ArrayValue = Func03Modbus(1,0,2);#slave,start,number of registers
    if len(Func03ArrayValue)>0:
        for i in range(0, len(Func03ArrayValue)):
            print "Read of Registers" + str(i) + " = " + str(Func03ArrayValue[i])

    #Fill Random Value for Write
    totalvalue=2
    val = [0 for i in range(totalvalue)]
    for i in range(0, len(val)):
        val[i] = random.randrange(-32767,32767) #Random Valiue from -32767 to max 32767

    #Write of Registers
    WriteValid = Func16Modbus(1,2,val)#slave,start,array value
    if WriteValid:
        for i in range(0, len(val)):
            print "Write of Registers" + str(i) + " = " + str(val[i])
        print "#################################"
