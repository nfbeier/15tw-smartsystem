from PyQt5 import QtWidgets, uic, QtGui, QtCore
import os
import sys
import numpy as np
 
cwd = os.getcwd()
print(cwd)
sys.path.insert(0,os.getcwd())

from devices.XGS600 import XGS600
from math import floor
from fractions import Fraction
import time, json

from devices.XGS600.XGS600 import XGS600Driver
from devices.XGS600.XGS600_WidgetUI import Ui_Form

class XGSWidget(QtWidgets.QWidget):
    def __init__(self,InheretedClass=None):
        super(XGSWidget,self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        #self.xgs = XGS600Driver(port="COM3")
    
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePressure)
        self.timer.start(1000)

    def updatePressure(self):
        pressure = np.random.randint(0,1000)
        self.ui.lcdNumber.display(pressure)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = XGSWidget()
    ui.show()
    sys.exit(app.exec_())