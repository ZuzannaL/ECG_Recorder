#https://stackoverflow.com/questions/37252756/simplest-way-for-pyqt-threading

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import sys
from random import randint

from main import read_from_serial_port

class FileMonitor(QObject):

    image_signal = QtCore.pyqtSignal(int)

    @QtCore.pyqtSlot()
    def monitor_port(self):
        baudrate = 9600
        port = 'COM7'
        for x in read_from_serial_port(port, baudrate):
            self.image_signal.emit(x)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))
        self.y = [randint(0, 100) for _ in range(100)]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.file_monitor = FileMonitor()
        self.thread = QtCore.QThread(self)
        self.file_monitor.image_signal.connect(self.update_plot_data)
        self.file_monitor.moveToThread(self.thread)
        self.thread.started.connect(self.file_monitor.monitor_port)
        self.thread.start()

    @QtCore.pyqtSlot(int)
    def update_plot_data(self, data_point):
        self.x = self.x[1:]  # Remove the first y element.
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.

        self.y = self.y[1:]  # Remove the first
        self.y.append(data_point)  # Add a new random value.

        self.data_line.setData(self.x, self.y)  # Update the data.


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
w.show()
sys.exit(app.exec_())
