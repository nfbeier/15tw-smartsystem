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

# Create the main application to use the widget (Multi-mirror control GUI)

class MultiMirrorControl_App(QtWidgets.QWidget):
    def __init__(self):
        super(MultiMirrorControl_App, self).__init__()

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

        # Create widgets for each mirror mount
        self.mirror1 = MirrorControlWidget(self.stage1, 1, 2, "Mirror 1")
        self.mirror2 = MirrorControlWidget(self.stage1, 3, 4, "Mirror 2")
        self.mirror3 = MirrorControlWidget(self.stage2, 1, 2, "Mirror 3")
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.mirror1)
        layout.addWidget(self.mirror2)
        layout.addWidget(self.mirror3)

    def closeEvent(self, event):
        if self.stage1:
            self.stage1.close()
        if self.stage2:
            self.stage2.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainApp = MultiMirrorControl_App()
    mainApp.show()
    sys.exit(app.exec_())
