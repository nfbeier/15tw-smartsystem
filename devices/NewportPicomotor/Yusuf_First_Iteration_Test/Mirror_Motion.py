import numpy as np
from pylablib.devices import Newport
import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets

# Update the current working directory check and import
cwd = os.getcwd()
print(cwd)

if '15tw-smartsystem' not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

cwd = os.path.sep.join(cwd.split(os.path.sep)[:cwd.split(os.path.sep).index('15tw-smartsystem') + 1])
sys.path.insert(0, cwd)

from Mirror_GUI import Ui_Form  # Import the generated UI file

class picoMotor_App(QtWidgets.QWidget):
    def __init__(self):
        super(picoMotor_App, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        # Axis assignments
        self.stage1_axes = [1, 2, 3, 4]  # Axes 1, 2, 3, 4 for stage 1
        self.stage2_axes = [1, 2, 3, 4]  # Axes 1, 2, 3, 4 for stage 2
        
        try:
            self.stage1 = Newport.Picomotor8742(conn=0,multiaddr=True)
            print("Stage 1 initialized successfully.")
        except Newport.base.NewportBackendError as e:
            print(f"Stage 1 could not be initialized: {e}")
            self.stage1 = None

        try:
            self.stage2 = Newport.Picomotor8742(conn=1,multiaddr=True)
            print("Stage 2 initialized successfully.")
        except Newport.base.NewportBackendError as e:
            print(f"Stage 2 could not be initialized: {e}")
            self.stage2 = None

        print(f"Number of connected devices: {Newport.get_usb_devices_number_picomotor()}")

        # Connect buttons to picomotor functions for stage1 (Mirror 1 and Mirror 2)
        self.ui.ButtonLeft.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber, self.ui.yStepNumber, axis=self.stage1_axes[0], steps=-1 * self.ui.stepSize.value()))
        self.ui.ButtonRight.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber, self.ui.yStepNumber, axis=self.stage1_axes[0], steps=self.ui.stepSize.value()))
        self.ui.ButtonUp.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber, self.ui.yStepNumber, axis=self.stage1_axes[1], steps=self.ui.stepSize.value()))
        self.ui.ButtonDown.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber, self.ui.yStepNumber, axis=self.stage1_axes[1], steps=-1 * self.ui.stepSize.value()))
        self.ui.ButtonHome.clicked.connect(lambda: self.moveToHome(self.stage1, self.ui.xStepNumber, self.ui.yStepNumber, xAxis=self.stage1_axes[0], yAxis=self.stage1_axes[1]))

        self.ui.ButtonLeft_2.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber_2, self.ui.yStepNumber_2, axis=self.stage1_axes[2], steps=-1 * self.ui.stepSize_2.value()))
        self.ui.ButtonRight_2.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber_2, self.ui.yStepNumber_2, axis=self.stage1_axes[2], steps=self.ui.stepSize_2.value()))
        self.ui.ButtonUp_2.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber_2, self.ui.yStepNumber_2, axis=self.stage1_axes[3], steps=self.ui.stepSize_2.value()))
        self.ui.ButtonDown_2.clicked.connect(lambda: self.movePico(self.stage1, self.ui.xStepNumber_2, self.ui.yStepNumber_2, axis=self.stage1_axes[3], steps=-1 * self.ui.stepSize_2.value()))
        self.ui.ButtonHome_2.clicked.connect(lambda: self.moveToHome(self.stage1, self.ui.xStepNumber_2, self.ui.yStepNumber_2, xAxis=self.stage1_axes[2], yAxis=self.stage1_axes[3]))

        # Connect buttons to picomotor functions for stage2 (Mirror 3)
        self.ui.ButtonLeft_3.clicked.connect(lambda: self.movePico(self.stage2, self.ui.xStepNumber_3, self.ui.yStepNumber_3, axis=self.stage2_axes[0], steps=-1 * self.ui.stepSize_3.value()))
        self.ui.ButtonRight_3.clicked.connect(lambda: self.movePico(self.stage2, self.ui.xStepNumber_3, self.ui.yStepNumber_3, axis=self.stage2_axes[0], steps=self.ui.stepSize_3.value()))
        self.ui.ButtonUp_3.clicked.connect(lambda: self.movePico(self.stage2, self.ui.xStepNumber_3, self.ui.yStepNumber_3, axis=self.stage2_axes[1], steps=self.ui.stepSize_3.value()))
        self.ui.ButtonDown_3.clicked.connect(lambda: self.movePico(self.stage2, self.ui.xStepNumber_3, self.ui.yStepNumber_3, axis=self.stage2_axes[1], steps=-1 * self.ui.stepSize_3.value()))
        self.ui.ButtonHome_3.clicked.connect(lambda: self.moveToHome(self.stage2, self.ui.xStepNumber_3, self.ui.yStepNumber_3, xAxis=self.stage2_axes[0], yAxis=self.stage2_axes[1]))

    def movePico(self, stage, xStepDisplay, yStepDisplay, axis, steps):
        if stage:
            stage.move_by(axis=axis, steps=steps)
            stage.wait_move()
            if axis in [self.stage1_axes[0], self.stage1_axes[2], self.stage2_axes[0]]:
                xStepDisplay.display(stage.get_position(axis))
            elif axis in [self.stage1_axes[1], self.stage1_axes[3],  self.stage2_axes[1]]:
                yStepDisplay.display(stage.get_position(axis))

    def moveToHome(self, stage, xStepDisplay, yStepDisplay, xAxis, yAxis):
        if stage:
            # Move x-axis to home
            stage.move_to(axis=xAxis, position=0)
            stage.wait_move()
            # Move y-axis to home
            stage.move_to(axis=yAxis, position=0)
            stage.wait_move()
            # Reset step counters
            xStepDisplay.display(stage.get_position(xAxis))
            yStepDisplay.display(stage.get_position(yAxis))

    def closeEvent(self, event):
        if self.stage1:
            self.stage1.close()
        if self.stage2:
            self.stage2.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    application = picoMotor_App()
    application.show()
    sys.exit(app.exec_())
