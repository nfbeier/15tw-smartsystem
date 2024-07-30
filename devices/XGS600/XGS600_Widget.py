from PyQt5 import QtWidgets, QtCore
import os
import sys
 
cwd = os.getcwd()
print(cwd)
# Check if '15tw-smartsystem' is in the components
if '15tw-smartsystem' not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(cwd.split(os.path.sep)[:cwd.split(os.path.sep).index('15tw-smartsystem') + 1])

sys.path.insert(0,cwd)

from devices.XGS600 import XGS600
import serial.tools.list_ports
from devices.XGS600.XGS600 import XGS600Driver
from devices.XGS600.XGS600_WidgetUI import Ui_Form

class XGSWidget(QtWidgets.QWidget):
    def __init__(self,InheretedClass=None):
        super(XGSWidget,self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # fuck wit the com port
        self.comport = None
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "PL2303GT" in port.description:
                self.comport = port.device
        if not self.comport:
            QtWidgets.QMessageBox.critical(self, "Error", "XGS not connected")
            return
        else:
            self.xgs = XGS600Driver(port=self.comport)
            self.gauge_id = "MAIN1" #The 15 TW chamber vacuum gauge ID is MAIN1
            self.ui.GaugeName.setText(self.gauge_id)
            self.ui.pressureUnitsLabel.setText(self.xgs.read_pressure_unit())

            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.updatePressure)
            self.timer.start(1000)

    def updatePressure(self):
        pressure = self.xgs.read_pressure(f"U{self.gauge_id}")
        self.ui.lcdNumber.display(pressure)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = XGSWidget()
    ui.show()
    sys.exit(app.exec_())