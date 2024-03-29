from datetime import datetime
import serial
from serial.tools.list_ports import comports


def convert_units_to_volts(value, adc_resolution=12, max_voltage=3.3):
    quantization_level = 2**adc_resolution
    max_value = quantization_level-1
    return value / max_value * max_voltage


def find_available_ports():
    return [port.name for port in comports()]


def read_from_serial_port(port, baudrate):
    # device-dependent configuration of serial connection
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=serial.PARITY_ODD,
        stopbits=serial.STOPBITS_TWO,
        bytesize=serial.SEVENBITS
    )
    ser.isOpen()

    value = ''
    while True:
        while ser.inWaiting() > 0:
            x = ser.read(1).decode("utf-8")
            if x.isdigit():
                value += x
            else:
                if value != '':
                    yield float(value)
                    value = ''
                else:
                    continue


def write_all_data_to_file(filename, port, baudrate):
    print(f'Saving to file {filename}')
    with open(filename, 'w') as file:
        for x in read_from_serial_port(port, baudrate):
            out = ''
            out += str(x)+'\n'
            if out != '':
                file.write(out)


def write_data_point_to_file(x, file):
    out = ''
    out += str(x)+'\n'
    if out != '':
        file.write(out)

def main():
    from enum import auto, Enum

    class System(Enum):
        LINUX = auto()
        WINDOWS = auto()

    baudrate = 38400
    system = System.WINDOWS

    if system == System.LINUX:
        filename = f'../data/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066CFF575353898667173738-if02'
        # port = '/dev/pts/3'
    elif system == System.WINDOWS:
        filename = f'..\data\{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = 'COM7'
    else:
        raise Exception("You didn't choose write system. Choose LINUX or WINDOWS.")

    write_all_data_to_file(filename, port, baudrate)


if __name__ == '__main__':
    main()

