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
        self.homeIrisButton.clicked.connect(self.onHome)
        self.openIrisButton.clicked.connect(self.onOpen)
        self.closeIrisButton.clicked.connect(self.onClose)
        self.comPortConnectButton.clicked.connect(self.initSerial)
        self.goToDiameterButton.clicked.connect(self.handle_goto)
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

    def onHome(self):
        if not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            resp = self.send_command("HOME;")
            if resp == "OK":
                self.isHomed = True
                print("Iris homed")
                self.update_position(self.send_command("POS;"))
            print(resp)
        

    def onOpen(self):
        if not self.isHomed:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        elif not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            resp = self.send_command("OPEN;")
            print(resp)
            self.update_position(self.send_command("POS;"))


    def onClose(self):
        if not self.isHomed:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        elif not self.serial_port:
            self.comPortConnectButton.setStyleSheet("background-color: red")
            QTimer.singleShot(1000, lambda: self.comPortConnectButton.setStyleSheet(""))
        else:
            resp = self.send_command("CLOSE;")
            print(resp)
            self.update_position(self.send_command("POS;"))

    def update_position(self, pos):
        self.currentDiameterLabel.setText(f"{pos} mm")

    def send_command(self, command):
        self.ser.write(command.encode())
        response = self.ser.readline().decode().strip()
        return response
    
    def handle_goto(self):
        go_to_diameter = self.goToDiameterEntry.text()
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
                    command = f"GOTO {diameter};"
                    resp = self.send_command(command)
                    print(resp)
                    self.update_position(self.send_command("POS;"))

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
