import time
from datetime import datetime
import serial


def read_from_serial_port(port):
    # configure the serial connections (the parameters differs on the device you are connecting to)
    ser = serial.Serial(
        port=port,
        baudrate=38400,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )

    ser.isOpen()

    print('Enter your commands below.\r\nInsert "exit" to leave the application.')

    filename = f'data/{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.txt'
    print(f'Saving to file {filename}')
    with open(filename, 'w') as file:
        while True:
            out = ''
            # let's wait one second before reading output (let's give device time to answer)
            time.sleep(1)
            while ser.inWaiting() > 0:
                out += ser.read(1).decode("utf-8")

            if out != '':
                #print(">>" + out)
                file.write(">>" + out)


if __name__ == '__main__':
    read_from_serial_port('/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066CFF575353898667173738-if02')


