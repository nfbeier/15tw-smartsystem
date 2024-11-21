# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\devices\Iris\irisWidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(758, 234)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ComPortLabel = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ComPortLabel.sizePolicy().hasHeightForWidth())
        self.ComPortLabel.setSizePolicy(sizePolicy)
        self.ComPortLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ComPortLabel.setObjectName("ComPortLabel")
        self.verticalLayout.addWidget(self.ComPortLabel)
        self.ComPortSelectBox = QtWidgets.QComboBox(Form)
        self.ComPortSelectBox.setObjectName("ComPortSelectBox")
        self.verticalLayout.addWidget(self.ComPortSelectBox)
        self.comPortConnectButton = QtWidgets.QPushButton(Form)
        self.comPortConnectButton.setObjectName("comPortConnectButton")
        self.verticalLayout.addWidget(self.comPortConnectButton)
        self.fireButton = QtWidgets.QPushButton(Form)
        self.fireButton.setObjectName("fireButton")
        self.verticalLayout.addWidget(self.fireButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.IrisWidget = QtWidgets.QWidget(Form)
        self.IrisWidget.setObjectName("IrisWidget")
        self.layoutWidget = QtWidgets.QWidget(self.IrisWidget)
        self.layoutWidget.setGeometry(QtCore.QRect(120, 20, 111, 91))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.homeIrisButton = QtWidgets.QPushButton(self.layoutWidget)
        self.homeIrisButton.setObjectName("homeIrisButton")
        self.verticalLayout_2.addWidget(self.homeIrisButton)
        self.openIrisButton = QtWidgets.QPushButton(self.layoutWidget)
        self.openIrisButton.setObjectName("openIrisButton")
        self.verticalLayout_2.addWidget(self.openIrisButton)
        self.closeIrisButton = QtWidgets.QPushButton(self.layoutWidget)
        self.closeIrisButton.setObjectName("closeIrisButton")
        self.verticalLayout_2.addWidget(self.closeIrisButton)
        self.layoutWidget_2 = QtWidgets.QWidget(self.IrisWidget)
        self.layoutWidget_2.setGeometry(QtCore.QRect(10, 153, 221, 41))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.layoutWidget_2)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.currentDiameterLabel = QtWidgets.QLabel(self.layoutWidget_2)
        self.currentDiameterLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.currentDiameterLabel.setObjectName("currentDiameterLabel")
        self.verticalLayout_3.addWidget(self.currentDiameterLabel)
        self.layoutWidget_3 = QtWidgets.QWidget(self.IrisWidget)
        self.layoutWidget_3.setGeometry(QtCore.QRect(10, 120, 223, 25))
        self.layoutWidget_3.setObjectName("layoutWidget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.goToDiameterButton = QtWidgets.QPushButton(self.layoutWidget_3)
        self.goToDiameterButton.setObjectName("goToDiameterButton")
        self.horizontalLayout.addWidget(self.goToDiameterButton)
        self.goToDiameterEntry = QtWidgets.QLineEdit(self.layoutWidget_3)
        self.goToDiameterEntry.setText("")
        self.goToDiameterEntry.setObjectName("goToDiameterEntry")
        self.horizontalLayout.addWidget(self.goToDiameterEntry)
        self.layoutWidget_6 = QtWidgets.QWidget(self.IrisWidget)
        self.layoutWidget_6.setGeometry(QtCore.QRect(10, 20, 101, 91))
        self.layoutWidget_6.setObjectName("layoutWidget_6")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.layoutWidget_6)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.iris1label = QtWidgets.QLabel(self.layoutWidget_6)
        self.iris1label.setAlignment(QtCore.Qt.AlignCenter)
        self.iris1label.setObjectName("iris1label")
        self.verticalLayout_7.addWidget(self.iris1label)
        self.horizontalLayout_3.addWidget(self.IrisWidget)
        self.IrisWidget_2 = QtWidgets.QWidget(Form)
        self.IrisWidget_2.setObjectName("IrisWidget_2")
        self.layoutWidget_4 = QtWidgets.QWidget(self.IrisWidget_2)
        self.layoutWidget_4.setGeometry(QtCore.QRect(120, 20, 111, 91))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.homeIrisButton_2 = QtWidgets.QPushButton(self.layoutWidget_4)
        self.homeIrisButton_2.setObjectName("homeIrisButton_2")
        self.verticalLayout_4.addWidget(self.homeIrisButton_2)
        self.openIrisButton_2 = QtWidgets.QPushButton(self.layoutWidget_4)
        self.openIrisButton_2.setObjectName("openIrisButton_2")
        self.verticalLayout_4.addWidget(self.openIrisButton_2)
        self.closeIrisButton_2 = QtWidgets.QPushButton(self.layoutWidget_4)
        self.closeIrisButton_2.setObjectName("closeIrisButton_2")
        self.verticalLayout_4.addWidget(self.closeIrisButton_2)
        self.layoutWidget_5 = QtWidgets.QWidget(self.IrisWidget_2)
        self.layoutWidget_5.setGeometry(QtCore.QRect(10, 153, 221, 41))
        self.layoutWidget_5.setObjectName("layoutWidget_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.layoutWidget_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QtWidgets.QLabel(self.layoutWidget_5)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.currentDiameterLabel_2 = QtWidgets.QLabel(self.layoutWidget_5)
        self.currentDiameterLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.currentDiameterLabel_2.setObjectName("currentDiameterLabel_2")
        self.verticalLayout_5.addWidget(self.currentDiameterLabel_2)
        self.layoutWidget_7 = QtWidgets.QWidget(self.IrisWidget_2)
        self.layoutWidget_7.setGeometry(QtCore.QRect(10, 19, 101, 91))
        self.layoutWidget_7.setObjectName("layoutWidget_7")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.layoutWidget_7)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.iris2label = QtWidgets.QLabel(self.layoutWidget_7)
        self.iris2label.setAlignment(QtCore.Qt.AlignCenter)
        self.iris2label.setObjectName("iris2label")
        self.verticalLayout_6.addWidget(self.iris2label)
        self.layoutWidget_8 = QtWidgets.QWidget(self.IrisWidget_2)
        self.layoutWidget_8.setGeometry(QtCore.QRect(10, 120, 223, 25))
        self.layoutWidget_8.setObjectName("layoutWidget_8")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget_8)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.goToDiameterButton_2 = QtWidgets.QPushButton(self.layoutWidget_8)
        self.goToDiameterButton_2.setObjectName("goToDiameterButton_2")
        self.horizontalLayout_2.addWidget(self.goToDiameterButton_2)
        self.goToDiameterEntry_2 = QtWidgets.QLineEdit(self.layoutWidget_8)
        self.goToDiameterEntry_2.setText("")
        self.goToDiameterEntry_2.setObjectName("goToDiameterEntry_2")
        self.horizontalLayout_2.addWidget(self.goToDiameterEntry_2)
        self.horizontalLayout_3.addWidget(self.IrisWidget_2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.ComPortLabel.setText(_translate("Form", "COM Port"))
        self.comPortConnectButton.setText(_translate("Form", "Connect"))
        self.fireButton.setText(_translate("Form", "FIRE MODE"))
        self.homeIrisButton.setText(_translate("Form", "Home"))
        self.openIrisButton.setText(_translate("Form", "Open"))
        self.closeIrisButton.setText(_translate("Form", "Close"))
        self.label.setText(_translate("Form", "Current Diameter:"))
        self.currentDiameterLabel.setText(_translate("Form", "NaN mm"))
        self.goToDiameterButton.setText(_translate("Form", "Go To Diameter"))
        self.iris1label.setText(_translate("Form", "Iris 1"))
        self.homeIrisButton_2.setText(_translate("Form", "Home"))
        self.openIrisButton_2.setText(_translate("Form", "Open"))
        self.closeIrisButton_2.setText(_translate("Form", "Close"))
        self.label_2.setText(_translate("Form", "Current Diameter:"))
        self.currentDiameterLabel_2.setText(_translate("Form", "NaN mm"))
        self.iris2label.setText(_translate("Form", "Iris 2"))
        self.goToDiameterButton_2.setText(_translate("Form", "Go To Diameter"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
