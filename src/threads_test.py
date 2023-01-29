#https://stackoverflow.com/questions/37252756/simplest-way-for-pyqt-threading
#https://stackoverflow.com/questions/16243752/serial-port-does-not-work-in-rewritten-python-code

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import sys
from datetime import datetime
from enum import Enum

from main import read_from_serial_port


def write_to_file(x, file):
    out = ''
    out += str(x)+'\n'
    if out != '':
        file.write(out)

class System(Enum):
    LINUX = 'LINUX'
    WINDOWS = 'WINDOWS'

class Configuration:
    system = System.WINDOWS
    baudrate = 9600 #38400 #9600
    if system == System.LINUX:
        filename = f'../data/{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066CFF575353898667173738-if02'
        #port = '/dev/pts/3'
    elif system == System.WINDOWS:
        filename = f'..\data\{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'
        port = 'COM7'
    else:
        raise Exception("You didn't choose right system. Choose LINUX or WINDOWS.")



class PortMonitor(QObject):

    image_signal = QtCore.pyqtSignal(int)

    @QtCore.pyqtSlot()
    def monitor_port(self):
        baudrate = Configuration.baudrate
        port = Configuration.port
        for x in read_from_serial_port(port, baudrate):
            self.image_signal.emit(x)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = [0]
        self.y = [0]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(0, 0, 255), width=1) #todo: it gives an error when width!=1 even though the plot looks ok
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.file = None
        self.open_file()

        self.port_monitor = PortMonitor()
        self.thread = QtCore.QThread(self)
        self.port_monitor.image_signal.connect(self.update_data)
        self.port_monitor.moveToThread(self.thread)
        self.thread.started.connect(self.port_monitor.monitor_port)
        self.thread.start()

    def open_file(self):
        if self.file is None:
            self.file = open(Configuration.filename, 'w')
            print(f'Saving data to file {Configuration.filename}')

    def close_file(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def closeEvent(self, event):
        self.close_file()

    @QtCore.pyqtSlot(int)
    def update_data(self, data_point):
        if len(self.x) == 100:
            self.x = self.x[1:]  # Remove the first x element
            self.y = self.y[1:]  # Remove the first y element
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last
        self.y.append(data_point)  # Add a new value
        self.data_line.setData(self.x, self.y)  # Update the data

        if self.file is not None:
            write_to_file(data_point, self.file)



app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
