from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget, QVBoxLayout, QGridLayout
import sys, os
from PyQt5.QtCore import QTimer
import serial.tools.list_ports

cwd = os.getcwd()
if '15tw-smartsystem' not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")
# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(cwd.split(os.path.sep)[:cwd.split(os.path.sep).index('15tw-smartsystem') + 1])
sys.path.insert(0,cwd)

from devices.Iris.irisWidget import Ui_Form



class IrisGUIWidget(QWidget, Ui_Form):
    """
    IrisGUI class that represents the graphical user interface for controlling the Iris devices.
    Inherits from QWidget and Ui_Form.
    """

    def __init__(self, parent=None, iris1name="Iris 1", iris2name="Iris 2"):
        """
        Initializes the IrisGUI class.

        :param parent: The parent widget, if any.
        :param iris1name: The name for the first Iris device.
        :param iris2name: The name for the second Iris device.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.find_arduinos()
        self.serial_port = False
        self.jog_len = 0.5      # mm
        # button attachments:
        self.comPortConnectButton.clicked.connect(self.initSerial)
        self.fireButton.clicked.connect(self.initFire)

        self.homeIrisButton.clicked.connect(lambda: self.onHome(iris=1))
        self.openIrisButton.clicked.connect(lambda: self.onOpen(iris=1))
        self.closeIrisButton.clicked.connect(lambda: self.onClose(iris=1))
        self.goToDiameterButton.clicked.connect(lambda: self.handle_goto(iris=1))

        self.homeIrisButton_2.clicked.connect(lambda: self.onHome(iris=2))
        self.openIrisButton_2.clicked.connect(lambda: self.onOpen(iris=2))
        self.closeIrisButton_2.clicked.connect(lambda: self.onClose(iris=2))
        self.goToDiameterButton_2.clicked.connect(lambda: self.handle_goto(iris=2))

        self.iris1_jogopen.clicked.connect(lambda: self.jog_open(iris=1))
        self.iris1_jogclosed.clicked.connect(lambda: self.jog_closed(iris=1))
        self.iris2_jogopen.clicked.connect(lambda: self.jog_open(iris=2))
        self.iris2_jogclosed.clicked.connect(lambda: self.jog_closed(iris=2))



        self.closeEvent = self.closeSerial
        self.isHomed = False
        self.isHomed_2 = False

        self.iris1label.setText(iris1name)
        self.iris2label.setText(iris2name)

    def find_arduinos(self):
        """
        Finds connected Arduino devices and populates the ComPortSelectBox with them.

        This function scans all available serial ports and checks their descriptions
        to identify those that are Arduino devices. It then adds the identified Arduino
        devices to the ComPortSelectBox for the user to select from.
        """
        ports = serial.tools.list_ports.comports()
        arduinos = []
        for port in ports:
            if "Arduino" in port.description:
                arduinos.append(port.device)
        self.ComPortSelectBox.addItems(arduinos)

    def initSerial(self):
        """
        Initializes the serial port connection to the selected Arduino device.

        This function retrieves the selected serial port from the ComPortSelectBox,
        sets the baud rate, and establishes a serial connection. It also handles
        error cases where no serial port is selected and ensures the serial buffers
        are flushed before reading the initial response from the Arduino.

        If no serial port is selected, it shows a critical error message.
        """
        self.serial_port = self.ComPortSelectBox.currentText()
        if not self.serial_port:
            QMessageBox.critical(
                self,
                "Error",
                "No serial port selected. Please select a serial port and try again.",
            )
            return
        self.baud_rate = 115200
        self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=20)
        self.ser.flushInput()
        self.ser.flushOutput()
        response = self.ser.readline().decode().strip()
        print(response)
        if response:
            self.comPortConnectButton.setStyleSheet("background-color: green")
        else:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QMessageBox.critical(self, "Error", "Could not connect to the Arduino")
        self.onHome(1)
        self.onHome(2)

    def onHome(self, iris):
        """
        Homes the specified Iris device.

        This function sends a homing command to the specified Iris device (1 or 2).
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            command = f"HOME {iris};"
            resp = self.send_command(command)
            if iris == 1:
                if resp == "OK":
                    self.isHomed = True
                    print(f"Iris {iris} homed")
                elif resp == "NC":
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to home iris 1. Please check the connection and try again.",
                    )
                    return

            elif iris == 2:
                if resp == "OK":
                    self.isHomed_2 = True
                    print(f"Iris {iris} homed")
                elif resp == "NC":
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to home iris 2. Please check the connection and try again.",
                    )
                    return

            self.update_position(self.send_command(f"POS {iris};"), iris=iris)
            print(resp)

    def onOpen(self, iris):
        """
        Opens the specified Iris device.

        This function sends an open command to the specified Iris device (1 or 2).
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if iris == 1:
            if not self.isHomed:
                self.homeIrisButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))
                return False
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(
                    1000, lambda: self.comPortConnectButton.setStyleSheet("")
                )
                return False
            else:
                resp = self.send_command(f"OPEN {iris};")
                print(resp)
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)
                if resp == "OK":
                    return True
                else:
                    return False
        elif iris == 2:
            if not self.isHomed_2:
                self.homeIrisButton_2.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton_2.setStyleSheet(""))
                return False
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(
                    1000, lambda: self.comPortConnectButton.setStyleSheet("")
                )
                return False
            else:
                resp = self.send_command(f"OPEN {iris};")
                print(resp)
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)
                if resp == "OK":
                    return True
                else:
                    return False

    def onClose(self, iris):
        """
        Closes the specified Iris device.

        This function sends a close command to the specified Iris device (1 or 2).
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if iris == 1:
            if not self.isHomed:
                self.homeIrisButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(
                    1000, lambda: self.comPortConnectButton.setStyleSheet("")
                )
            else:
                resp = self.send_command(f"CLOSE {iris};")
                print(resp)
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)
        elif iris == 2:
            if not self.isHomed_2:
                self.homeIrisButton_2.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton_2.setStyleSheet(""))
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(
                    1000, lambda: self.comPortConnectButton.setStyleSheet("")
                )
            else:
                resp = self.send_command(f"CLOSE {iris};")
                print(resp)
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)
    
    def jog_open(self, iris):
        """
        Jogs the specified Iris device open.

        This function sends a jog open command to the specified Iris device (1 or 2).
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if iris == 1:
            diameter = float(self.currentDiameterLabel.text().split()[0]) + self.jog_len
            command = f"GOTO {iris} {diameter};"
            resp = self.send_command(command)
            print(resp)
            self.update_position(self.send_command(f"POS {iris};"), iris=iris)
        elif iris == 2:
            diameter = float(self.currentDiameterLabel_2.text().split()[0]) + self.jog_len
            command = f"GOTO {iris} {diameter};"
            resp = self.send_command(command)
            print(resp)
            self.update_position(self.send_command(f"POS {iris};"), iris=iris)
    
    def jog_closed(self, iris):
        """
        Jogs the specified Iris device closed.

        This function sends a jog close command to the specified Iris device (1 or 2).
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        
        if iris == 1:
            diameter = float(self.currentDiameterLabel.text().split()[0]) - self.jog_len
            command = f"GOTO {iris} {diameter};"
            resp = self.send_command(command)
            print(resp)
            self.update_position(self.send_command(f"POS {iris};"), iris=iris)
        elif iris == 2:
            diameter = float(self.currentDiameterLabel_2.text().split()[0]) - self.jog_len
            command = f"GOTO {iris} {diameter};"
            resp = self.send_command(command)
            print(resp)
            self.update_position(self.send_command(f"POS {iris};"), iris=iris)

    def update_position(self, pos, iris):
        """
        Updates the position of the specified Iris device.

        This function retrieves the current position of the specified Iris device (1 or 2)
        from the Arduino and updates the corresponding UI element to reflect the new position.
        It checks if the serial port is initialized and sends the appropriate command to the
        connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if iris == 1:
            self.currentDiameterLabel.setText(f"{pos} mm")
        else:
            self.currentDiameterLabel_2.setText(f"{pos} mm")

    def send_command(self, command):
        """
        Sends a custom command to the Arduino.

        This function allows the user to send a custom command to the Arduino device.
        It checks if the serial port is initialized and sends the provided command to the
        connected Arduino device.

        :param command: The custom command to send to the Arduino.
        """
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response

    def handle_goto(self, iris):
        """
        Moves the specified Iris device to a given diameter.

        This function retrieves the desired diameter from the user input and sends
        a command to the specified Iris device (1 or 2) to move to that diameter.
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.

        :param iris: The Iris device number (1 or 2).
        """
        if iris == 1:
            go_to_diameter = self.goToDiameterEntry.text()
            is_homed = self.isHomed
            home_button = self.homeIrisButton
        else:
            go_to_diameter = self.goToDiameterEntry_2.text()
            is_homed = self.isHomed_2
            home_button = self.homeIrisButton_2
        try:
            diameter = float(go_to_diameter)
            if 2 <= diameter <= 41.3:
                if not is_homed:
                    home_button.setStyleSheet("background-color: red")
                    QTimer.singleShot(1000, lambda: home_button.setStyleSheet(""))
                elif not self.serial_port:
                    self.comPortConnectButton.setStyleSheet("background-color: red")
                    QTimer.singleShot(
                        1000, lambda: self.comPortConnectButton.setStyleSheet("")
                    )
                else:
                    command = f"GOTO {iris} {diameter};"
                    print(command)
                    resp = self.send_command(command)
                    print(resp)
                    self.update_position(self.send_command(f"POS {iris};"), iris=iris)

            else:
                QMessageBox.warning(
                    self,
                    "Invalid Diameter",
                    "Please enter a diameter between 2 and 41.3",
                )
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Input", "Please enter a valid number for the diameter"
            )

    def initFire(self):
        """
        Handles the fire button click event.

        This function sends a command to the Arduino to initiate the firing sequence.
        It checks if the serial port is initialized and sends the appropriate command
        to the connected Arduino device.
        """
        if not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        elif not self.isHomed and not self.isHomed_2:
            self.homeIrisButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))
            self.homeIrisButton_2.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.homeIrisButton_2.setStyleSheet(""))

        elif not self.isHomed:
            self.homeIrisButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))

        elif not self.isHomed_2:
            self.homeIrisButton_2.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.homeIrisButton_2.setStyleSheet(""))

        else:
            if not self.onOpen(1):
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to open iris 1. Please check the connection and try again.",
                )
                return
            if not self.onOpen(2):
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to open iris 2. Please check the connection and try again.",
                )
                return

            if self.fireButton.styleSheet() == "background-color: green":
                self.openIrisButton.setEnabled(True)
                self.closeIrisButton.setEnabled(True)
                self.homeIrisButton.setEnabled(True)
                self.openIrisButton_2.setEnabled(True)
                self.closeIrisButton_2.setEnabled(True)
                self.homeIrisButton_2.setEnabled(True)
                self.goToDiameterButton.setEnabled(True)
                self.goToDiameterButton_2.setEnabled(True)
                self.fireButton.setStyleSheet("")
            else:
                self.openIrisButton.setEnabled(False)
                self.closeIrisButton.setEnabled(False)
                self.homeIrisButton.setEnabled(False)
                self.openIrisButton_2.setEnabled(False)
                self.closeIrisButton_2.setEnabled(False)
                self.homeIrisButton_2.setEnabled(False)
                self.goToDiameterButton.setEnabled(False)
                self.goToDiameterButton_2.setEnabled(False)
                self.fireButton.setStyleSheet("background-color: green")

    def closeSerial(self, event):
        """
        Closes the serial port connection when the application is closed.

        This function ensures that the serial port connection is properly closed
        when the application is exited to prevent any potential issues with the
        serial communication.

        :param event: The close event.
        """
        if self.serial_port:

            def open_irises():
                if not self.onOpen(1):
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to open iris 1. Please check the connection and try again.",
                    )
                    return
                if not self.onOpen(2):
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to open iris 2. Please check the connection and try again.",
                    )
                    return
                self.ser.close()
                QMessageBox.information(
                    self, "Irises Opened", "Irises successfully opened."
                )

            QTimer.singleShot(0, open_irises)

            return


if __name__ == "__main__":

    app = QApplication(sys.argv)

    main_window = QWidget()
    main_window.resize(800, 600)  # Set the default window size

    layout = QVBoxLayout(main_window)
    grid_layout = QGridLayout()
    for i in range(1):
        for j in range(1):
            iris_gui = IrisGUIWidget()
            grid_layout.addWidget(iris_gui, i, j)

    layout.addLayout(grid_layout)

    main_window.setLayout(layout)

    main_window.show()

    sys.exit(app.exec_())
