# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 14:30:47 2024

@author: Kyulg
"""

from PyQt5.QtWidgets import *
import pyqtgraph as pg
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import threading
import RPi.GPIO as GPIO
from time import sleep


global DIR
global STEP 
global CW
global CCW
global log
DIR = 10
STEP = 8
CW = 1
CCW = 0
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
log=0

uiclass, baseclass =pg.Qt.loadUiType('StepperMotors.ui')
class MainWindow(uiclass, baseclass):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.Left.clicked.connect(self.LeftMotorRun)
        self.Right.clicked.connect(self.RightMotorRun)

    def LeftMotorRun(self):
        steps = round(int(self.Steps.toPlainText())*615.384615)
        GPIO.output(DIR, CW)
        

        for x in range(steps):

			# Set one coil winding to high
            GPIO.output(STEP,GPIO.HIGH)
			# Allow it to get there.
            sleep(.001) # Dictates how fast stepper motor will run
 			# Set coil winding to low
            GPIO.output(STEP,GPIO.LOW)
            sleep(.001) # Dictates how fast stepper motor will run

    def RightMotorRun(self):
        steps = round(int(self.Steps.toPlainText())*615.384615)
        GPIO.output(DIR, CCW)
        for x in range(steps):

			# Set one coil winding to high
            GPIO.output(STEP,GPIO.HIGH)
			# Allow it to get there.
            sleep(.001) # Dictates how fast stepper motor will run
 			# Set coil winding to low
            GPIO.output(STEP,GPIO.LOW)
            sleep(.001) # Dictates how fast stepper motor will run

        


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()