import sys, os
from time import sleep
import RPi.GPIO as GPIO

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread

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
from devices.StepperMotor.motor_config import MotorConfig

class MotorMovement(QObject):
    """
    This class handles the logic for controlling the stepper motor, including movement, homing, and position tracking. 
    It communicates with the GUI through signals.

    Attributes:
        config: An instance of MotorConfig containing GPIO and motor configuration.
        motor_enabled: Tracks whether the motor is enabled or disabled.
        current_position: Tracks the current position of the motor in centimeters.
        stop_command: A flag to stop the motor movement.

    Signals:
        update_position_signal: Emits the updated position of the motor.
        motor_status_signal: Emits the current status of the motor (e.g., "Moving...", "Stopped").
        error_signal: Emits error messages.
        pushbutton_state_signal: Emits the state of push buttons (enabled/disabled).
        motor_enabled_signal: Emits the state of the motor (enabled/disabled).

    Methods:
        __init__: Initializes GPIO pins and motor state.
        enable_motor: Enables the motor by setting the ENA pin low.
        disable_motor: Disables the motor by setting the ENA pin high.
        run: Starts the motor movement based on the direction ("move left" or "move right") and distance.
        StopMotorRun: Stops the motor movement by setting the stop_command flag.
        update_position: Updates the current position of the motor based on steps and direction.
        MotorRun: Handles the motor movement logic, including limit switch checks and position updates.
        HomeMotorRun: Implements homing logic using the right limit switch.

    """
        
    update_position_signal = pyqtSignal(float)  
    motor_status_signal = pyqtSignal(str)  
    error_signal = pyqtSignal(str) 
    pushbutton_state_signal = pyqtSignal(bool)  
    motor_enabled_signal = pyqtSignal(bool)  


    def __init__(self):
        super().__init__()

        self.config = MotorConfig()
        self.motor_enabled = False  # Track motor state
        self.current_position = 0.00

        GPIO.cleanup()

        # Setup GPIO mode
        GPIO.setmode(GPIO.BOARD)

        # Setup GPIO pins for limit switches
        GPIO.setup(self.config.LIMIT_SWITCH_LEFT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
        GPIO.setup(self.config.LIMIT_SWITCH_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

        # Setup GPIO pins
        GPIO.setup(self.config.DIR, GPIO.OUT)
        GPIO.setup(self.config.STEP, GPIO.OUT)
        GPIO.setup(self.config.ENA, GPIO.OUT)

        # Initialize the motor as OFF (ENA high to disable the driver)
        GPIO.output(self.config.ENA, GPIO.HIGH) 

    def enable_motor(self):
        GPIO.output(self.config.ENA, GPIO.LOW)
        self.motor_enabled = True
        self.motor_enabled_signal.emit(True)
        print("Motor enabled.")

    def disable_motor(self):
        GPIO.output(self.config.ENA, GPIO.HIGH)
        self.motor_enabled = False
        self.motor_enabled_signal.emit(False)
        print("Motor disabled.")

    def run(self, run_mode, input_distance): 
        self.enable_motor()     # Enable the motor before movement
        if run_mode == "move left":
            self.MotorRun(run_mode, input_distance)  
        elif run_mode == "move right":
            self.MotorRun(run_mode, input_distance) 

    def StopMotorRun(self):
        self.stop_command = True
        print("Stop button pressed. Stopping motor...")

    def update_position(self, steps, direction_command):
        distance_moved = steps / self.config.microsteps_per_cm
        if direction_command == "move left":
            self.current_position += distance_moved
        elif direction_command == "move right":
            self.current_position -= distance_moved

        self.update_position_signal.emit(self.current_position) 
        
    def MotorRun(self,direction_command,distance_in_cm):
        steps = round(distance_in_cm * self.config.microsteps_per_cm)  
        self.stop_command = False
        self.pushbutton_state_signal.emit(False)
        self.motor_status_signal.emit("Moving...")

        if direction_command == "move right":
            try:
                GPIO.output(self.config.DIR, self.config.CW)
                for _ in range(steps):
                    if self.stop_command:  
                        print("Movement interrupted.")
                        self.motor_status_signal.emit("Stopped")
                        break

                    # Check if the right limit switch is pressed
                    if GPIO.input(self.config.LIMIT_SWITCH_RIGHT_PIN) == GPIO.LOW:
                        print("Right limit reached!")
                        self.motor_status_signal.emit("Right End")
                        self.HomeMotorRun()  # Call the HomeMotor method to handle homing and reset position to 0
                        break  # Stop if limit switch is pressed

                    GPIO.output(self.config.STEP, GPIO.HIGH)
                    sleep(0.001)  # Speed control
                    GPIO.output(self.config.STEP, GPIO.LOW)
                    sleep(0.001)  # Speed control

                    # update position for each step
                    self.update_position(1, "move right")

                # Update position if the movement is completed without hitting the limit
                if GPIO.input(self.config.LIMIT_SWITCH_RIGHT_PIN) != GPIO.LOW:
                    self.motor_status_signal.emit("Stopped")

            except ValueError:
                self.error_signal.emit("Invalid input. Please enter a valid number.")

            finally:
                # Disable the motor only if the toggle button is in the "disabled" state
                if not self.motor_enabled:
                    self.disable_motor()
                self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
                self.motor_status_signal.emit("Stopped")

        elif direction_command == "move left":
            try:
                GPIO.output(self.config.DIR, self.config.CCW)
                for step in range(steps):
                    if self.stop_command: 
                        print("Movement interrupted.")
                        self.motor_status_signal.emit("Stopped")
                        break

                    # Check if the left limit switch is pressed
                    if GPIO.input(self.config.LIMIT_SWITCH_LEFT_PIN) == GPIO.LOW:
                        print("Left limit reached!")
                        self.motor_status_signal.emit("Left End")

                        # Reverse direction slowly until the limit switch is released
                        GPIO.output(self.config.DIR, self.config.CW)  # Reverse direction
                        while GPIO.input(self.config.LIMIT_SWITCH_LEFT_PIN) == GPIO.LOW:
                            GPIO.output(self.config.STEP, GPIO.HIGH)
                            sleep(0.0015)  # Slow speed
                            GPIO.output(self.config.STEP, GPIO.LOW)
                            sleep(0.0015)  # Slow speed

                        # Stop the motor and update position
                        self.update_position(step, "move left")
                        return  

                    GPIO.output(self.config.STEP, GPIO.HIGH)
                    sleep(0.001)  # Speed control
                    GPIO.output(self.config.STEP, GPIO.LOW)
                    sleep(0.001)  # Speed control

                    #update position for each step
                    self.update_position(1, "move left")

                # Update position if the movement is completed without hitting the limit
                if GPIO.input(self.config.LIMIT_SWITCH_LEFT_PIN) != GPIO.LOW:
                    self.motor_status_signal.emit("Stopped")

            except ValueError:
                self.error_signal.emit("Invalid input. Please enter a valid number.")

            finally:
                # Disable the motor only if the toggle button is in the "disabled" state
                if not self.motor_enabled:
                    self.disable_motor()
                self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
                self.motor_status_signal.emit("Stopped")


    def HomeMotorRun(self):
        try:

            # Enable the motor before homing
            self.enable_motor()

            # Move towards the right limit switch
            GPIO.output(self.config.DIR, self.config.CW) 
            self.stop_command = False
            self.pushbutton_state_signal.emit(False)
            self.motor_status_signal.emit("Moving...")

            while GPIO.input(self.config.homing_limit_switch_pin) == GPIO.HIGH:  # While the switch is not pressed
                # Check if the stop command is set
                if self.stop_command:  
                    print("Movement interrupted.")
                    self.motor_status_signal.emit("Stopped")
                    break
                GPIO.output(self.config.STEP, GPIO.HIGH)
                sleep(0.001)  
                GPIO.output(self.config.STEP, GPIO.LOW)
                sleep(0.001)

            # Once the limit switch is pressed, reverse direction away from the switch slowly
            GPIO.output(self.config.DIR, self.config.CCW)  
            while GPIO.input(self.config.homing_limit_switch_pin) == GPIO.LOW:  # wait until the switch is released
                # Check if the stop command is set
                if self.stop_command:  
                    print("Movement interrupted.")
                    self.motor_status_signal.emit("Stopped")
                    break
                GPIO.output(self.config.STEP, GPIO.HIGH)
                sleep(0.0015)  # Slow speed
                GPIO.output(self.config.STEP, GPIO.LOW)
                sleep(0.0015)  # Slow speed

            # Stop the motor once the limit switch is released
            GPIO.output(self.config.STEP, GPIO.LOW) 

            # Reset position to 0.00cm (home position)
            self.current_position = 0.00
            self.update_position_signal.emit(self.current_position) # update display
            print("Home position set.")

        except Exception as e:
            self.error_signal.emit(f"Error in homing: {str(e)}")

        finally:
            # Disable the motor only if the toggle button is in the "disabled" state
            if not self.motor_enabled:
                self.disable_motor()
            self.pushbutton_state_signal.emit(True) # Re-enable other push buttons
            self.motor_status_signal.emit("Stopped")   
            

class StepperMotorControl(QMainWindow):
    """
    This class represents the main GUI window and handles user interactions. 
    It connects the GUI signals to the MotorMovement class methods.

    Attributes:
        ui: An instance of the generated UI class (Ui_Form).
        latest_position: Tracks the latest position of the motor for display.
        motor_enabled: Tracks whether the motor is enabled or disabled.
        config: An instance of MotorConfig containing GPIO and motor configuration.
        motorWorker: An instance of MotorMovement for motor control logic.
        motorWorker_thread: A QThread to run the MotorMovement worker in the background.
        timer: A QTimer for periodic updates of the position display.

    Signals:
        motorRun_signals: Emits the direction and distance for motor movement.
        homing_signal: Emits a signal to initiate homing.

    Methods:
        __init__: Initializes the GUI, connects signals and slots, and starts the worker thread.
        toggle_motor_GUI: Toggles the motor state between enabled and disabled.
        update_toggle_button_from_signal: Updates the toggle button state based on the motor state.
        update_toggle_button: Updates the toggle button's text and color based on the motor state.
        LeftMotorRunGUI: Emits a signal to move the motor left.
        RightMotorRunGUI: Emits a signal to move the motor right.
        HomeMotorRunGUI: Emits a signal to initiate homing.
        StopMotorRunGUI: Stops the motor movement.
        handle_position_update: Updates the latest position of the motor.
        refresh_position_display: Updates the position display on the GUI.
        set_pushbutton_states: Enables or disables buttons based on the motor state.
        updateMotorStatus: Updates the motor status label and its appearance.
        showErrorMessage: Displays error messages in a QMessageBox.
        closeEvent: Cleans up GPIO pins when the window is closed.

    """

    motorRun_signals = pyqtSignal(str, float) # Signals for "direction and input distance" for left and right motor run
    homing_signal = pyqtSignal() # Signal for homing motor.

    def __init__(self):
        super(StepperMotorControl, self).__init__()

        self.ui = Ui_Form()  # Create an instance of the generated UI class
        self.ui.setupUi(self)  # Set up the UI within this widget

        # Initialize the latest position
        self.latest_position = 0.00

        self.ui.LeftButton.clicked.connect(self.LeftMotorRunGUI)
        self.ui.RightButton.clicked.connect(self.RightMotorRunGUI)
        self.ui.HomeButton.clicked.connect(self.HomeMotorRunGUI)
        self.ui.StopButton.clicked.connect(self.StopMotorRunGUI)

        # Connect the toggle button
        self.ui.toggleMotorButton.clicked.connect(self.toggle_motor_GUI)

        # Initialize the button state
        self.motor_enabled = False  # Track motor state
        self.update_toggle_button()  

        # Initialize the MotorMovement worker and its thread
        self.config = MotorConfig()  # Create MotorConfig instance
        self.motorWorker = MotorMovement(self.config)
        self.motorWorker_thread = QThread()  

        # Move the worker to its thread
        self.motorWorker.moveToThread(self.motorWorker_thread)

        # Connect GUI signals to worker methods
        self.motorRun_signals.connect(self.motorWorker.run)
        self.homing_signal.connect(self.motorWorker.HomeMotorRun)

        # Connect worker signals to GUI methods
        self.motorWorker.update_position_signal.connect(self.handle_position_update)
        self.motorWorker.motor_status_signal.connect(self.updateMotorStatus)
        self.motorWorker.pushbutton_state_signal.connect(self.set_pushbutton_states)
        self.motorWorker.error_signal.connect(self.showErrorMessage)

        # Connect the new motor_enabled_signal to update the toggle button
        self.motorWorker.motor_enabled_signal.connect(self.update_toggle_button_from_signal)

        # start the worker thread
        self.motorWorker_thread.start()

        # Set up QTimer for periodic display updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_position_display)
        self.timer.start(100)  # Update every 100 milliseconds

        # show the window
        self.show()

    def toggle_motor_GUI(self):
        if self.motor_enabled:
            # Emit a signal to disable the motor
            self.motorWorker.disable_motor()
        else:
            # Emit a signal to enable the motor
            self.motorWorker.enable_motor()


    def update_toggle_button_from_signal(self, enabled):
        self.motor_enabled = enabled
        self.update_toggle_button()


    def update_toggle_button(self):
        DisableMotor_stylesheet = """
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #99FF99, stop:1 #33CC33);
                color: white;
                border-radius: 10px;
                font-style: italic;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px;
                border: 2px solid #00AA00;
                text-align: center;
            }
        """

        EnableMotor_stylesheet = """
            QPushButton {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #FF6666, stop:1 #CC0000);
                color: white;
                border-radius: 10px;
                font-style: italic;
                font-size: 12pt;
                font-weight: bold;
                padding: 5px;
                border: 2px solid #AA0000;
                text-align: center;
            }
        """

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
        self.latest_position = position

    def refresh_position_display(self):
        self.ui.DisplayCurrentDistance.display(self.latest_position)

    def set_pushbutton_states(self, enabled):
        self.ui.LeftButton.setEnabled(enabled)
        self.ui.RightButton.setEnabled(enabled)
        self.ui.HomeButton.setEnabled(enabled)

    def updateMotorStatus(self, status):

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
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self,event):
        print ("Cleaning up GPIO before exit...")
        GPIO.cleanup()
        event.accept() #Allow window to close
 
# Initialize and run the application
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = StepperMotorControl()
        window.show()
        sys.exit(app.exec_())
    finally:
        print("Cleaning up GPIO before exiting...")
        GPIO.cleanup()