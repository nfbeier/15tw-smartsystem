class MotorConfig:

    """
    The MotorConfig class contains all the configuration settings for the stepper motor, 
    including GPIO pin assignments, motor constants, and calibration factors. 
    
    """
    def __init__(self):
        # GPIO pins
        self.DIR = 10  # Direction pin
        self.STEP = 8  # Step pin
        self.ENA = 11  # Enable pin
        self.LIMIT_SWITCH_LEFT_PIN = 21  # Left limit switch pin
        self.LIMIT_SWITCH_RIGHT_PIN = 23  # Right limit switch pin
        self.homing_limit_switch_pin = self.LIMIT_SWITCH_RIGHT_PIN # Defines the reference limit switch for homing the motor

        # Motor constants
        self.CW = 1  # Clockwise direction
        self.CCW = 0  # Counter-clockwise direction

        # Calibration constants
        self.step_angle = 1.8  # Step angle in degrees
        self.motor_steps_per_revolution = 360 / self.step_angle  # Steps per revolution
        self.number_of_microsteps = 4  # Microsteps per step
        self.total_microsteps_per_revolution = self.motor_steps_per_revolution * self.number_of_microsteps
        self.screw_pitch_in_cm = 0.5  # Screw pitch in cm
        self.number_of_revolution_per_cm = 1 / self.screw_pitch_in_cm  # Revolutions per cm

        # Calibration factor
        self.microsteps_per_cm = self.total_microsteps_per_revolution * self.number_of_revolution_per_cm