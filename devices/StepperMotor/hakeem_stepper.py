from PyQt5 import QtWidgets, QtCore, QtGui
import sys, os
from time import sleep
import RPi.GPIO as GPIO

cwd = os.getcwd()
print(cwd)
# Check if '15tw-smartsystem' is in the components
if "15tw-smartsystem" not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(
    cwd.split(os.path.sep)[: cwd.split(os.path.sep).index("15tw-smartsystem") + 1]
)

sys.path.insert(0, cwd)

from devices.StepperMotor.Hakeem_StepperMotors import (Ui_Form) 

# Define GPIO pins and constants
global DIR, STEP, CW, CCW, log
DIR = 10  # the GPIO pin number on the Raspberry Pi that tells the motor what direction (CW or CCW) to move
STEP = 8  # the GPIO pin number on the Raspberry Pi that tells the motor to take a step
CW = 1
CCW = 0

# Calibration calculations
step_angle = 1.8  # NEMA 23 stepper motor with a 1.8-degree step angle
motor_steps_per_revolution = 360 / step_angle  # steps per revolution
number_of_microsteps = 4  # number of microsteps within each full step
total_microsteps_per_revolution = motor_steps_per_revolution * number_of_microsteps
screw_pitch_in_cm = 0.5  # Ballscrew moves 0.5 cm per revolution
number_of_revolution_per_cm = 1 / screw_pitch_in_cm  # revolutions per cm

# Calibration factor
microsteps_per_cm = total_microsteps_per_revolution * number_of_revolution_per_cm

# Setup GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
log = 0

# Define GPIO pin numbers for limit switches
LIMIT_SWITCH_LEFT_PIN = 12
LIMIT_SWITCH_RIGHT_PIN = 16

# Setup GPIO pins for limit switches
GPIO.setup(LIMIT_SWITCH_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Left limit switch
GPIO.setup(LIMIT_SWITCH_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Right limit switch


class StepperMotorControl(QtWidgets.QMainWindow):
    def __init__(self):
        super(StepperMotorControl, self).__init__()

        self.ui = Ui_Form()  # Create an instance of the generated UI class
        self.ui.setupUi(self)  # Set up the UI within this widget

        self.ui.LeftButton.clicked.connect(self.LeftMotorRun)
        self.ui.RightButton.clicked.connect(self.RightMotorRun)
        self.ui.HomeButton.clicked.connect(self.HomeMotor)

    def LeftMotorRun(self):
        try:
            distance_in_cm = float(self.ui.MovingDistance.value())  # User input in cm
            steps = round(distance_in_cm * microsteps_per_cm)  # Convert to steps
            GPIO.output(DIR, CCW)

            for _ in range(steps):
                # Check if the left limit switch is pressed
                if GPIO.input(LIMIT_SWITCH_LEFT_PIN) == GPIO.LOW:
                    print("Left limit reached!")
                    break  # Stop if limit switch is pressed

                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)  # Speed control
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)  # Speed control

        except ValueError:
            self.showErrorMessage("Invalid input. Please enter a valid number.")

    def RightMotorRun(self):
        try:
            distance_in_cm = float(self.ui.MovingDistance.value())  # User input in cm
            steps = round(distance_in_cm * microsteps_per_cm)  # Convert to steps
            GPIO.output(DIR, CW)

            for _ in range(steps):
                # Check if the right limit switch is pressed
                if GPIO.input(LIMIT_SWITCH_RIGHT_PIN) == GPIO.LOW:
                    print("Right limit reached!")
                    break  # Stop if limit switch is pressed

                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)  # Speed control
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)  # Speed control

        except ValueError:
            self.showErrorMessage("Invalid input. Please enter a valid number.")

    def HomeMotor(self):
        """Homing logic using the right limit switch."""
        try:
            # Move towards the right limit switch
            GPIO.output(DIR, CCW)  
            while GPIO.input(LIMIT_SWITCH_RIGHT_PIN) == GPIO.HIGH:  # While the switch is not pressed
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)  
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)

            # Once the limit switch is pressed, reverse direction away from the switch slowly
            GPIO.output(DIR, CW)  
            while GPIO.input(LIMIT_SWITCH_RIGHT_PIN) == GPIO.LOW:  # wait until the switch is released
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.0015)  # Slow speed
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.0015)  # Slow speed

            # Stop the motor once the limit switch is released
            GPIO.output(STEP, GPIO.LOW) 

            print("Home position set.")

        except Exception as e:
            self.showErrorMessage(f"Error in homing: {str(e)}")

    def showErrorMessage(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", message)

# Initialize and run the application
app = QtWidgets.QApplication(sys.argv)
window = StepperMotorControl()
window.show()
app.exec()