# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ECG_Recorder.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(716, 433)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton_recording = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_recording.setObjectName("pushButton_recording")
        self.horizontalLayout.addWidget(self.pushButton_recording)
        self.label_port = QtWidgets.QLabel(self.centralwidget)
        self.label_port.setObjectName("label_port")
        self.horizontalLayout.addWidget(self.label_port)
        self.comboBox_port = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_port.setObjectName("comboBox_port")
        self.horizontalLayout.addWidget(self.comboBox_port)
        self.label_baudrate = QtWidgets.QLabel(self.centralwidget)
        self.label_baudrate.setObjectName("label_baudrate")
        self.horizontalLayout.addWidget(self.label_baudrate)
        self.comboBox_baudrate = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_baudrate.setObjectName("comboBox_baudrate")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.comboBox_baudrate.addItem("")
        self.horizontalLayout.addWidget(self.comboBox_baudrate)
        self.label_filename = QtWidgets.QLabel(self.centralwidget)
        self.label_filename.setObjectName("label_filename")
        self.horizontalLayout.addWidget(self.label_filename)
        self.lineEdit_filename = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEdit_filename.sizePolicy().hasHeightForWidth())
        self.lineEdit_filename.setSizePolicy(sizePolicy)
        self.lineEdit_filename.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.lineEdit_filename.setObjectName("lineEdit_filename")
        self.horizontalLayout.addWidget(self.lineEdit_filename)
        self.checkBox_filtering = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_filtering.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.checkBox_filtering.setObjectName("checkBox_filtering")
        self.horizontalLayout.addWidget(self.checkBox_filtering)
        self.label_HR = QtWidgets.QLabel(self.centralwidget)
        self.label_HR.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_HR.setObjectName("label_HR")
        self.horizontalLayout.addWidget(self.label_HR)
        self.lcdNumber_HR = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber_HR.setObjectName("lcdNumber_HR")
        self.horizontalLayout.addWidget(self.lcdNumber_HR)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ECG Recorder"))
        self.pushButton_recording.setText(_translate("MainWindow", "Start Recording"))
        self.label_port.setText(_translate("MainWindow", "Port"))
        self.label_baudrate.setText(_translate("MainWindow", "Baudrate"))
        self.comboBox_baudrate.setCurrentText(_translate("MainWindow", "38400"))
        self.comboBox_baudrate.setItemText(0, _translate("MainWindow", "1200"))
        self.comboBox_baudrate.setItemText(1, _translate("MainWindow", "2400"))
        self.comboBox_baudrate.setItemText(2, _translate("MainWindow", "4800"))
        self.comboBox_baudrate.setItemText(3, _translate("MainWindow", "9600"))
        self.comboBox_baudrate.setItemText(4, _translate("MainWindow", "19200"))
        self.comboBox_baudrate.setItemText(5, _translate("MainWindow", "38400"))
        self.comboBox_baudrate.setItemText(6, _translate("MainWindow", "57600"))
        self.comboBox_baudrate.setItemText(7, _translate("MainWindow", "115200"))
        self.label_filename.setText(_translate("MainWindow", "Filename"))
        self.checkBox_filtering.setText(_translate("MainWindow", "Filtering"))
        self.label_HR.setText(_translate("MainWindow", "Heart Rate"))
