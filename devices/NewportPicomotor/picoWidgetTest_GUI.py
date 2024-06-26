# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mirrorWidgetTest.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(230, 196)
        self.buttonUp = QtWidgets.QToolButton(Form)
        self.buttonUp.setGeometry(QtCore.QRect(140, 60, 51, 51))
        self.buttonUp.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.buttonUp.setAutoRaise(False)
        self.buttonUp.setArrowType(QtCore.Qt.UpArrow)
        self.buttonUp.setObjectName("buttonUp")
        self.buttonDown = QtWidgets.QToolButton(Form)
        self.buttonDown.setGeometry(QtCore.QRect(140, 120, 51, 51))
        self.buttonDown.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.buttonDown.setAutoRaise(False)
        self.buttonDown.setArrowType(QtCore.Qt.DownArrow)
        self.buttonDown.setObjectName("buttonDown")
        self.buttonLeft = QtWidgets.QToolButton(Form)
        self.buttonLeft.setGeometry(QtCore.QRect(20, 120, 51, 51))
        self.buttonLeft.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.buttonLeft.setAutoRaise(False)
        self.buttonLeft.setArrowType(QtCore.Qt.LeftArrow)
        self.buttonLeft.setObjectName("buttonLeft")
        self.buttonRight = QtWidgets.QToolButton(Form)
        self.buttonRight.setGeometry(QtCore.QRect(80, 120, 51, 51))
        self.buttonRight.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.buttonRight.setAutoRaise(False)
        self.buttonRight.setArrowType(QtCore.Qt.RightArrow)
        self.buttonRight.setObjectName("buttonRight")
        self.stepSize = QtWidgets.QSpinBox(Form)
        self.stepSize.setGeometry(QtCore.QRect(20, 70, 111, 41))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.stepSize.setFont(font)
        self.stepSize.setSuffix("")
        self.stepSize.setMaximum(1000)
        self.stepSize.setProperty("value", 100)
        self.stepSize.setObjectName("stepSize")
        self.mirrorName = QtWidgets.QLabel(Form)
        self.mirrorName.setGeometry(QtCore.QRect(20, 20, 141, 31))
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.mirrorName.setFont(font)
        self.mirrorName.setObjectName("mirrorName")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.buttonUp.setText(_translate("Form", "..."))
        self.buttonDown.setText(_translate("Form", "..."))
        self.buttonLeft.setText(_translate("Form", "..."))
        self.buttonRight.setText(_translate("Form", "..."))
        self.mirrorName.setText(_translate("Form", "Mirror 1"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
