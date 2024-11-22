from pylablib.devices import Newport
import sys, os
from PyQt5 import QtWidgets, QtCore, QtGui

cwd = os.getcwd()
if "15tw-smartsystem" not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")
# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(
    cwd.split(os.path.sep)[: cwd.split(os.path.sep).index("15tw-smartsystem") + 1]
)
sys.path.insert(0, cwd)

#from devices.NewportPicomotor.MirrorControlWidget import MirrorControlWidget
from software.LaserAlignment.alignment_GUI import Ui_MainWindow
from devices.NewportPicomotor.MirrorControlWidget import MirrorControlWidget

class Alignator9000(QtWidgets.QMainWindow):
    """
    A QWidget subclass for controlling multiple mirrors using Newport Picomotor8742 stages.

    Attributes:
    stage1 : Newport.Picomotor8742 or None
        The Picomotor stage controller for the first set of mirrors (2 mirrors specifically).
    stage2 : Newport.Picomotor8742 or None
        The Picomotor stage controller for the second set of mirrors.
    mirror1 : MirrorControlWidget
        Control widget for the first mirror.
    mirror2 : MirrorControlWidget
        Control widget for the second mirror.
    mirror3 : MirrorControlWidget
        Control widget for the third mirror.

    Methods:
    initialize_widgets() : Create widgets for each mirror
    updateConnectionStatus():
        Updates the connection status and LED indicator based on the number of connected stages.
    SafetySwitch():
        switch the safety mode on or off.
    updateMovementButtons():
        Updates the enabled state of movement buttons based on the safety mode.
    updateSafetyStatusLabel():
        Updated the status of the safety switch based on the current safety mode
    closeEvent()
        Closes the stage controllers when the application is closed.
    """

    def __init__(self):
        """
        Initializes the MultiMirrorControl_App with the specified Picomotor stage controllers and the control widgets.
        """
        super(Alignator9000, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Define expected device IDs for both stages
        self.expected_stage1_id = "102070"  # Expected device ID for stage 1
        self.expected_stage2_id = "102092"  # Expected device ID for stage 2

        self.stage1 = None
        self.stage2 = None

        # Attempt to connect to all available devices and assign to stage1 and stage2 based on device ID
        for i in range(Newport.get_usb_devices_number_picomotor()):
            try:
                temp_stage = Newport.Picomotor8742(conn=i)
                device_info = temp_stage.get_device_info()

                # Check if this is the expected device for stage 1
                if device_info.id.endswith(self.expected_stage1_id):
                    self.stage1 = temp_stage
                    print(
                        f"Stage 1 initialized successfully using ID 8742-{self.expected_stage1_id}."
                    )
                # Check if this is the expected device for stage 2
                elif device_info.id.endswith(self.expected_stage2_id):
                    self.stage2 = temp_stage
                    print(
                        f"Stage 2 initialized successfully using ID 8742-{self.expected_stage2_id}."
                    )
                else:
                    # Close any devices that don't match the expected IDs
                    temp_stage.close()

            except Newport.base.NewportBackendError as e:
                print(f"Stage {i + 1} could not be initialized: {e}")

        # Check if stages are properly initialized
        if self.stage1 is None:
            print(
                f"Could not find the device with ID 8742-{self.expected_stage1_id} for Stage 1."
            )
        if self.stage2 is None:
            print(
                f"Could not find the device with ID 8742-{self.expected_stage2_id} for Stage 2."
            )

        # Show total number of connected devices
        print(
            f"Total number of connected devices: {Newport.get_usb_devices_number_picomotor()}"
        )

        # proceed with initialization of the mirrors
        self.initialize_widgets()

    def initialize_widgets(self):
        # Create widgets for each mirror
        self.ui.mirror1 = MirrorControlWidget(self.stage1, 1, 2, "Mirror 1")
        self.ui.mirror2 = MirrorControlWidget(self.stage1, 3, 4, "Mirror 2")
        self.ui.mirror3 = MirrorControlWidget(self.stage2, 1, 2, "Mirror 3")
        self.ui.mirror4 = MirrorControlWidget(self.stage2, 3, 4, "Mirror 4")

        self.mirrors = [self.ui.mirror1, self.ui.mirror2, self.ui.mirror3, self.ui.mirror4]

        #self.ui.mirrorLayout.resize(800, 600)
        # connect the safety button
        self.ui.safety_button.clicked.connect(self.SafetySwitch)

        for mirror in self.mirrors:
            self.ui.mirrorLayout.addWidget(mirror)

        self.mirror_safe = True  # Initialize mirrors as safe (i.e motion is disabled)

        # Update connection status when initializing
        self.updateConnectionStatus()

    def updateConnectionStatus(self):
        """
        Updates the connection status and LED indicator based on the number of connected stages.
        """
        num_connected_stages = Newport.get_usb_devices_number_picomotor()
        self.ui.connectionStatusLabel.setText(
            f"Connected Controllers: {num_connected_stages}"
        )
        self.ui.connectionStatusLabel.setStyleSheet("font-size: 14pt; font-weight: bold")

        if num_connected_stages >= 2:
            self.ui.LEDindicator.setStyleSheet(
                "background-color: green;border-radius: 15px;min-width: 30px;min-height: 30px;"
            )
        else:
            self.ui.LEDindicator.setStyleSheet(
                "background-color: red;border-radius: 15px;min-width: 30px;min-height: 30px;"
            )

    def SafetySwitch(self):
        """
        Toggles the safety mode on or off for all mirrors.
        """
        self.mirror_safe = not self.mirror_safe
        self.updateMovementButtons()
        self.updateSafetyStatusLabel()

    def updateMovementButtons(self):
        """
        Updates the enabled state of movement buttons for all mirrors based on the safety mode.
        """
        for mirror in self.mirrors:
            mirror.updateMovementButtons(self.mirror_safe)

    def updateSafetyStatusLabel(self):
        """
        Updates the status label for the safety mode.
        """
        if self.mirror_safe:
            self.ui.safety_status_label.setText("High Power Mode")
            self.ui.safety_status_label.setStyleSheet(
                """
                QLabel {
                    background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #FF6666, stop:1 #CC0000);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #AA0000;
                    text-align: center;
                }
            """
            )
            self.ui.safety_button.setText("Disable Safety")
        else:
            self.ui.safety_status_label.setText("Alignment Mode")
            self.ui.safety_button.setText("Enable Safety")
            self.ui.safety_status_label.setStyleSheet(
                """
                QLabel {
                    background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #99FF99, stop:1 #33CC33);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #00AA00;
                    text-align: center;
                }
            """
            )

    def closeEvent(self, event):
        """
        Closes the stage controllers when the application is closed.

        Argument:
        event : QCloseEvent
            The close event that is triggered when the application window is closed.
        """
        if self.stage1:
            self.stage1.close()
        if self.stage2:
            self.stage2.close()
        event.accept()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainApp = Alignator9000()
    mainApp.show()
    sys.exit(app.exec_())