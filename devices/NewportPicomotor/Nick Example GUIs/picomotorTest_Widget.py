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

from picoWidgetTest_GUI import Ui_Form

class picoMotor_App(QtWidgets.QWidget):
    def __init__(self,axes):
        super(picoMotor_App,self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.xAxis = axes[0]
        self.yAxis = axes[1]

        print(Newport.get_usb_devices_number_picomotor())

        try:
            self.stage = Newport.Picomotor8742()
        except Newport.base.NewportBackendError:
            print("Newport Picomotor controller could not be initialized.")
            self.stage = None
        self.ui.buttonLeft.clicked.connect(lambda: self.movePico(axis = self.xAxis,steps = self.ui.stepSize.value()))
        self.ui.buttonRight.clicked.connect(lambda: self.movePico(axis = self.xAxis,steps = -1*self.ui.stepSize.value()))
        self.ui.buttonUp.clicked.connect(lambda: self.movePico(axis = self.yAxis,steps = self.ui.stepSize.value()))
        self.ui.buttonDown.clicked.connect(lambda: self.movePico(axis = self.yAxis,steps = -1*self.ui.stepSize.value()))

    def movePico(self, axis, steps):
        self.stage.move_by(axis = axis, steps = steps)
        self.stage.wait_move()
    
    def close(self):
        self.stage.close()

if __name__ == "__main__":
    #from ResultsWindow import Results
    app = QtWidgets.QApplication(sys.argv)
    #qdarktheme.setup_theme()
    application = picoMotor_App([1,2])
    application.show()
    sys.exit(app.exec_())  