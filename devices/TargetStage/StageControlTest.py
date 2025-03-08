import numpy as np
from pylablib.devices import Newport
import sys, os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

cwd = os.getcwd()
print(cwd)
# Check if '15tw-smartsystem' is in the components
if "15tw-smartsystem" not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(
    cwd.split(os.path.sep)[: cwd.split(os.path.sep).index("15tw-smartsystem") + 1]
)

sys.path.insert(0, cwd)

from devices.XPS.XPS import XPS
#from devices.TargetStage.XPSControlPanel_GUI import Ui_Form
from devices.TargetStage.singleAxisControl import singleAxisControl
from devices.TargetStage.XPSControlPanelMultiAxisTest_GUI import Ui_Form

class StagePositionThread(QtCore.QThread):
    position_updated = QtCore.pyqtSignal(str, float)  # Signal to update GUI

    def __init__(self, xps, axis):
        super().__init__()
        self.xps = xps
        self.axis = axis
        self.selected_group = None
        self.running = True

    def run(self):
        while self.running:
            if self.xps and self.selected_group:
                try:
                    position = self.xps.getStagePosition(self.selected_group)
                    self.position_updated.emit(self.axis, position)
                except Exception as e:
                    print(f"Error updating position for {self.axis}: {e}")
            self.msleep(200)  # Sleep for 200ms (same as original timer)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class TargetStageControl(QtWidgets.QWidget):
    """
    This class provides functionality to initialize, home, enable/disable, and move stages, 
    as well as update the GUI with real-time stage status and position.

    Attributes:
        ui: An instance of the Ui_Form class, representing the GUI layout.
        xps: An instance of the XPS class, representing the Newport XPS Motion Controller.
        xps_groups: A dictionary containing the status of all available groups (axes) connected to the XPS controller.
        selected_group: A string representing the currently selected group (axis).
        stageStatus: A string representing the current status of the selected group.
        timer: A QTimer instance used to periodically update the stage position and status.

    Methods:
        __init__: Initializes the TargetStageControl class and sets up the GUI, XPS controller, and timer.
        initialize_xps: Initializes the XPS controller and refreshes the list of available groups.
        refreshGroups: Refreshes the list of available groups and updates the group combo box.
        updateGroup: Updates the selected group when the user changes the combo box selection.
        updateGUIStatus: Updates the GUI based on the current stage status.
        updateStagePosition: Updates the stage position display in the GUI.
        kill_all: Immediately stops all motion for the selected group.
        updateTravelLimits: Updates the minimum or maximum travel limits for the selected group.
        motionButtons: Handles motion commands (absolute, forward, backward).
        statusButtons: Handles status-related commands (initialize, home, enable/disable).
        closeEvent: Override the close event to stop the timer and clean up.
        show_error_message: Displays an error message in a QMessageBox.

    """
    def __init__(self):
        super(TargetStageControl, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # Create a dictionary to store the axis controls
        self.axis_controls = {
        "X": singleAxisControl(self),
        "Y": singleAxisControl(self),
        "Z": singleAxisControl(self),
    }
        
        # Initialize XPS controller
        self.xps = None
        self.selected_groups_by_axis = {"X": None, "Y": None, "Z": None}  # Store selected groups for each axis 
        self.position = {"X": 0.000, "Y": 0.000, "Z": 0.000}
        self.initialize_xps()

        # Set geometry for each axis control
        self.axis_controls["X"].setGeometry(QtCore.QRect(169, 30, 261, 411))
        self.axis_controls["Y"].setGeometry(QtCore.QRect(440, 30, 261, 411))
        self.axis_controls["Z"].setGeometry(QtCore.QRect(710, 30, 261, 411))

        # Set the correct labels for each axis
        self.axis_controls["X"].ui.XaxisLabel.setText("X-Axis")
        self.axis_controls["Y"].ui.XaxisLabel.setText("Y-Axis")
        self.axis_controls["Z"].ui.XaxisLabel.setText("Z-Axis")

        # Set the correct labels for the Realtive move button on each axis
        self.axis_controls["Z"].ui.X_LeftRelativeMoveButton.setText("Backward")
        self.axis_controls["Z"].ui.X_RightRelativeMoveButton.setText("Forward")
        self.axis_controls["Y"].ui.X_LeftRelativeMoveButton.setText("Down")
        self.axis_controls["Y"].ui.X_RightRelativeMoveButton.setText("Up")

        # Set up a timer to update the stage position periodically
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)  # Update every 200 ms
        self.timer.timeout.connect(self.updateAllStagePositions)
        self.timer.start()

        # Connect signals to slots for each axis control
        for axis, control in self.axis_controls.items():
            control.ui.X_GroupNames.activated.connect(lambda _, c=control, a=axis: self.updateGroup(c,a))
            control.ui.X_AbsoluteMoveButton.clicked.connect(lambda _, c=control,a=axis: self.motionButtons("Absolute", c,a))
            control.ui.X_LeftRelativeMoveButton.clicked.connect(lambda _, c=control,a=axis: self.motionButtons("Left", c,a))
            control.ui.X_RightRelativeMoveButton.clicked.connect(lambda _, c=control,a=axis: self.motionButtons("Right", c,a))
            control.ui.MaxTravelValue.textChanged.connect(lambda _, c=control,a=axis: self.updateTravelLimits("max", c,a))
            control.ui.MinTravelValue.textChanged.connect(lambda _, c=control,a=axis: self.updateTravelLimits("min", c,a))
            control.ui.RefreshGroupsButton.clicked.connect(lambda _, c=control, a=axis: self.refreshGroups(c, a))

        self.ui.InitializeXPS.clicked.connect(lambda: self.statusButtons("Initialize"))
        self.ui.HomeXPS.clicked.connect(lambda: self.statusButtons("Home"))
        self.ui.EnableDisableXPS.clicked.connect(lambda: self.statusButtons("Enable/Disable"))
        self.ui.KillAll.clicked.connect(self.kill_all)


    def initialize_xps(self):
        try:
            self.xps = XPS(ipAddress='192.168.254.254',username = 'Administrator',password = 'Administrator')

            if self.xps:
                for axis, control in self.axis_controls.items():
                    self.refreshGroups(control, axis)
        except Exception as e:
            self.xps = None
            self.show_error_message("XPS Initialization Error", f"Failed to initialize XPS controller: {e}")

    def refreshGroups(self,axis_control, axis):
        if self.xps:
            try:
                self.xps_groups = self.xps.getXPSStatus()
                group_names = list(self.xps_groups.keys())
                axis_control.ui.X_GroupNames.clear()
                axis_control.ui.X_GroupNames.addItems(group_names)
                if axis == "X":
                    axis_control.ui.X_GroupNames.setCurrentIndex(0)  # Default to the first group for X-axis
                elif axis == "Y":
                    axis_control.ui.X_GroupNames.setCurrentIndex(1)  # Default to the second group for Y-axis
                elif axis == "Z":
                    axis_control.ui.X_GroupNames.setCurrentIndex(2)  # Default to the third group for Z-axis
                self.selected_groups_by_axis[axis] = str(axis_control.ui.X_GroupNames.currentText())
                self.xps.setGroup(self.selected_groups_by_axis[axis])
                self.updateGroup(axis_control,axis)
            except Exception as e:
                self.show_error_message("Group Refresh Error", f"Failed to refresh groups: {e}")
        else:
            self.show_error_message("XPS Not Available", "XPS controller is not initialized.")

    def updateGroup(self, axis_control, axis):
        self.selected_groups_by_axis[axis] = str(axis_control.ui.X_GroupNames.currentText())
        if self.xps:
            self.xps.setGroup(self.selected_groups_by_axis[axis])
            self.stageStatus = self.xps.getStageStatus(self.selected_groups_by_axis[axis])
            self.updateGUIStatus(axis_control, axis)

    def updateGUIStatus(self, axis_control, axis):
        if self.stageStatus == "Not initialized state" or self.stageStatus == "Not initialized state due to a GroupKill or KillAll command":
            self.ui.HomeXPS.setEnabled(False)
            self.ui.EnableDisableXPS.setEnabled(False)
            axis_control.ui.X_AbsoluteMoveButton.setEnabled(False)
            axis_control.ui.X_RightRelativeMoveButton.setEnabled(False)
            axis_control.ui.X_LeftRelativeMoveButton.setEnabled(False)
            self.ui.XPSstatusLabel.setText("Not Initialized")
            self.ui.XPSstatusLabel.setStyleSheet("color: red;")
            self.ui.EnableDisableXPS.setText("Enable XPS")

        elif self.stageStatus == "Not referenced state":
            self.ui.HomeXPS.setEnabled(True)
            self.ui.EnableDisableXPS.setEnabled(False)
            axis_control.ui.X_AbsoluteMoveButton.setEnabled(False)
            axis_control.ui.X_RightRelativeMoveButton.setEnabled(False)
            axis_control.ui.X_LeftRelativeMoveButton.setEnabled(False)
            self.ui.XPSstatusLabel.setText("Not Homed")
            self.ui.XPSstatusLabel.setStyleSheet("color: red;")
            self.ui.EnableDisableXPS.setText("Enable XPS")

        elif self.stageStatus == "Disabled state":
            self.ui.EnableDisableXPS.setEnabled(True)
            self.ui.HomeXPS.setEnabled(True)
            axis_control.ui.X_AbsoluteMoveButton.setEnabled(False)
            axis_control.ui.X_RightRelativeMoveButton.setEnabled(False)
            axis_control.ui.X_LeftRelativeMoveButton.setEnabled(False)
            self.ui.XPSstatusLabel.setText("Disabled")
            self.ui.XPSstatusLabel.setStyleSheet("color: red;")
            self.ui.EnableDisableXPS.setText("Enable XPS")

        elif self.stageStatus[:11].upper() == "Ready state".upper():
            self.ui.EnableDisableXPS.setEnabled(True)
            self.ui.HomeXPS.setEnabled(True)
            axis_control.ui.X_AbsoluteMoveButton.setEnabled(True)
            axis_control.ui.X_RightRelativeMoveButton.setEnabled(True)
            axis_control.ui.X_LeftRelativeMoveButton.setEnabled(True)
            self.ui.XPSstatusLabel.setText("Enabled")
            self.ui.XPSstatusLabel.setStyleSheet("color: green;")
            self.ui.EnableDisableXPS.setText("Disable XPS")

        self.updateStagePosition(axis_control, axis)

    def updateStagePosition(self, axis_control, axis):
        if self.xps:
            try:
                self.position[axis] = self.xps.getStagePosition(self.selected_groups_by_axis[axis])
                print(self.position[axis])
                axis_control.ui.PositionValue.display(self.position[axis])
                self.stageStatus = self.xps.getStageStatus(self.selected_groups_by_axis[axis])
                #print(self.stageStatus)
                self.error_shown = False  # Reset the flag if the update succeeds
            except Exception as e:
                if not hasattr(self, "error_shown") or not self.error_shown:
                    self.show_error_message("Position Update Error", f"Failed to update stage position: {e}")
                    self.error_shown = True  # Set the flag to prevent repeated messages
        else:
            if not hasattr(self, "xps_error_shown"):
                self.show_error_message("XPS Not Connected", "XPS controller is not initialized.")
                self.xps_error_shown = True  # Set a flag to indicate the error has been shown


    def updateAllStagePositions(self):
        """Update the stage position for all axes."""
        for axis, control in self.axis_controls.items():
            self.updateStagePosition(control, axis)


    def kill_all(self):
        if self.xps:
            try:
                for group_name in self.selected_groups_by_axis.values():
                    self.xps.killAll(group_name)
                for axis, control in self.axis_controls.items():
                    self.updateGUIStatus(control, axis)

                self.ui.XPSstatusLabel.setText("Emergency Stop")
                self.ui.XPSstatusLabel.setStyleSheet("color: red;")

            except Exception as e:
                self.show_error_message("Kill All Error", f"Failed to kill all motion: {e}")

    def updateTravelLimits(self, lim, axis_control, axis):
        if self.xps:
            try:
                if lim == "min":
                    limit = float(axis_control.ui.MinTravelValue.text())
                    if limit < 0 or limit > 50:
                        self.show_error_message("Invalid Limit", "Minimum limit must be between 0 and 50 mm.")
                        axis_control.ui.MinTravelValue.setText(str(self.xps.getminLimit(self.selected_groups_by_axis[axis])))
                    else:
                        self.xps.setminLimit(self.selected_groups_by_axis[axis], limit)
                elif lim == "max":
                    limit = float(axis_control.ui.MaxTravelValue.text())
                    if limit < 0 or limit > 50:
                        self.show_error_message("Invalid Limit", "Maximum limit must be between 0 and 50 mm.")
                        axis_control.ui.MaxTravelValue.setText(str(self.xps.getmaxLimit(self.selected_groups_by_axis[axis])))
                    else:
                        self.xps.setmaxLimit(self.selected_groups_by_axis[axis], limit)
            except ValueError:
                self.show_error_message("Invalid Input", "Please enter a valid number for the travel limit.")

    def motionButtons(self, btn, axis_control, axis):
        if self.xps:
            try:
                if btn == "Absolute":
                    pos = float(axis_control.ui.AbsoluteMoveValue.text())
                else:
                    pos = float(axis_control.ui.RelativeMoveValue.text())

                if self.stageStatus[:11].upper() == "Ready state".upper():
                    if btn == "Absolute":
                        self.xps.moveAbsolute(self.selected_groups_by_axis[axis], pos)
                    elif btn == "Right":
                        self.xps.moveRelative(self.selected_groups_by_axis[axis], pos)
                    elif btn == "Left":
                        self.xps.moveRelative(self.selected_groups_by_axis[axis], -1 * pos)
                else:
                    self.show_error_message("Stage Not Ready", "The stage is not ready to move.")
            except ValueError:
                self.show_error_message("Invalid Input", "Please enter a valid number for the position.")
            except Exception as e:
                self.show_error_message("Motion Error", f"Failed to execute motion command: {e}")

    def statusButtons(self, btn):
        if self.xps:
            try:
                for axis, control in self.axis_controls.items():
                    if btn == "Initialize":
                        self.xps.initializeStage(self.selected_groups_by_axis[axis])
                    elif btn == "Home":
                        self.xps.homeStage(self.selected_groups_by_axis[axis])
                    elif btn == "Enable/Disable" and self.stageStatus.upper() == "Disabled state".upper():
                        self.xps.enableGroup(self.selected_groups_by_axis[axis])
                    elif btn == "Enable/Disable" and self.stageStatus[:11].upper() == "Ready state".upper():
                        self.xps.disableGroup(self.selected_groups_by_axis[axis])

                    self.stageStatus = self.xps.getStageStatus(self.selected_groups_by_axis[axis])
                    self.updateGUIStatus(control, axis)
            except Exception as e:
                self.show_error_message("Status Error", f"Failed to execute status command: {e}")

    def closeEvent(self, event):
        print("Closing the application...")
        #Add kill all command for all stages
        self.kill_all()
        self.timer.stop()  # Stop the timer
        event.accept()  

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = TargetStageControl()
    window.show()
    sys.exit(app.exec_())
