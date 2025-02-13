from PyQt5 import QtWidgets, QtCore, QtGui
import sys, os
from time import sleep
import RPi.GPIO as GPIO

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

# TO DO:  the current position should update for every step  

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
print(f"total microsteps: {microsteps_per_cm}")

# Define GPIO pin numbers for limit switches
LIMIT_SWITCH_LEFT_PIN = 21
LIMIT_SWITCH_RIGHT_PIN = 23

# Define the reference limit switch for homing the motor
homing_limit_switch_pin = LIMIT_SWITCH_RIGHT_PIN  

class MotorMovement(QObject):
        
    update_position_signal = pyqtSignal(float)  # Signal to update position
    motor_status_signal = pyqtSignal(str)  # Signal to update motor status
    error_signal = pyqtSignal(str) # Signal to display error message
    pushbutton_state_signal = pyqtSignal(bool)  # Signal to enable or disable buttons 


    def __init__(self):
        super().__init__()

        GPIO.cleanup()

        # Setup GPIO mode
        GPIO.setmode(GPIO.BOARD)

        # Setup GPIO pins for limit switches
        GPIO.setup(LIMIT_SWITCH_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Left limit switch
        GPIO.setup(LIMIT_SWITCH_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Right limit switch

        switch_state_right =  GPIO.input(LIMIT_SWITCH_RIGHT_PIN)
        print(f"Right limit Switch State {switch_state_right}")

        switch_state_left =  GPIO.input(LIMIT_SWITCH_LEFT_PIN)
        print(f"Left limit Switch State {switch_state_left}")

        # Setup GPIO pins
        GPIO.setup(DIR, GPIO.OUT)
        GPIO.setup(STEP, GPIO.OUT)


        
        self.current_position = 0.00

    def run(self, run_mode, input_distance):   # run_mode == "move right" or "move left"

        print(f"MotorMovement.run() started: {run_mode}, {input_distance}")
        
        if run_mode == "move left":
            self.MotorRun(run_mode, input_distance)  

        if run_mode == "move right":
            self.MotorRun(run_mode, input_distance) 

    def StopMotorRun(self):

        """Set the stop command to True to interrupt the motor movement."""

        self.stop_command = True
        print("Stop button pressed. Stopping motor...")


    def update_position(self, steps, direction_command):

        """Update the current position based on steps and direction."""
        
        distance_moved = steps / microsteps_per_cm
        if direction_command == "move left":
            self.current_position += distance_moved
        elif direction_command == "move right":
            self.current_position -= distance_moved

        self.update_position_signal.emit(self.current_position) 
        #print(f"Position Updated: {self.current_position}") 
        

    def MotorRun(self,direction_command,distance_in_cm):
        #Common code here
        steps = round(distance_in_cm * microsteps_per_cm)  # Convert to steps
        self.stop_command = False
        self.pushbutton_state_signal.emit(False)
        self.motor_status_signal.emit("Moving...")

        if direction_command == "move right":
            #code for moving right with the right limit switch
            try:
                GPIO.output(DIR, CW)
                for _ in range(steps):
                    # Check if the stop command is set
                    #switch_state_right =  GPIO.input(LIMIT_SWITCH_RIGHT_PIN)
                    #print(f"Limit Switch State {switch_state_right}")
                    if self.stop_command:  
                        print("Movement interrupted.")
                        self.motor_status_signal.emit("Stopped")
                        break

                    # Check if the right limit switch is pressed
                    if GPIO.input(LIMIT_SWITCH_RIGHT_PIN) == GPIO.LOW:
                        print("Right limit reached!")
                        self.motor_status_signal.emit("Right End")
                        self.HomeMotorRun()  # Call the HomeMotor method to handle homing and reset position to 0
                        break  # Stop if limit switch is pressed

                    GPIO.output(STEP, GPIO.HIGH)
                    sleep(0.001)  # Speed control
                    GPIO.output(STEP, GPIO.LOW)
                    sleep(0.001)  # Speed control

                    # update position for each step
                    self.update_position(1, "move right")

                # Update position if the movement is completed without hitting the limit
                if GPIO.input(LIMIT_SWITCH_RIGHT_PIN) != GPIO.LOW:
                    self.motor_status_signal.emit("Stopped")

            except ValueError:
                self.error_signal.emit("Invalid input. Please enter a valid number.")

            finally:
                self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
                self.motor_status_signal.emit("Stopped")


        elif direction_command == "move left":
                #code for moving left with the left limit switch
            try:
                GPIO.output(DIR, CCW)
                for step in range(steps):
                    #switch_state_left =  GPIO.input(LIMIT_SWITCH_LEFT_PIN)
                    #print(f"Limit Switch State {switch_state_left}")
                    # Check if the stop command is set
                    if self.stop_command: 
                        print("Movement interrupted.")
                        self.motor_status_signal.emit("Stopped")
                        break

                    # Check if the left limit switch is pressed
                    if GPIO.input(LIMIT_SWITCH_LEFT_PIN) == GPIO.LOW:
                        print("Left limit reached!")
                        self.motor_status_signal.emit("Left End")

                        # Reverse direction slowly until the limit switch is released
                        GPIO.output(DIR, CW)  # Reverse direction
                        while GPIO.input(LIMIT_SWITCH_LEFT_PIN) == GPIO.LOW:
                            GPIO.output(STEP, GPIO.HIGH)
                            sleep(0.0015)  # Slow speed
                            GPIO.output(STEP, GPIO.LOW)
                            sleep(0.0015)  # Slow speed

                        # Stop the motor and update position
                        self.update_position(step, "move left")
                        return  

                    GPIO.output(STEP, GPIO.HIGH)
                    sleep(0.001)  # Speed control
                    GPIO.output(STEP, GPIO.LOW)
                    sleep(0.001)  # Speed control

                    #update position for each step
                    self.update_position(1, "move left")

                # Update position if the movement is completed without hitting the limit
                if GPIO.input(LIMIT_SWITCH_LEFT_PIN) != GPIO.LOW:
                    self.motor_status_signal.emit("Stopped")

            except ValueError:
                self.error_signal.emit("Invalid input. Please enter a valid number.")

            finally:
                self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
                self.motor_status_signal.emit("Stopped")


    def HomeMotorRun(self):
        """Homing logic using the right limit switch."""
        try:
            # Move towards the right limit switch
            GPIO.output(DIR, CW) 
            self.stop_command = False
            self.pushbutton_state_signal.emit(False)
            self.motor_status_signal.emit("Moving...")

            while GPIO.input(homing_limit_switch_pin) == GPIO.HIGH:  # While the switch is not pressed
                # Check if the stop command is set
                if self.stop_command:  
                    print("Movement interrupted.")
                    self.motor_status_signal.emit("Stopped")
                    break
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.001)  
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.001)

            # Once the limit switch is pressed, reverse direction away from the switch slowly
            GPIO.output(DIR, CCW)  
            while GPIO.input(homing_limit_switch_pin) == GPIO.LOW:  # wait until the switch is released
                # Check if the stop command is set
                if self.stop_command:  
                    print("Movement interrupted.")
                    self.motor_status_signal.emit("Stopped")
                    break
                GPIO.output(STEP, GPIO.HIGH)
                sleep(0.0015)  # Slow speed
                GPIO.output(STEP, GPIO.LOW)
                sleep(0.0015)  # Slow speed

            # Stop the motor once the limit switch is released
            GPIO.output(STEP, GPIO.LOW) 

            # Reset position to 0.0cm (home position)
            self.current_position = 0.0
            self.update_position_signal.emit(self.current_position) # update display
            print("Home position set.")

        except Exception as e:
            self.error_signal.emit(f"Error in homing: {str(e)}")

        finally:
            self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
            self.motor_status_signal.emit("Stopped")   
            

class StepperMotorControl(QtWidgets.QMainWindow):

    motorRun_signals = pyqtSignal(str, float) # Signals for "direction and input distance" for left and right motor run
    homing_signal = pyqtSignal() # Signal for homing motor.

    def __init__(self):
        super(StepperMotorControl, self).__init__()

        self.ui = Ui_Form()  # Create an instance of the generated UI class
        self.ui.setupUi(self)  # Set up the UI within this widget

        self.ui.LeftButton.clicked.connect(self.LeftMotorRunGUI)
        self.ui.RightButton.clicked.connect(self.RightMotorRunGUI)
        self.ui.HomeButton.clicked.connect(self.HomeMotorRunGUI)
        self.ui.StopButton.clicked.connect(self.StopMotorRunGUI)

        # Initialize the latest position
        self.latest_position = 0.00

        # Initialize the MotorMovement worker and its thread
        self.motorWorker = MotorMovement()
        self.motorWorker_thread = QThread()  

        # Move the worker to its thread
        self.motorWorker.moveToThread(self.motorWorker_thread)

        # Connect GUI signals to worker methods
        print("connecting motorRun_signals to MotorMovement.run()")
        self.motorRun_signals.connect(self.motorWorker.run)
        self.homing_signal.connect(self.motorWorker.HomeMotorRun)

        # Connect worker signals to GUI methods
        self.motorWorker.update_position_signal.connect(self.handle_position_update)
        self.motorWorker.motor_status_signal.connect(self.updateMotorStatus)
        self.motorWorker.pushbutton_state_signal.connect(self.set_pushbutton_states)
        self.motorWorker.error_signal.connect(self.showErrorMessage)

        # start the worker thread
        print("Starting motorWorker thread...")
        self.motorWorker_thread.start()

        # Set up QTimer for periodic display updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_position_display)
        self.timer.start(100)  # Update every 100 milliseconds

        # show the window
        self.show()

    def toggle_motor_GUI(self):
        """Toggle the motor state between enabled and disabled."""
        if self.motor_enabled:
            # Emit a signal to disable the motor
            self.motorWorker.disable_motor()
        else:
            # Emit a signal to enable the motor
            self.motorWorker.enable_motor()


    def update_toggle_button_from_signal(self, enabled):

        """Update the toggle button's state based on the motor_enabled_signal."""

        self.motor_enabled = enabled
        self.update_toggle_button()


    def update_toggle_button(self):

        """Update the toggle button's text and color based on the motor state."""
        EnableMotor_stylesheet = """QLabel {background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #99FF99, stop:1 #33CC33);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #00AA00;
                    text-align: center;}"""
        
        DisableMotor_stylesheet = """QLabel {background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #FF6666, stop:1 #CC0000);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 12pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #AA0000;
                    text-align: center;}"""

        if self.motor_enabled:
            self.ui.toggleMotorButton.setText("Disable")
            self.ui.toggleMotorButton.setStyleSheet(EnableMotor_stylesheet)
        else:
            self.ui.toggleMotorButton.setText("Enable")
            self.ui.toggleMotorButton.setStyleSheet(DisableMotor_stylesheet)

    def LeftMotorRunGUI(self):
        distance_in_cm = float(self.ui.MovingDistance.value())  # User input in cm
        print(f"Emitting signals: move left {distance_in_cm} cm")
        self.motorRun_signals.emit("move left", distance_in_cm)
       
    def RightMotorRunGUI(self):
        distance_in_cm = float(self.ui.MovingDistance.value())  # User input in cm
        print(f"Emitting signals: move right {distance_in_cm} cm")
        self.motorRun_signals.emit("move right", distance_in_cm)

    def HomeMotorRunGUI(self):
        self.homing_signal.emit()  

    def StopMotorRunGUI(self):
        self.motorWorker.StopMotorRun()

    def handle_position_update(self, position):
        """Handle position updates from the worker."""
        self.latest_position = position
        #print(f"GUI received position update: {position}")

    def refresh_position_display(self):
        """Update the display with the latest position."""
        self.ui.DisplayCurrentDistance.display(self.latest_position)

    def set_pushbutton_states(self, enabled):
        """
        Enable or disable buttons except the Stop button.

        Arg: enabled: True to enable, False to disable.

        """
        self.ui.LeftButton.setEnabled(enabled)
        self.ui.RightButton.setEnabled(enabled)
        self.ui.HomeButton.setEnabled(enabled)

    def updateMotorStatus(self, status):
        """
        Update the motor status label.
        Arg: 
        status: "Moving..." or "Stopped"
        """

        motion_styleSheet = """QLabel {background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #99FF99, stop:1 #33CC33);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 9pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #00AA00;
                    text-align: center;}"""
        
        stop_styleSheet ="""QLabel {background-color: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #FF6666, stop:1 #CC0000);
                    color: white;
                    border-radius: 10px;
                    font-style: italic;                               
                    font-size: 9pt;
                    font-weight: bold;
                    padding: 5px;
                    border: 2px solid #AA0000;
                    text-align: center;}"""
            
        if status == "Moving...":
            self.ui.MotorStatusLabel.setText("Moving...")
            self.ui.MotorStatusLabel.setStyleSheet(motion_styleSheet)

        elif status == "Stopped":
            self.ui.MotorStatusLabel.setText("Stopped")
            self.ui.MotorStatusLabel.setStyleSheet(stop_styleSheet)

        elif status == "Left End":
            self.ui.MotorStatusLabel.setText("Left End")
            self.ui.MotorStatusLabel.setStyleSheet(stop_styleSheet)

        elif status == "Right End":
            self.ui.MotorStatusLabel.setText("Right End")
            self.ui.MotorStatusLabel.setStyleSheet(stop_styleSheet)
        
    def showErrorMessage(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", message)

    def closeEvent(self,event):
        print ("Cleaning up GPIO before exit...")
        GPIO.cleanup()
        event.accept() #Allow window to close
 
# Initialize and run the application
if __name__ == "__main__":
    try:
        app = QtWidgets.QApplication(sys.argv)
        window = StepperMotorControl()
        window.show()
        sys.exit(app.exec_())
    finally:
        print("Cleaning up GPIO before exiting...")
        GPIO.cleanup()