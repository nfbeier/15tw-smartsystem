from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)

from PyQt5.uic import loadUi
import sys
from irisUI import Ui_MainWindow
from PyQt5.QtCore import QTimer
import serial.tools.list_ports
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.find_arduinos()
        self.serial_port = False

        # button attachments:
        self.comPortConnectButton.clicked.connect(self.initSerial)


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

    def onHome(self, iris):
        if not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            command = f"HOME {iris};"
            resp = self.send_command(command)
            if resp == "OK":
                self.isHomed = True
                print(f"Iris {iris} homed")
                self.update_position(self.send_command(f"POS {iris};"), iris=iris)
            print(resp)
        

    def onOpen(self, iris):
        if not self.isHomed:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        elif not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            resp = self.send_command(f"OPEN {iris};")
            print(resp)
            self.update_position(self.send_command(f"POS {iris};"), iris=iris)


    def onClose(self, iris):
        if not self.isHomed:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
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
        else:
            go_to_diameter = self.goToDiameterEntry_2.text()
        try:
            diameter = float(go_to_diameter)
            if 2 <= diameter <= 41.3:
                if not self.isHomed:
                    self.comPortConnectButton.setStyleSheet("background-color: red")
                    QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
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


    
    def closeSerial(self, event):
        if not self.serial_port:
            return
        self.ser.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show() 
    sys.exit(app.exec())
