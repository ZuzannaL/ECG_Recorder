from datetime import datetime
import serial
from enum import Enum
import time

class System(Enum):
    LINUX = 'LINUX'
    WINDOWS = 'WINDOWS'

def read_from_serial_port(port, baudrate, **kwargs):
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )
    ser.isOpen()

    while True:
        # let's wait one second before reading output (let's give device time to answer)
        time.sleep(1) #todo: why it is needed
        value = ''
        while ser.inWaiting() > 0:
            x = ser.read(1).decode("utf-8")
            if x.isdigit():
                value += x
            else:
                if value != '':
                    yield int(value)
                    value = ''
                else:
                    continue

def write_to_file(filename, port, baudrate):
    print(f'Saving to file {filename}')
    with open(filename, 'w') as file:
        for x in read_from_serial_port(port, baudrate):
            out = ''
            out += str(x)+'\n'
            if out != '':
                file.write(out)

if __name__ == '__main__':
    baudrate = 9600 #38400
    system = System.WINDOWS

    if system==System.LINUX:
        filename = f'data/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066CFF575353898667173738-if02'
        #port = '/dev/pts/3'
    elif system==System.WINDOWS:
        filename = f'data\{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = 'COM7'
    else:
        raise Exception("You didn't choose write system. Choose LINUX or WINDOWS.")

    write_to_file(filename, port, baudrate)


