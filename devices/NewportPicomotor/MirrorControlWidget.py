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


from SingleMirror_GUI import Ui_Form  # Import the generated UI class

# Single Mirror control
class MirrorControlWidget(QtWidgets.QWidget):
    def __init__(self, stage, xAxis, yAxis, mirror_label, parent=None):
        super(MirrorControlWidget, self).__init__(parent)
        self.stage = stage
        self.xAxis = xAxis
        self.yAxis = yAxis

        self.ui = Ui_Form()  # Create an instance of the generated UI class
        self.ui.setupUi(self)  # Set up the UI within this widget

        # Set the mirror label
        self.ui.Mirror_Label.setText(mirror_label)

        # Connect buttons to picomotor functions
        self.ui.ButtonLeft.clicked.connect(lambda: self.movePico(self.xAxis, -1 * self.ui.stepSize.value()))
        self.ui.ButtonRight.clicked.connect(lambda: self.movePico(self.xAxis, self.ui.stepSize.value()))
        self.ui.ButtonUp.clicked.connect(lambda: self.movePico(self.yAxis, self.ui.stepSize.value()))
        self.ui.ButtonDown.clicked.connect(lambda: self.movePico(self.yAxis, -1 * self.ui.stepSize.value()))
        self.ui.ButtonHome.clicked.connect(self.moveToHome)

    def movePico(self, axis, steps):
        if self.stage:
            self.stage.move_by(axis=axis, steps=steps)
            self.stage.wait_move()
            if axis == self.xAxis:
                self.ui.xStepNumber.display(self.stage.get_position(axis))
            elif axis == self.yAxis:
                self.ui.yStepNumber.display(self.stage.get_position(axis))

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