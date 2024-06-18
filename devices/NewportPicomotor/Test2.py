# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 11:32:10 2024

@author: BD-1
"""

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Mirror1_test2.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

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
        self.Mirror1_Label = QtWidgets.QLabel(Form)
        self.Mirror1_Label.setGeometry(QtCore.QRect(150, 60, 91, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Mirror1_Label.setFont(font)
        self.Mirror1_Label.setObjectName("Mirror1_Label")
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

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ButtonUp.setText(_translate("Form", "..."))
        self.ButtonDown.setText(_translate("Form", "..."))
        self.ButtonRight.setText(_translate("Form", "..."))
        self.ButtonLeft.setText(_translate("Form", "..."))
        self.Mirror1_Label.setText(_translate("Form", "Mirror 1"))
        self.yValueLabel.setText(_translate("Form", "Y value"))
        self.xValueLabel.setText(_translate("Form", "X value"))


#if __name__ == "__main__":
#    app = QtWidgets.QApplication(sys.argv)
#    Form = QtWidgets.QWidget()
#    ui = Ui_Form()
#    ui.setupUi(Form)
#    Form.show()
#    sys.exit(app.exec_())
    
#cwd = os.getcwd()
#print(cwd)
#sys.path.insert(0, os.getcwd())

#from devices.NewportPicomotor.picoWidgetTest_GUI import Ui_Form

class picoMotor_App(QtWidgets.QWidget):
    def __init__(self, axes):
        super(picoMotor_App, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.xAxis = axes[0]
        self.yAxis = axes[1]
        self.x_steps = 0
        self.y_steps = 0
        
        try:
            self.stage = Newport.Picomotor8742()
        except Newport.base.NewportBackendError:
            print("Newport Picomotor controller could not be initialized.")
            self.stage = None
        
        self.ui.ButtonLeft.clicked.connect(lambda: self.movePico(axis=self.xAxis, steps=-self.ui.stepSize.value()))
        self.ui.ButtonRight.clicked.connect(lambda: self.movePico(axis=self.xAxis, steps=self.ui.stepSize.value()))
        self.ui.ButtonUp.clicked.connect(lambda: self.movePico(axis=self.yAxis, steps=self.ui.stepSize.value()))
        self.ui.ButtonDown.clicked.connect(lambda: self.movePico(axis=self.yAxis, steps=-self.ui.stepSize.value()))

    def movePico(self, axis, steps):
        if self.stage:
            self.stage.move_by(axis=axis, steps=steps)
            self.stage.wait_move()
            if axis == self.xAxis:
                self.x_steps += steps
                self.ui.xStepNumber.display(self.x_steps)
            elif axis == self.yAxis:
                self.y_steps += steps
                self.ui.yStepNumber.display(self.y_steps)

    def closeEvent(self, event):
        if self.stage:
            self.stage.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = picoMotor_App([3, 4])
    application.show()
    sys.exit(app.exec_())
