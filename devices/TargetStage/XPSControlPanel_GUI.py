# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\devices\TargetStage\XPSControlPanel_GUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(441, 412)
        self.XPSstatus = QtWidgets.QGroupBox(Form)
        self.XPSstatus.setGeometry(QtCore.QRect(10, 20, 151, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.XPSstatus.setFont(font)
        self.XPSstatus.setObjectName("XPSstatus")
        self.XPSstatusLabel = QtWidgets.QLabel(self.XPSstatus)
        self.XPSstatusLabel.setGeometry(QtCore.QRect(20, 30, 121, 31))
        self.XPSstatusLabel.setObjectName("XPSstatusLabel")
        self.InitializeXPS = QtWidgets.QPushButton(Form)
        self.InitializeXPS.setGeometry(QtCore.QRect(30, 110, 93, 41))
        self.InitializeXPS.setObjectName("InitializeXPS")
        self.HomeXPS = QtWidgets.QPushButton(Form)
        self.HomeXPS.setGeometry(QtCore.QRect(30, 180, 93, 41))
        self.HomeXPS.setObjectName("HomeXPS")
        self.EnableDisableXPS = QtWidgets.QPushButton(Form)
        self.EnableDisableXPS.setGeometry(QtCore.QRect(30, 250, 93, 41))
        self.EnableDisableXPS.setObjectName("EnableDisableXPS")
        self.KillAll = QtWidgets.QPushButton(Form)
        self.KillAll.setGeometry(QtCore.QRect(30, 320, 93, 41))
        self.KillAll.setObjectName("KillAll")
        self.XaxisLabel = QtWidgets.QLabel(Form)
        self.XaxisLabel.setGeometry(QtCore.QRect(200, 20, 61, 31))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.XaxisLabel.setFont(font)
        self.XaxisLabel.setObjectName("XaxisLabel")
        self.X_GroupNames = QtWidgets.QComboBox(Form)
        self.X_GroupNames.setGeometry(QtCore.QRect(280, 90, 121, 21))
        self.X_GroupNames.setObjectName("X_GroupNames")
        self.GroupNameLabel = QtWidgets.QLabel(Form)
        self.GroupNameLabel.setGeometry(QtCore.QRect(170, 60, 81, 21))
        self.GroupNameLabel.setObjectName("GroupNameLabel")
        self.RelativeMoveLabel = QtWidgets.QLabel(Form)
        self.RelativeMoveLabel.setGeometry(QtCore.QRect(170, 130, 121, 21))
        self.RelativeMoveLabel.setObjectName("RelativeMoveLabel")
        self.X_RightRelativeMoveButton = QtWidgets.QPushButton(Form)
        self.X_RightRelativeMoveButton.setGeometry(QtCore.QRect(330, 160, 71, 31))
        self.X_RightRelativeMoveButton.setObjectName("X_RightRelativeMoveButton")
        self.RelativeMoveValue = QtWidgets.QDoubleSpinBox(Form)
        self.RelativeMoveValue.setGeometry(QtCore.QRect(250, 160, 71, 31))
        self.RelativeMoveValue.setDecimals(3)
        self.RelativeMoveValue.setProperty("value", 0.0)
        self.RelativeMoveValue.setObjectName("RelativeMoveValue")
        self.X_LeftRelativeMoveButton = QtWidgets.QPushButton(Form)
        self.X_LeftRelativeMoveButton.setGeometry(QtCore.QRect(170, 160, 71, 31))
        self.X_LeftRelativeMoveButton.setObjectName("X_LeftRelativeMoveButton")
        self.AbsoluteMoveLabel = QtWidgets.QLabel(Form)
        self.AbsoluteMoveLabel.setGeometry(QtCore.QRect(170, 210, 121, 21))
        self.AbsoluteMoveLabel.setObjectName("AbsoluteMoveLabel")
        self.AbsoluteMoveValue = QtWidgets.QDoubleSpinBox(Form)
        self.AbsoluteMoveValue.setGeometry(QtCore.QRect(170, 240, 71, 31))
        self.AbsoluteMoveValue.setDecimals(3)
        self.AbsoluteMoveValue.setObjectName("AbsoluteMoveValue")
        self.X_AbsoluteMoveButton = QtWidgets.QPushButton(Form)
        self.X_AbsoluteMoveButton.setGeometry(QtCore.QRect(270, 240, 71, 31))
        self.X_AbsoluteMoveButton.setObjectName("X_AbsoluteMoveButton")
        self.PositionLabel = QtWidgets.QLabel(Form)
        self.PositionLabel.setGeometry(QtCore.QRect(170, 290, 91, 21))
        self.PositionLabel.setObjectName("PositionLabel")
        self.PositionValue = QtWidgets.QLCDNumber(Form)
        self.PositionValue.setGeometry(QtCore.QRect(270, 280, 61, 41))
        self.PositionValue.setSmallDecimalPoint(False)
        self.PositionValue.setProperty("value", 0.0)
        self.PositionValue.setObjectName("PositionValue")
        self.MinTravelLabel = QtWidgets.QLabel(Form)
        self.MinTravelLabel.setGeometry(QtCore.QRect(170, 340, 141, 21))
        self.MinTravelLabel.setObjectName("MinTravelLabel")
        self.MinTravelValue = QtWidgets.QLineEdit(Form)
        self.MinTravelValue.setGeometry(QtCore.QRect(310, 340, 71, 22))
        self.MinTravelValue.setObjectName("MinTravelValue")
        self.MaxTravelLabel = QtWidgets.QLabel(Form)
        self.MaxTravelLabel.setGeometry(QtCore.QRect(170, 370, 141, 21))
        self.MaxTravelLabel.setObjectName("MaxTravelLabel")
        self.MaxTravelValue = QtWidgets.QLineEdit(Form)
        self.MaxTravelValue.setGeometry(QtCore.QRect(310, 370, 71, 22))
        self.MaxTravelValue.setObjectName("MaxTravelValue")
        self.RefreshGroupsButton = QtWidgets.QPushButton(Form)
        self.RefreshGroupsButton.setGeometry(QtCore.QRect(170, 80, 101, 41))
        self.RefreshGroupsButton.setObjectName("RefreshGroupsButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.XPSstatus.setTitle(_translate("Form", "XPS Status"))
        self.XPSstatusLabel.setText(_translate("Form", "Not Initialized"))
        self.InitializeXPS.setText(_translate("Form", "Initialize XPS"))
        self.HomeXPS.setText(_translate("Form", "Home XPS"))
        self.EnableDisableXPS.setText(_translate("Form", "Enable XPS"))
        self.KillAll.setText(_translate("Form", "Kill All"))
        self.XaxisLabel.setText(_translate("Form", "X-Axis"))
        self.GroupNameLabel.setText(_translate("Form", "Group Name:"))
        self.RelativeMoveLabel.setText(_translate("Form", "Relative Move (mm)"))
        self.X_RightRelativeMoveButton.setText(_translate("Form", "Right"))
        self.X_LeftRelativeMoveButton.setText(_translate("Form", "Left"))
        self.AbsoluteMoveLabel.setText(_translate("Form", "Absolute Move (mm)"))
        self.X_AbsoluteMoveButton.setText(_translate("Form", "Move"))
        self.PositionLabel.setText(_translate("Form", "Position (mm):"))
        self.MinTravelLabel.setText(_translate("Form", "Minimum Travel (mm):"))
        self.MaxTravelLabel.setText(_translate("Form", "Maximum Travel (mm):"))
        self.RefreshGroupsButton.setText(_translate("Form", "Refresh Groups"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
