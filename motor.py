import serial
import time
import crc16

##################
#Open Serial Port#
##################
ser = serial.Serial(
    port = '/dev/ttyUSB0',
    baudrate = 115200,
    parity = serial.PARITY_EVEN,
    stopbits = serial.STOPBITS_ONE,
    timeout = 0.1)

###################
#Message structure#
###################
##Slave address 8 bits (usually 01)
##Function code 8 bits (03 reading from a holding register
##                      06 writing to a holding register
##                      08 diagnosis
##                      10 writing to multiple holding registers
##                      17 read/write of multiple holding registers)
##Data Nx8 bits (18 00 starting register
##               00 02 number of registers
##               04 number of bytes (twice the number of registers)
##               00 00 data to be written into first register)
##Registers (MODBUS) (18 00 Operation type (Base address)
##               18 02 Position
##               18 04 Operating speed
##               18 06 Starting/changing rate
##               18 08 Stop
##               18 10 Operating current)
##Error check 16 bits

#######################
#Reading from register#
#######################
##Query
##Slave address 8 bits (usually 01)
##Function code 8 bits (03 reading from a holding register)
##Data Nx8 bits (00 7f register to read from
##               00 02 number of registers to read)
##Error check 16 bits
##
##Response
##Slave address 8 bits (usually 01)
##Function code 8 bits (03 reading from a holding register)
##Number of data bytes (Twice number of registers in the query)
##Data Nx8 bits (Values read)
##Error check 16 bits

#############
#CRC16 guide#
#############
##crc16.crc16(data) returns a dictionary containing upper and lower values.
##Use dictionary reference ['upper'] or ['lower'] to access

#####################
#Machine Calibration#
#####################
##1 mm = 100 steps
##0.1 mm = 10 steps
def ConvertSteps(mm):
    return int(mm*100)

#################
#Motor commands#
#################
def Execute():
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x08\xF5\x18')
    time.sleep(1)
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x00\xF4\xDE')
    ser.read(200)

def AlarmReset():
    command = b'\x01\x10\x01\x80\x00\x02\x04\x30\xC0\x30\xC0'
    command = command + crc16.crc16(b'\x01\x10\x01\x80\x00\x02\x04\x30\xC0\x30\xC0')['lower'] + crc16.crc16(b'\x01\x10\x01\x80\x00\x02\x04\x30\xC0\x30\xC0')['upper']
    ser.write(command)
    ser.read(200)
    CheckAlarm()

def GoLeft():
    print("Going left...")
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x40\x00'
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x40\x00')['lower']
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x40\x00')['upper'])
    ser.read(200)
    CheckReady()
    ser.read(200)
    CheckMove()
    ser.read(200)
    CheckAlarm()
    ser.read(200)

def GoRight():
    print("Going right...")
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x80\x00'
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x80\x00')['lower']
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x80\x00')['upper'])
    ser.read(200)
    CheckReady()
    ser.read(200)
    CheckMove()
    ser.read(200)
    CheckAlarm()
    ser.read(200)

def Stop():
    print("Stopping...")
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x00'
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x00')['lower']
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x00')['upper'])
    ser.read(200)
    CheckReady()
    ser.read(200)
    CheckMove()
    ser.read(200)
    CheckAlarm()
    ser.read(200)

def GoHome():
    print("Going home!")
    ser.write(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x10'
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x10')['lower']
              + crc16.crc16(b'\x01\x10\x00\x7C\x00\x02\x04\x00\x00\x00\x10')['upper'])
    ser.read(200)

def Move(pos):
    print("Moving to:", pos)
    position = (ConvertSteps(float(pos)).to_bytes(4, 'big', signed=True))
    ser.write((b'\x01\x10\x18\x00\x00\x04\x08\x00\x00\x00\x01'+position)
              + crc16.crc16((b'\x01\x10\x18\x00\x00\x04\x08\x00\x00\x00\x01'+position))['lower']
              + crc16.crc16((b'\x01\x10\x18\x00\x00\x04\x08\x00\x00\x00\x01'+position))['upper'])
    ser.read(200)
    Execute()

def SetSpeed(spd):
    print("Speed set to:", spd)
    speed = (int(spd).to_bytes(4, 'big', signed=True))
    ser.write((b'\x01\x10\x18\x04\x00\x02\x04'+speed)
                  + crc16.crc16((b'\x01\x10\x18\x04\x00\x02\x04'+speed))['lower']
                  + crc16.crc16((b'\x01\x10\x18\x04\x00\x02\x04'+speed))['upper'])
    ser.read(200)

######################
#Driver output status#
######################
def CheckReady():
    ser.write(b'\x01\x03\x00\x7F\x00\x01'
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['lower']
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['upper'])
    if int.from_bytes(ser.read(200)[3:5], 'big') & 0b100000 == 0b100000:
        print("Ready!")
        return 1
    else:
        print("Not Ready!")
        return 0

def CheckMove():
    ser.write(b'\x01\x03\x00\x7F\x00\x01'
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['lower']
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['upper'])
    if int.from_bytes(ser.read(200)[3:5], 'big') & 0b10000000000000 == 0b10000000000000:
        print("Moving!")
        return 1
    else:
        return 0

def CheckAlarm():
    ser.write(b'\x01\x03\x00\x7F\x00\x01'
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['lower']
              + crc16.crc16(b'\x01\x03\x00\x7F\x00\x01')['upper'])
    if int.from_bytes(ser.read(200)[3:5], 'big') & 0b10000000 == 0b10000000:
        print("Alarm ON!")
        return 1
    else:
        return 0

def CheckPosition():
    ser.write(b'\x01\x03\x00\xCC\x00\x02'
              + crc16.crc16(b'\x01\x03\x00\xCC\x00\x02')['lower']
              + crc16.crc16(b'\x01\x03\x00\xCC\x00\x02')['upper'])
    print("Current position:", int.from_bytes(ser.read(200)[4:7], 'big')/100, "mm")
