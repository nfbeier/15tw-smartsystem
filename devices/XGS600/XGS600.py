import time
import serial

class XGS600Driver:
    '''
    Driver for the Agilent XGS600 Vacuum Gauge Controller
    '''

    def __init__(self,port = "",timeout = 2.0):
        self.serial = serial.Serial(port)
        self.timeout = timeout