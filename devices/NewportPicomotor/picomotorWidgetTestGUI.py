import numpy as np
from pylablib.devices import Newport
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

sys.path.append(r'C:\Users\HK-47\Documents\CODE\GitHub\15tw-smartsystem\devices\NewportPicomotor')
from picoWidgetTest_GUI import Ui_Form

class picoMotor_App(QtWidgets.QWidget):
    def __init__(self,axes):
        super(picoMotor_App,self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.xAxis = axes[0]
        self.yAxis = axes[1]

        self.stage = Newport.Picomotor8742()
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
    application = picoMotor_App([3,4])
    application.show()
    sys.exit(app.exec_())  