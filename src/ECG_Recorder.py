from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import sys
from datetime import datetime
from enum import auto, Enum
from pathlib import Path

from port_handler import read_from_serial_port, write_data_point_to_file
from gui.ECG_Recorder_ui import Ui_MainWindow

def create_default_filename():
    _data_folder = Path('../data/')
    return _data_folder/f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'

class System(Enum):
    LINUX = auto()
    WINDOWS = auto()

class Configuration:
    system = System.WINDOWS
    baudrate = 9600 #38400 #9600
    #filename = None
    if system == System.LINUX:
        port = '/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_066CFF575353898667173738-if02'
        #port = '/dev/pts/3'
    elif system == System.WINDOWS:
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
        _translate = QtCore.QCoreApplication.translate

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.comboBox_baudrate.setCurrentText(_translate("MainWindow", "9600"))
        self.setActions()

        self.graphWidget = pg.PlotWidget(self.ui.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphWidget.sizePolicy().hasHeightForWidth())
        self.graphWidget.setSizePolicy(sizePolicy)
        self.graphWidget.setObjectName("graphWidget")
        self.ui.verticalLayout_2.addWidget(self.graphWidget)

        self.x = [0]
        self.y = [0]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(0, 0, 255), width=1) #todo: it gives an error when width!=1 even though the plot looks ok
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        self.file = None
        self.user_filename = None
        self.filename = None
        self.recording = False

        self.port_monitor = PortMonitor()
        self.thread = QtCore.QThread(self)
        self.port_monitor.image_signal.connect(self.update_data)
        self.port_monitor.moveToThread(self.thread)
        self.thread.started.connect(self.port_monitor.monitor_port)
        self.thread.start()

    def setActions(self):
        self.ui.pushButton_recording.clicked.connect(self.startStopRecording)

    def startStopRecording(self):
        _translate = QtCore.QCoreApplication.translate
        if not self.recording:
            self.open_file()
            self.ui.pushButton_recording.setText(_translate("MainWindow", "Stop Recording"))
            self.ui.statusbar.showMessage(f'Saving data to file {self.filename}')
            self.recording = True
        else:
            self.close_file()
            self.ui.pushButton_recording.setText(_translate("MainWindow", "Start Recording"))
            self.ui.statusbar.showMessage(f'Data saved in {self.filename}', 5000)
            self.recording = False

    def open_file(self):
        if self.file is None:
            if self.user_filename is None:
                self.filename = create_default_filename()
            else:
                self.filename = self.user_filename
            self.file = open(self.filename, 'w')
            print(f'Saving data to file {self.filename}')

    def close_file(self):
        if self.file is not None:
            self.file.close()
            print(f'Data saved in {self.filename}')
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
            write_data_point_to_file(data_point, self.file)

def run():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
	run()