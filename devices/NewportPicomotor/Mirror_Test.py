# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 10:14:28 2024

@author: BD-1
"""

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from pylablib.devices import Newport
import sys, os


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(785, 432)
        self.stepSize = QtWidgets.QSpinBox(Form)
        self.stepSize.setGeometry(QtCore.QRect(140, 110, 101, 41))
        self.stepSize.setMaximum(1000)
        self.stepSize.setObjectName("stepSize")
        self.ButtonUp = QtWidgets.QToolButton(Form)
        self.ButtonUp.setGeometry(QtCore.QRect(260, 110, 41, 41))
        self.ButtonUp.setArrowType(QtCore.Qt.UpArrow)
        self.ButtonUp.setObjectName("ButtonUp")
        self.ButtonDown = QtWidgets.QToolButton(Form)
        self.ButtonDown.setGeometry(QtCore.QRect(260, 160, 41, 41))
        self.ButtonDown.setArrowType(QtCore.Qt.DownArrow)
        self.ButtonDown.setObjectName("ButtonDown")
        self.ButtonRight = QtWidgets.QToolButton(Form)
        self.ButtonRight.setGeometry(QtCore.QRect(200, 160, 41, 41))
        self.ButtonRight.setArrowType(QtCore.Qt.RightArrow)
        self.ButtonRight.setObjectName("ButtonRight")
        self.ButtonLeft = QtWidgets.QToolButton(Form)
        self.ButtonLeft.setGeometry(QtCore.QRect(140, 160, 41, 41))
        self.ButtonLeft.setArrowType(QtCore.Qt.LeftArrow)
        self.ButtonLeft.setObjectName("ButtonLeft")
        self.Mirror_Label = QtWidgets.QLabel(Form)
        self.Mirror_Label.setGeometry(QtCore.QRect(150, 60, 91, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Mirror_Label.setFont(font)
        self.Mirror_Label.setObjectName("Mirror_Label")
        self.yStepNumber = QtWidgets.QLCDNumber(Form)
        self.yStepNumber.setGeometry(QtCore.QRect(320, 130, 61, 41))
        self.yStepNumber.setDigitCount(5)
        self.yStepNumber.setObjectName("yStepNumber")
        self.xStepNumber = QtWidgets.QLCDNumber(Form)
        self.xStepNumber.setGeometry(QtCore.QRect(160, 220, 61, 41))
        self.xStepNumber.setObjectName("xStepNumber")
        self.yValueLabel = QtWidgets.QLabel(Form)
        self.yValueLabel.setGeometry(QtCore.QRect(330, 80, 81, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.yValueLabel.setFont(font)
        self.yValueLabel.setObjectName("yValueLabel")
        self.xValueLabel = QtWidgets.QLabel(Form)
        self.xValueLabel.setGeometry(QtCore.QRect(230, 220, 81, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.xValueLabel.setFont(font)
        self.xValueLabel.setObjectName("xValueLabel")
        self.ButtonHome = QtWidgets.QPushButton(Form)
        self.ButtonHome.setGeometry(QtCore.QRect(320, 220, 75, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ButtonHome.setFont(font)
        self.ButtonHome.setObjectName("ButtonHome")
        self.TurningBox = QtWidgets.QComboBox(Form)
        self.TurningBox.setGeometry(QtCore.QRect(10, 130, 111, 51))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.TurningBox.setFont(font)
        self.TurningBox.setObjectName("TurningBox")
        self.TurningBox.addItem("")
        self.TurningBox.addItem("")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ButtonUp.setText(_translate("Form", "..."))
        self.ButtonDown.setText(_translate("Form", "..."))
        self.ButtonRight.setText(_translate("Form", "..."))
        self.ButtonLeft.setText(_translate("Form", "..."))
        self.Mirror_Label.setText(_translate("Form", "Mirror 1"))
        self.yValueLabel.setText(_translate("Form", "Y value"))
        self.xValueLabel.setText(_translate("Form", "X value"))
        self.ButtonHome.setText(_translate("Form", "Home"))
        self.TurningBox.setItemText(0, _translate("Form", "TURNING BOX 1"))
        self.TurningBox.setItemText(1, _translate("Form", "TURNING BOX 2"))


class picoMotor_App(QtWidgets.QWidget):
    def __init__(self, axes, mirror_label):
        super(picoMotor_App, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.xAxis = axes[0]
        self.yAxis = axes[1]
        self.ui.Mirror_Label.setText(mirror_label)

        try:
            self.stage = Newport.Picomotor8742()
        except Newport.base.NewportBackendError:
            print("Newport Picomotor controller could not be initialized.")
            self.stage = None

        self.ui.ButtonLeft.clicked.connect(lambda: self.movePico(axis=self.xAxis, steps=-self.ui.stepSize.value()))
        self.ui.ButtonRight.clicked.connect(lambda: self.movePico(axis=self.xAxis, steps=self.ui.stepSize.value()))
        self.ui.ButtonUp.clicked.connect(lambda: self.movePico(axis=self.yAxis, steps=self.ui.stepSize.value()))
        self.ui.ButtonDown.clicked.connect(lambda: self.movePico(axis=self.yAxis, steps=-self.ui.stepSize.value()))
        self.ui.ButtonHome.clicked.connect(self.moveToHome)

    def movePico(self, axis, steps):
        if self.stage:
            self.stage.move_by(axis=axis, steps=steps)
            self.stage.wait_move()
            if axis == self.xAxis:
                self.ui.xStepNumber.display(self.stage.get_position(self.xAxis))
            elif axis == self.yAxis:
                self.ui.yStepNumber.display(self.stage.get_position(self.yAxis))

    def moveToHome(self):
        if self.stage:
            # Move x-axis to home
            self.stage.move_to(axis=self.xAxis, position=0)
            self.stage.wait_move()
            # Move y-axis to home
            self.stage.move_to(axis=self.yAxis, position=0)
            self.stage.wait_move()
            # Reset step counters
            self.ui.xStepNumber.display(self.stage.get_position(self.xAxis))
            self.ui.yStepNumber.display(self.stage.get_position(self.yAxis))

    def closeEvent(self, event):
        if self.stage:
            self.stage.close()
        event.accept()


class MainController(QtWidgets.QWidget):
    def __init__(self):
        super(MainController, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.current_app = None
        self.ui.TurningBox.currentIndexChanged.connect(self.switchApplication)
        self.switchApplication()

    def switchApplication(self):
        if self.current_app:
            self.current_app.close()
            self.current_app.deleteLater()

        if self.ui.TurningBox.currentIndex() == 0:
            self.current_app = picoMotor_App([1, 2], "Mirror 1")
        else:
            self.current_app = picoMotor_App([3, 4], "Mirror 2")

        self.current_app.setParent(self)
        self.current_app.setGeometry(self.rect())
        self.current_app.show()

    def closeEvent(self, event):
        if self.current_app:
            self.current_app.close()
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_controller = MainController()
    main_controller.show()
    sys.exit(app.exec_())
