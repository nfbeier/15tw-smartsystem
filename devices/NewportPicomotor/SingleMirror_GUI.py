# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SingleMirror_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(376, 350)
        self.stepSize = QtWidgets.QSpinBox(Form)
        self.stepSize.setGeometry(QtCore.QRect(20, 100, 101, 41))
        self.stepSize.setMaximum(1000)
        self.stepSize.setObjectName("stepSize")
        self.ButtonUp = QtWidgets.QToolButton(Form)
        self.ButtonUp.setGeometry(QtCore.QRect(130, 100, 41, 41))
        self.ButtonUp.setArrowType(QtCore.Qt.UpArrow)
        self.ButtonUp.setObjectName("ButtonUp")
        self.ButtonDown = QtWidgets.QToolButton(Form)
        self.ButtonDown.setGeometry(QtCore.QRect(130, 150, 41, 41))
        self.ButtonDown.setArrowType(QtCore.Qt.DownArrow)
        self.ButtonDown.setObjectName("ButtonDown")
        self.ButtonRight = QtWidgets.QToolButton(Form)
        self.ButtonRight.setGeometry(QtCore.QRect(80, 150, 41, 41))
        self.ButtonRight.setArrowType(QtCore.Qt.RightArrow)
        self.ButtonRight.setObjectName("ButtonRight")
        self.ButtonLeft = QtWidgets.QToolButton(Form)
        self.ButtonLeft.setGeometry(QtCore.QRect(20, 150, 41, 41))
        self.ButtonLeft.setArrowType(QtCore.Qt.LeftArrow)
        self.ButtonLeft.setObjectName("ButtonLeft")
        self.Mirror_Label = QtWidgets.QLabel(Form)
        self.Mirror_Label.setGeometry(QtCore.QRect(30, 50, 101, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.Mirror_Label.setFont(font)
        self.Mirror_Label.setObjectName("Mirror_Label")
        self.yStepNumber = QtWidgets.QLCDNumber(Form)
        self.yStepNumber.setGeometry(QtCore.QRect(190, 130, 61, 41))
        self.yStepNumber.setDigitCount(5)
        self.yStepNumber.setObjectName("yStepNumber")
        self.xStepNumber = QtWidgets.QLCDNumber(Form)
        self.xStepNumber.setGeometry(QtCore.QRect(20, 200, 61, 41))
        self.xStepNumber.setObjectName("xStepNumber")
        self.yValueLabel = QtWidgets.QLabel(Form)
        self.yValueLabel.setGeometry(QtCore.QRect(180, 100, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.yValueLabel.setFont(font)
        self.yValueLabel.setObjectName("yValueLabel")
        self.xValueLabel = QtWidgets.QLabel(Form)
        self.xValueLabel.setGeometry(QtCore.QRect(90, 200, 81, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.xValueLabel.setFont(font)
        self.xValueLabel.setObjectName("xValueLabel")
        self.ButtonHome = QtWidgets.QPushButton(Form)
        self.ButtonHome.setGeometry(QtCore.QRect(180, 200, 75, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ButtonHome.setFont(font)
        self.ButtonHome.setObjectName("ButtonHome")
        self.connectionStatusLabel = QtWidgets.QLabel(Form)
        self.connectionStatusLabel.setGeometry(QtCore.QRect(90, 20, 201, 21))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.connectionStatusLabel.setFont(font)
        self.connectionStatusLabel.setObjectName("connectionStatusLabel")
        self.LEDindicator = QtWidgets.QLabel(Form)
        self.LEDindicator.setGeometry(QtCore.QRect(30, 20, 21, 21))
        self.LEDindicator.setStyleSheet("    background-color: red;\n"
"    border-radius: 10px;\n"
"    min-width: 20px;\n"
"    min-height: 20px;")
        self.LEDindicator.setText("")
        self.LEDindicator.setObjectName("LEDindicator")
        self.ButtonSafety = QtWidgets.QPushButton(Form)
        self.ButtonSafety.setGeometry(QtCore.QRect(20, 260, 41, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ButtonSafety.setFont(font)
        self.ButtonSafety.setObjectName("ButtonSafety")
        self.MirrorLockLabel = QtWidgets.QLabel(Form)
        self.MirrorLockLabel.setGeometry(QtCore.QRect(70, 270, 131, 21))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.MirrorLockLabel.setFont(font)
        self.MirrorLockLabel.setObjectName("MirrorLockLabel")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ButtonUp.setText(_translate("Form", "..."))
        self.ButtonDown.setText(_translate("Form", "..."))
        self.ButtonRight.setText(_translate("Form", "..."))
        self.ButtonLeft.setText(_translate("Form", "..."))
        self.Mirror_Label.setText(_translate("Form", "Mirror 1 "))
        self.yValueLabel.setText(_translate("Form", "Y value"))
        self.xValueLabel.setText(_translate("Form", "X value"))
        self.ButtonHome.setText(_translate("Form", "Home"))
        self.connectionStatusLabel.setText(_translate("Form", "Connected Controllers: 0 "))
        self.ButtonSafety.setText(_translate("Form", "OK"))
        self.MirrorLockLabel.setText(_translate("Form", " HIGH POWER MODE"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
