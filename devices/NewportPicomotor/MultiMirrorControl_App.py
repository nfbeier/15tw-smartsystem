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

from devices.NewportPicomotor.MirrorControlWidget import MirrorControlWidget


# Create the main application to use the widget (Multi-mirror control GUI)
class MultiMirrorControl_App(QtWidgets.QWidget):
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
    updateConnectionStatus():
        Updates the connection status and LED indicator based on the number of connected stages.
    SafetySwitch():
        switch the safety mode on or off.
    updateMovementButtons():
        Updates the enabled state of movement buttons based on the safety mode.
    updateSafetyStatusLabel():
        Updated the status of the safety switch based on the current safety mode
    closeEvent(event)
        Closes the stage controllers when the application is closed.
    """

    def __init__(self):
        """
        Initializes the MultiMirrorControl_App with the specified Picomotor stage controllers and the control widgets.
        """
        super(MultiMirrorControl_App, self).__init__()

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
                        f"Stage 1 initialized successfully with ID 8742-{self.expected_stage1_id}."
                    )
                # Check if this is the expected device for stage 2
                elif device_info.id.endswith(self.expected_stage2_id):
                    self.stage2 = temp_stage
                    print(
                        f"Stage 2 initialized successfully with ID 8742-{self.expected_stage2_id}."
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
            f"Number of connected devices: {Newport.get_usb_devices_number_picomotor()}"
        )

        # proceed with initialization of the mirrors
        self.initialize_widgets()

    def initialize_widgets(self):
        # Create widgets for each mirror
        self.mirror1 = MirrorControlWidget(self.stage1, 1, 2, "Mirror 1")
        self.mirror2 = MirrorControlWidget(self.stage1, 3, 4, "Mirror 2")
        self.mirror3 = MirrorControlWidget(self.stage2, 1, 2, "Mirror 3")
        self.mirror4 = MirrorControlWidget(self.stage2, 3, 4, "Mirror 4")

        self.mirrors = [self.mirror1, self.mirror2, self.mirror3, self.mirror4]

        # Add a safety control button
        self.safety_button = QtWidgets.QPushButton("Disable Safety", self)
        self.safety_button.setGeometry(QtCore.QRect(20, 260, 71, 41))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.safety_button.setFont(font)
        self.safety_button.setStyleSheet(
            """QPushButton {background-color: blue; 
                color: white;
                border-radius: 15px;
                font-size: 12pt;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #333333;}"""
        )

        # connect the safety button
        self.safety_button.clicked.connect(self.SafetySwitch)

        # Add a label to display the safety status
        self.safety_status_label = QtWidgets.QLabel("High Power Mode", self)
        self.safety_status_label.setGeometry(QtCore.QRect(90, 270, 131, 21))
        font.setBold(True)
        font.setWeight(75)
        self.safety_status_label.setFont(font)
        self.safety_status_label.setStyleSheet(
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

        # Add a connection status labels
        self.connectionStatusLabel = QtWidgets.QLabel("Connected Controllers: 0", self)
        self.connectionStatusLabel.setGeometry(
            QtCore.QRect(90, 20, 250, 30)
        )  # 90, 20, 201, 21
        font.setPointSize(9)
        font.setBold(True)
        font.setWeight(75)
        self.connectionStatusLabel.setFont(font)
        self.connectionStatusLabel.setStyleSheet("font-size: 14pt; font-weight: bold")

        self.LEDindicator = QtWidgets.QLabel("", self)
        self.LEDindicator.setGeometry(QtCore.QRect(40, 30, 31, 31))  # 30, 20, 21, 21
        self.LEDindicator.setStyleSheet(
            "background-color: red;border-radius: 10px;min-width: 20px;min-height: 20px;"
        )

        # Layout for the connection status and LED indicator
        connection_layout = QtWidgets.QHBoxLayout()
        connection_layout.addWidget(self.LEDindicator)
        connection_layout.addWidget(self.connectionStatusLabel)
        connection_layout.setAlignment(QtCore.Qt.AlignCenter)
        connection_layout.setSpacing(
            20
        )  # set the spacing between LEDindicator and connectionStatusLabel
        connection_layout.setContentsMargins(0, 80, 0, 0)

        # Layout for the safety controls
        safety_layout = QtWidgets.QHBoxLayout()
        safety_layout.addWidget(self.safety_button)
        safety_layout.addWidget(self.safety_status_label)
        safety_layout.setAlignment(QtCore.Qt.AlignCenter)
        safety_layout.setSpacing(
            20
        )  # Set the spacing between the  safety_button and safety_status_label
        safety_layout.setContentsMargins(0, 0, 0, 80)

        # Create a layout for the mirrors
        mirror_layout = QtWidgets.QHBoxLayout()
        for mirror in self.mirrors:
            mirror_layout.addWidget(mirror)

        # Layout of main window
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(connection_layout)
        main_layout.addLayout(mirror_layout)
        main_layout.addLayout(safety_layout)

        main_layout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)

        self.setLayout(main_layout)
        self.setFixedSize(1100, 400)  # Adjust the window size

        self.mirror_safe = True  # Initialize mirrors as safe (i.e motion is disabled)

        # Update connection status when initializing
        self.updateConnectionStatus()

    def updateConnectionStatus(self):
        """
        Updates the connection status and LED indicator based on the number of connected stages.
        """
        num_connected_stages = Newport.get_usb_devices_number_picomotor()
        self.connectionStatusLabel.setText(
            f"Connected Controllers: {num_connected_stages}"
        )
        self.connectionStatusLabel.setStyleSheet("font-size: 14pt; font-weight: bold")

        if num_connected_stages >= 2:
            self.LEDindicator.setStyleSheet(
                "background-color: green;border-radius: 15px;min-width: 30px;min-height: 30px;"
            )
        else:
            self.LEDindicator.setStyleSheet(
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
            self.safety_status_label.setText("High Power Mode")
            self.safety_status_label.setStyleSheet(
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
            self.safety_button.setText("Disable Safety")
        else:
            self.safety_status_label.setText("Alignment Mode")
            self.safety_button.setText("Enable Safety")
            self.safety_status_label.setStyleSheet(
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
    app = QtWidgets.QApplication(sys.argv)
    mainApp = MultiMirrorControl_App()
    mainApp.show()
    sys.exit(app.exec_())
