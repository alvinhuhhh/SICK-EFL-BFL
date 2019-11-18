#Testing
test1 = b'\x02'
test2 = b'\x02\x07'
test3 = b'\x01\x10\x18\x00\x00\x02\x04\x00\x00\x00\x02'

def crc16(data): #data = type bytes
    result = 0xffff
    
    for i in range(len(data)):
        current = data[i]
        result = calc(current, result)

    if len(hex(result)) < 6:
        upper = '0' + hex(result)[2]
        lower = hex(result)[3:5]
    else:
        upper = hex(result)[2:4]
        lower = hex(result)[4:7]

    return {'upper': bytes.fromhex(upper), 'lower': bytes.fromhex(lower)}


def calc(data, prv): #data = type int
    crc16 = data ^ prv
        
    for i in range(8):
        lsb = str(bin(crc16))[-1]
        crc16 = crc16 >> 1
        if lsb == '1':
            crc16 ^= 0xa001 #XOR with 0xa001 if bit shifted out is 1

    return crc16

##print(crc16(test1))
##print(crc16(test2))
##print(crc16(test3))

#Correct answers
#calc(0x02) = 33086
#calc(0x02\0x07) = 4673
#calc(x01\x10\x18\x00\x00\x02\x04\x00\x00\x00\x02) = 28376
