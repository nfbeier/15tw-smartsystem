# -*- coding: utf-8 -*-
"""
Created on Wed Jun 19 12:58:40 2024

@author: BD-1
"""

import numpy as np
from pylablib.devices import Newport
import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets

cwd = os.getcwd()
print(cwd)
# Check if '15tw-smartsystem' is in the components
if '15tw-smartsystem' not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(cwd.split(os.path.sep)[:cwd.split(os.path.sep).index('15tw-smartsystem') + 1])

sys.path.insert(0,cwd)

from Mirror_GUI import Ui_Form

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
