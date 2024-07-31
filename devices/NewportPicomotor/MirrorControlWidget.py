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

# setting the correct path
mirror_dir = os.path.dirname(os.path.abspath(__file__)) # current SingleMirror_GUI directory
parent_dir = os.path.dirname(mirror_dir) # get the parent directory of SingleMirror_GUI
sys.path.insert(0, parent_dir) 

from SingleMirror_GUI import Ui_Form  # Import the generated UI class

class MirrorControlWidget(QtWidgets.QWidget):
    '''
    A QWidget subclass for controlling a mirror using Newport Picomotor8742 stages.

    Attributes:
    stage : Newport.Picomotor8742()
        The Picomotor stage controller.
    xAxis : int
        The axis number for the x-axis control.
    yAxis : int
        The axis number for the y-axis control.
    mirror_label: str
        sets the label for the mirrors controlled by Newport Picomotor 8742 stages.
    ui : Ui_Form
        The user interface generated by PyQt5.

    Methods:
    movePico(axis, steps)
        Moves the specified axis by a user-defined number of steps.
    moveToHome()
        Moves both x and y axes to the home (0) position.
    '''

    Max_steps = 1000 # Maximum nuber of steps to prevent damage to the mirrors

    def __init__(self, stage, xAxis, yAxis, mirror_label, parent=None):
        '''
        Initializes the MirrorControlWidget with a given stage and axis configurations.

        Arguments:
        stage : Newport.Picomotor8742()
            The Picomotor stage controller.
        xAxis : int
            The axis number for the x-axis control.
        yAxis : int
            The axis number for the y-axis control.
        mirror_label : str
            The label for the mirror.
        parent : QWidget (optional)
            The parent widget (default is None).
        '''
        super(MirrorControlWidget, self).__init__(parent)

        # Error handling (Validate the x axis and y axis inputs)  
        if not isinstance(xAxis, int) or xAxis < 1 or xAxis > 4:
            raise ValueError("Axis number must be an odd positive integer, either 1 or 3.")
        if not isinstance(yAxis, int) or yAxis < 1 or yAxis > 4:
            raise ValueError("Axis number must be an even positive integer, either 2 or 4.")
        
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
        '''
        Moves the specified axis by the given number of steps.

        Arguments:
        axis : int
            The axis number to move (xAxis or yAxis).
        steps : int
            The number of steps to move the axis by.
        '''
        if self.stage:
            try:
                if axis not in [self.xAxis, self.yAxis]:
                    raise ValueError(f"Axis {axis} is not valid.")
                
                # Validate number of steps
                if not isinstance(steps, int) or steps > self.Max_steps:
                    raise ValueError(f"Number of steps {steps} is out of bounds. Maximum allowed steps: {self.Max_steps}.")

                self.stage.move_by(axis=axis, steps=steps)
                self.stage.wait_move()
                if axis == self.xAxis:
                    self.ui.xStepNumber.display(self.stage.get_position(axis))
                elif axis == self.yAxis:
                    self.ui.yStepNumber.display(self.stage.get_position(axis))
            except ValueError as ve:
                QtWidgets.QMessageBox.warning(self, "Input Error", str(ve))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to move the Picomotor: {e}")

    def moveToHome(self):
        '''
        Moves both x and y axes to the home (0) position.
        '''
        if self.stage:
            try:
                # Move x-axis to home
                self.stage.move_to(axis=self.xAxis, position=0)
                self.stage.wait_move()
                # Move y-axis to home
                self.stage.move_to(axis=self.yAxis, position=0)
                self.stage.wait_move()
                # Reset step counters
                self.ui.xStepNumber.display(self.stage.get_position(self.xAxis))
                self.ui.yStepNumber.display(self.stage.get_position(self.yAxis))
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to move to Home: {e}")