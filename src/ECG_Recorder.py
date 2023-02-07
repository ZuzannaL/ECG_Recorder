from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QObject
import pyqtgraph as pg
import sys
from datetime import datetime
from pathlib import Path
import serial
import numpy as np

from port_handler import read_from_serial_port, write_data_point_to_file, find_available_ports
from signal_processor import SignalProcessor
from gui.ECG_Recorder_ui import Ui_MainWindow

def create_default_filename():
    _data_folder = Path('../data/')
    return _data_folder/f'{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.txt'

class Configuration:
    baudrate = 38400 #38400 #9600
    port = None
    Fs = 200
    data_points_number_in_the_plot = 3*Fs
    data_points_number_in_the_buffer = 10*Fs
    filtering = False

class PortMonitor(QObject):

    image_signal = QtCore.pyqtSignal(int)

    @QtCore.pyqtSlot()
    def monitor_port(self):
        while True:
            try:
                baudrate = Configuration.baudrate
                port = Configuration.port
                for x in read_from_serial_port(port, baudrate):
                    self.image_signal.emit(x)
                    if (baudrate, port) != (Configuration.baudrate, Configuration.port):
                        break
            except serial.serialutil.SerialException as e:
                print(e)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self._translate = QtCore.QCoreApplication.translate

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.comboBox_baudrate.setCurrentText(self._translate("MainWindow", str(Configuration.baudrate)))
        self.ui.lcdNumber_HR.display('---')
        self.setupGraphWidget()

        self.file = None
        self.user_filename = None
        self.filename = None
        self.recording = False
        self.ports = find_available_ports()
        self.sp = SignalProcessor(Configuration.Fs)
        self.buffer = [0]
        self.neverending_buffer = [0]

        self.updatePortsList()
        Configuration.port = self.ports[0]
        self.setActions()

        self.port_monitor = PortMonitor()
        self.thread = QtCore.QThread(self)
        self.port_monitor.image_signal.connect(self.update_data)
        self.port_monitor.moveToThread(self.thread)
        self.thread.started.connect(self.port_monitor.monitor_port)
        self.thread.start()

    def setupGraphWidget(self):
        self.graphWidget = pg.PlotWidget(self.ui.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphWidget.sizePolicy().hasHeightForWidth())
        self.graphWidget.setSizePolicy(sizePolicy)
        self.graphWidget.setMinimumSize(QtCore.QSize(600, 0))
        self.graphWidget.setObjectName("graphWidget")
        self.ui.verticalLayout_1.addWidget(self.graphWidget)

        self.x = [0]
        self.y = [0]

        self.graphWidget.setBackground('w')

        pen = pg.mkPen(color=(0, 0, 255), width=1) #todo: it gives an error when width!=1 even though the plot looks ok
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

    def updatePortsList(self):
        for i in range(len(self.ports)):
            self.ui.comboBox_port.addItem("")
        for i, port in enumerate(self.ports):
            self.ui.comboBox_port.setItemText(i, self._translate("MainWindow", port))

    def setActions(self):
        self.ui.pushButton_recording.clicked.connect(self.startStopRecording)
        self.ui.comboBox_port.activated.connect(self.choosePort)
        self.ui.comboBox_baudrate.activated.connect(self.chooseBaudrate)
        self.ui.lineEdit_filename.editingFinished.connect(self.chooseFilename)
        self.ui.checkBox_filtering.stateChanged.connect(self.setFiltering)

    def startStopRecording(self):
        if not self.recording:
            self.open_file()
            self.ui.pushButton_recording.setText(self._translate("MainWindow", "Stop Recording"))
            self.ui.statusbar.showMessage(f'Saving data to file {self.filename}')
            print(f'Saving data to file {self.filename}')
            self.recording = True
        else:
            self.close_file()
            self.ui.pushButton_recording.setText(self._translate("MainWindow", "Start Recording"))
            self.ui.statusbar.showMessage(f'Data saved in {self.filename}', 5000)
            print(f'Data saved in {self.filename}')
            self.recording = False

    def choosePort(self):
        for port in self.ports:
            if self.ui.comboBox_port.currentText() == port:
                Configuration.port = port
                self.ui.statusbar.showMessage(f'Setting port to {port}', 5000)
                print(f'Setting port to {port}')

    def chooseBaudrate(self):
        all_baudrates = [self.ui.comboBox_baudrate.itemText(i) for i in range(self.ui.comboBox_baudrate.count())]
        for baudrate in all_baudrates:
            if self.ui.comboBox_baudrate.currentText() == baudrate:
                Configuration.baudrate = int(baudrate)
                self.ui.statusbar.showMessage(f'Setting baudrate to {baudrate}', 5000)
                print(f'Setting baudrate to {baudrate}')

    def chooseFilename(self):
        self.user_filename = self.ui.lineEdit_filename.text()
        self.ui.statusbar.showMessage(f'Setting filename to {self.user_filename}', 5000)
        print(f'Setting filename to {self.user_filename}')

    def setFiltering(self, state):
        if state == QtCore.Qt.Checked:
            Configuration.filtering = True
            self.ui.statusbar.showMessage(f'Filtering on', 5000)
            print(f'Filtering on')
        else:
            Configuration.filtering = False
            self.ui.statusbar.showMessage(f'Filtering off', 5000)
            print(f'Filtering off')

    def showHR(self):
        if len(self.buffer) >= Configuration.data_points_number_in_the_buffer:
            hr = self.sp.find_hr(self.buffer)
            if np.isnan(hr):
                self.ui.lcdNumber_HR.display('---')
            else:
                self.ui.lcdNumber_HR.display(hr)

    @staticmethod
    def create_heart_measures_display_text(measures):
        keys = ['bpm', 'ibi', 'sdnn', 'sdsd', 'rmssd', 'pnn20', 'pnn50', 'hr_mad', 'sd1', 'sd2', 's', 'sd1/sd2']
        displayed_measures = {}
        for key in keys:
            if not np.isnan(measures[key]):
                displayed_measures[key] = '{:.2f}'.format(measures[key])
            else:
                displayed_measures[key] = '--'
        displayed_text = f"<html><head/><body><p><span style=\" font-size:8pt;\">ECG measures:<br/>average hr: {displayed_measures['bpm']}<br/>ibi: {displayed_measures['ibi']}<br/>sdnn: {displayed_measures['sdnn']}<br/>sdsd: {displayed_measures['sdsd']}<br/>rmssd: {displayed_measures['rmssd']}<br/>pnn20: {displayed_measures['pnn20']}<br/>pnn50: {displayed_measures['pnn50']}<br/>hr mad: {displayed_measures['hr_mad']}<br/>sd1: {displayed_measures['sd1']}<br/>sd2: {displayed_measures['sd2']}<br/>s: {displayed_measures['s']}<br/>sd1/sd2: {displayed_measures['sd1/sd2']}</span></p></body></html>"
        return displayed_text


    def showECGAnalysis(self):
        if len(self.neverending_buffer) >= Configuration.data_points_number_in_the_buffer:
            measures = self.sp.make_ecg_analysis(np.array(self.neverending_buffer))
            if measures is None:
                return
            displayed_text = self.create_heart_measures_display_text(measures)
            self.ui.label_ecg_measures.setText(displayed_text)

    def open_file(self):
        if self.file is None:
            if self.user_filename is None or self.user_filename == '':
                self.filename = create_default_filename()
            else:
                self.filename = self.user_filename
            self.file = open(self.filename, 'w')

    def close_file(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    def closeEvent(self, event):
        self.close_file()

    @QtCore.pyqtSlot(int)
    def update_data(self, data_point):
        if Configuration.filtering: # todo decide if data given to heartpy methods will be filtered or raw
            data_point = self.sp.use_all_filters(data_point)

        if len(self.buffer) == Configuration.data_points_number_in_the_buffer:
            self.buffer = self.buffer[1:]
        self.buffer.append(data_point)
        if self.x[-1] % (1*Configuration.Fs) == 0:
            self.showHR()

        self.neverending_buffer.append(data_point)
        if self.x[-1] % (10*Configuration.Fs) == 0:
            self.showECGAnalysis()

        if len(self.x) == Configuration.data_points_number_in_the_plot:
            self.x = self.x[1:]  # Remove the first x element
            self.y = self.y[1:]  # Remove the first y element
        self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last - x-axis in numbers of samples
        self.y.append(data_point)  # Add a new value
        x_in_seconds = np.array(self.x)/Configuration.Fs
        self.data_line.setData(x_in_seconds, self.y)  # Update the data

        if self.file is not None:
            write_data_point_to_file(data_point, self.file)

def run():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
	run()