from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox, QWidget
)

from PyQt5.uic import loadUi
import sys
from irisUI import Ui_MainWindow
from PyQt5.QtCore import QTimer
import serial.tools.list_ports
import json, os


class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, iris1name="Iris 1", iris2name="Iris 2"):
        super().__init__(parent)
        self.setupUi(self)
        self.find_arduinos()
        self.serial_port = False

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
        self.closeEvent = self.closeSerial
        self.isHomed = False
        self.isHomed_2 = False

        self.iris1label.setText(iris1name)
        self.iris2label.setText(iris2name)


    def find_arduinos(self):
        # List all available serial ports
        ports = serial.tools.list_ports.comports()
        arduinos = []
        for port in ports:
            if 'Arduino' in port.description:
                arduinos.append(port.device)
        self.ComPortSelectBox.addItems(arduinos)

    def initSerial(self):
        self.serial_port = self.ComPortSelectBox.currentText()
        if not self.serial_port:
            QMessageBox.critical(self, "Error", "No serial port selected. Please select a serial port and try again.")
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
                    QMessageBox.critical(self, "Error", "Failed to home iris 1. Please check the connection and try again.")
                    return
            
            elif iris == 2:
                if resp == "OK":
                    self.isHomed_2 = True
                    print(f"Iris {iris} homed")
                elif resp == "NC":
                    QMessageBox.critical(self, "Error", "Failed to home iris 2. Please check the connection and try again.")
                    return

            self.update_position(self.send_command(f"POS {iris};"), iris=iris)
            print(resp)
        

    def onOpen(self, iris):
        if iris == 1:
            if not self.isHomed:
                self.homeIrisButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))
                return False
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
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
                QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
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
        if iris == 1:
            if not self.isHomed:
                self.homeIrisButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.homeIrisButton.setStyleSheet(""))
            elif not self.serial_port:
                self.comPortConnectButton.setStyleSheet("background-color: red")
                QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
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
                QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
            else:
                resp = self.send_command(f"CLOSE {iris};")
                print(resp)
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)

    def update_position(self, pos, iris):
        if iris == 1:
            self.currentDiameterLabel.setText(f"{pos} mm")
        else:
            self.currentDiameterLabel_2.setText(f"{pos} mm")

    def send_command(self, command):
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response
    
    def handle_goto(self, iris):
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
                    QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
                else:
                    command = f"GOTO {iris} {diameter};"
                    print(command)
                    resp = self.send_command(command)
                    print(resp)
                    self.update_position(self.send_command(f"POS {iris};"), iris=iris)

            else:
                QMessageBox.warning(self, "Invalid Diameter", "Please enter a diameter between 2 and 41.3")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for the diameter")


    def initFire(self):
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
                QMessageBox.critical(self, "Error", "Failed to open iris 1. Please check the connection and try again.")
                return
            if not self.onOpen(2):
                QMessageBox.critical(self, "Error", "Failed to open iris 2. Please check the connection and try again.")
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
        if self.serial_port:
            def open_irises():
                if not self.onOpen(1):
                    QMessageBox.critical(self, "Error", "Failed to open iris 1. Please check the connection and try again.")
                    return
                if not self.onOpen(2):
                    QMessageBox.critical(self, "Error", "Failed to open iris 2. Please check the connection and try again.")
                    return
                self.ser.close()
                QMessageBox.information(self, "Irises Opened", "Irises successfully opened.")

            QTimer.singleShot(0, open_irises)
            
            return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window(iris1name="Tube1", iris2name="Tube2")
    win.show() 
    sys.exit(app.exec())
