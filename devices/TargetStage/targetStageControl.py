# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 13:21:12 2024

@author: User
"""
# Importing necessary libraries
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QLabel
import numpy as np
import sys, os
from fractions import Fraction
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

cwd = os.getcwd()
if "15tw-smartsystem" not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")
# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(
    cwd.split(os.path.sep)[: cwd.split(os.path.sep).index("15tw-smartsystem") + 1]
)
sys.path.insert(0, cwd)

from devices.TargetStage.targetStage_GUI import Ui_MainWindow
from devices.XPS.XPS import XPS


# Main class for GUI
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # STAGE CONTROL ----------------------------------------------------------------------
        # Access the QWidget by its object name in Qt Designer

        self.rasterPlotWidget = self.findChild(QtWidgets.QWidget, "rasterPlotWidget")
        self.groupCombo = [self.x_group_combo, self.y_group_combo, self.z_group_combo]
        self.xpsAxes = []
        try:
            self.xps = XPS()
            self.xps_groups = self.xps.getXPSStatus()

            for idx, axis in enumerate(self.groupCombo):
                axis.clear()
                axis.addItems(list(self.xps_groups.keys()))
                axis.setCurrentIndex(idx)
                self.xpsAxes.append(str(axis.currentText()))
                self.xps.setGroup(self.xpsAxes[-1])

            self.stageStatus = [self.xps.getStageStatus(axis) for axis in self.xpsAxes]
        except AttributeError:
            self.xps = None

        self.x_group_combo.activated.connect(lambda: self.update_group("X"))
        self.y_group_combo.activated.connect(lambda: self.update_group("Y"))
        self.z_group_combo.activated.connect(lambda: self.update_group("Z"))

        self.x_slider.setValue(int(self.xps.getStagePosition(self.xpsAxes[0]) * 10))
        self.y_slider.setValue(int(self.xps.getStagePosition(self.xpsAxes[1]) * 10))
        self.z_slider.setValue(int(self.xps.getStagePosition(self.xpsAxes[2]) * 10))

        self.stageStatus = [self.xps.getStageStatus(axis) for axis in self.xpsAxes]

        """Nick edits up to here"""

        # self.setupUi(self)
        self.abs_max = [
            40.00000,
            40.00000,
            40.00000,
        ]  # Maximum absolute position of the stage
        self.abs_min = [
            0.00000,
            0.00000,
            0.00000,
        ]  # Minimum absolute position of the stage
        self.rast_timer = QtCore.QTimer(self)
        self.error_flag = False
        self.x_reference = None
        # self.rep_rate=2
        self.x_pos = 0
        # Initialize the matplotlib canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.grid(True)
        # Add the canvas to the QWidget (rasterPlotWidget)
        layout = QtWidgets.QVBoxLayout(self.rasterPlotWidget)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        # X Axis Slider
        self.x_slider = self.findChild(QtWidgets.QSlider, "x_slider")
        self.x_slider.setPageStep(1)
        self.slider_factor = 10  # This will allow increments of 0.1 mm
        self.x_slider.setMinimum(0)  # Represents 0.1 mm
        self.x_slider.setMaximum(int(self.abs_max[0] * 10))  # Represents 40.0 mm
        self.x_slider.setTickInterval(10)
        self.x_slider.valueChanged.connect(
            lambda: self.update_position_from_scrollbar("X_slider")
        )  # Connect the scrollbar to the update function
        # Y Axis Slider
        self.y_slider = self.findChild(QtWidgets.QSlider, "y_slider")
        self.y_slider.setPageStep(1)
        self.slider_factor = 10  # This will allow increments of 0.1 mm
        self.y_slider.setMinimum(0)  # Represents 0.1 mm
        self.y_slider.setMaximum(int(self.abs_max[1] * 10))  # Represents 40.0 mm
        self.y_slider.setTickInterval(10)
        self.y_slider.valueChanged.connect(
            lambda: self.update_position_from_scrollbar("Y_slider")
        )  # Connect the scrollbar to the update function
        # Z Axis Slider
        self.z_slider = self.findChild(QtWidgets.QSlider, "z_slider")
        self.z_slider.setPageStep(1)
        self.slider_factor = 10  # This will allow increments of 0.1 mm
        self.z_slider.setMinimum(0)  # Represents 0.1 mm
        self.z_slider.setMaximum(int(self.abs_max[1] * 10))  # Represents 40.0 mm
        self.z_slider.setTickInterval(10)
        self.z_slider.valueChanged.connect(
            lambda: self.update_position_from_scrollbar("Z_slider")
        )  # Connect the scrollbar to the update function

        # Raster Input Boxes
        self.step_length_line.setValidator(QtGui.QDoubleValidator(0.10, 40.00, 2))
        self.step_length_line.textChanged.connect(
            lambda: self.raster_inp("step_length")
        )
        self.sample_length_line.setValidator(QtGui.QDoubleValidator(0.10, 40.00, 2))
        self.sample_length_line.textChanged.connect(
            lambda: self.raster_inp("sample_length")
        )
        self.sample_width_line.setValidator(QtGui.QDoubleValidator(0.10, 40.00, 2))
        self.sample_width_line.textChanged.connect(
            lambda: self.raster_inp("sample_width")
        )
        self.set_x_bound.clicked.connect(lambda: self.raster_inp("set_bound_x"))
        self.set_y_bound.clicked.connect(lambda: self.raster_inp("set_bound_y"))
        # self.num_shots_line.setEnabled(False)
        # self.num_shots_line.textChanged.connect(lambda: self.raster_inp('num_shots'))
        self.rep_rate_line.setValidator(QtGui.QDoubleValidator(1, 40.00, 1))
        self.rep_rate_line.textChanged.connect(lambda: self.raster_inp("Rep_rate"))

        # Raster Controls
        self.raster_btn.setEnabled(False)
        self.raster_btn.clicked.connect(self.start_raster)
        # Connect the stop button to stop the timer:
        self.stop_btn_2.clicked.connect(self.rast_timer.stop)

        # Log window
        # layout=QtWidgets.QVBoxLayout()
        # self.log_window = QtWidgets.QTextEdit()
        # self.log_window.setReadOnly(True)
        # self.log_window.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        # # layout.addWidget(QtWidgets.QVBoxLayout("log:"))
        # layout.addWidget(self.log_window)
        # Relative Motion Controls
        self.step_interval_x.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.step_interval_y.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.step_interval_z.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.left_btn.clicked.connect(lambda: self.relative("left"))
        self.right_btn.clicked.connect(lambda: self.relative("right"))
        self.down_btn.clicked.connect(lambda: self.relative("down"))
        self.up_btn.clicked.connect(lambda: self.relative("up"))
        self.down_btn_z.clicked.connect(lambda: self.relative("down_z"))
        self.up_btn_z.clicked.connect(lambda: self.relative("up_z"))
        # Status Buttons
        self.initialize_btn.clicked.connect(self.initialize)
        self.kill_btn.clicked.connect(self.kill)
        self.enable_btn.clicked.connect(self.enable_disable)

        # Absolute Motion Controls
        self.abs_x_line.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.abs_x_line.textChanged.connect(lambda: self.chkvalue("abs_x_length"))
        self.abs_y_line.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.abs_y_line.textChanged.connect(lambda: self.chkvalue("abs_y_length"))
        self.abs_z_line.setValidator(QtGui.QDoubleValidator(0.10, 50.00, 2))
        self.abs_z_line.textChanged.connect(lambda: self.chkvalue("abs_z_length"))
        self.abs_move_btn.clicked.connect(self.absolute)

        # Reference Point Commands
        self.ref = [
            0.00000,
            0.00000,
            0.00000,
        ]  # Initialize reference point for both x and y axes
        self.ref_x = 0.00000  # Initialize reference point for x-axis
        self.ref_y = 0.00000  # Initialize reference point for y-axis
        self.ref_z = 0.00000  # Initialize reference point for z-axis
        # Connect buttons to the ref_commands method for individual axes
        self.set_x_btn.clicked.connect(lambda: self.ref_commands("set", "x"))
        self.return_x_btn.clicked.connect(lambda: self.ref_commands("return", "x"))
        self.set_y_btn.clicked.connect(lambda: self.ref_commands("set", "y"))
        self.return_y_btn.clicked.connect(lambda: self.ref_commands("return", "y"))
        self.set_z_btn.clicked.connect(lambda: self.ref_commands("set", "z"))
        self.return_z_btn.clicked.connect(lambda: self.ref_commands("return", "z"))
        # Combined set and return buttons for both axes
        self.set_both_btn.clicked.connect(lambda: self.ref_commands("set", "both"))
        self.return_both_btn.clicked.connect(
            lambda: self.ref_commands("return", "both")
        )

        # Timer and Printing of Stage Location
        self.print_timer = QtCore.QTimer(
            self, interval=1000, timeout=self.print_location
        )
        self.print_timer.start()
        self.print_location()

    def ref_commands(self, cmd, axis):
        """
        Controls commands relating to the reference point of the stage.

        Parameters
        ----------
        cmd (string) : Button pressed that determines what command to trigger ("set" or "return").
        axis (string): Axis to apply the command to ('x', 'y', or 'both').
        """
        if cmd == "set":
            if axis == "x":
                self.ref_x = round(self.x_xps.getStagePosition(self.x_axis), 2)
                self.ref[0] = round(self.ref_x, 2)  # Update self.ref for x-axis
                self.position_x_ref.setText(f"Ref. X is: {self.ref[0]:.2f} mm")
                self.log_window.append(f"Set Ref. X to {self.ref[0] :.2f} mm. ")
                # Update the marker on the slider
            #  self.update_slider_marker()
            elif axis == "y":
                self.ref_y = round(self.y_xps.getStagePosition(self.y_axis), 2)
                self.ref[1] = round(self.ref_y, 2)  # Update self.ref for y-axis
                self.position_y_ref.setText(f"Ref. Y is: {self.ref[1]:.2f} mm")
                self.log_window.append(f"Set Ref. Y to {self.ref[1] :.2f} mm.")
            elif axis == "z":
                self.ref_z = round(self.z_xps.getStagePosition(self.z_axis), 2)
                self.ref[2] = round(self.ref_z, 2)  # Update self.ref for z-axis
                self.position_z_ref.setText(f"Ref. Z is: {self.ref[2]:.2f} mm")
                self.log_window.append(f"Set Ref. Z to {self.ref[2] :.2f} mm.")

            elif axis == "both":
                self.log_window.append(
                    f"Clicked button! Set Ref. XYZ to ({self.ref[0] :.2f}, {self.ref[1] :.2f}, {self.ref[1] :.2f} ) mm."
                )
                self.ref_x = round(self.x_xps.getStagePosition(self.x_axis), 2)
                self.ref_y = round(self.y_xps.getStagePosition(self.y_axis), 2)
                self.ref_z = round(self.z_xps.getStagePosition(self.z_axis), 2)
                self.ref = [
                    self.ref_x,
                    self.ref_y,
                    self.ref_z,
                ]  # Update self.ref for three axes

        elif cmd == "return":
            if axis == "x":
                self.log_window.append(f"Clicked button! Return X to Ref. Point. ")
                self.x_xps.moveAbsolute(self.x_axis, self.ref_x)

            elif axis == "y":
                self.log_window.append(f"Clicked button! Return Y to Ref. Point.")
                self.y_xps.moveAbsolute(self.y_axis, self.ref_y)
            elif axis == "z":
                self.log_window.append(f"Clicked button! Return Z to Ref. Point.")
                self.z_xps.moveAbsolute(self.z_axis, self.ref_z)

            elif axis == "both":
                self.log_window.append(f"Clicked button! Return XYZ to Ref. button.")
                self.x_xps.moveAbsolute(self.x_axis, self.ref[0])
                self.y_xps.moveAbsolute(self.y_axis, self.ref[1])
                self.z_xps.moveAbsolute(self.z_axis, self.ref[2])

    def raster_inp(self, inp):
        """
        Checks and validates the inputs given to raster. Also clears the number of shots line
        after editing other inputs and enables/disables the raster button depending on whether
        all inputs have been entered.
        """
        if inp == "step_length":
            if self.step_length_line.text():
                self.step_length = float(self.step_length_line.text())
                self.log_window.append(
                    f"Step Length changed  to: {self.step_length:.3f} mm"
                )
        elif inp == "sample_length":
            max_length = self.abs_max[0] - self.ref[0]
            if self.sample_length_line.text():
                if float(self.sample_length_line.text()) > max_length:
                    self.sample_length_line.setText(str(max_length))
                self.sample_length = float(self.sample_length_line.text())
                self.log_window.append(
                    f"Sample Length changed to: {self.sample_length:.3f} mm"
                )
        elif inp == "sample_width":
            max_width = self.abs_max[1] - self.ref[1]
            if self.sample_width_line.text():
                if float(self.sample_width_line.text()) > max_width:
                    self.sample_width_line.setText(str(max_width))
                self.sample_width = float(self.sample_width_line.text())
                self.log_window.append(
                    f"Sample Width changed to: {self.sample_width:.3f} mm"
                )
        elif inp == "set_bound_x":
            self.sample_length = np.abs(
                self.x_xps.getStagePosition(self.x_axis) - self.ref[0]
            )
            self.sample_length_line.setText(f"{self.sample_length:.3f}")
            self.log_window.append(
                f"Set Bound X clicked. Sample Length: {self.sample_length:.3f}"
            )

        elif inp == "set_bound_y":
            self.sample_width = np.abs(
                self.y_xps.getStagePosition(self.y_axis) - self.ref[1]
            )
            self.sample_width_line.setText(f"{self.sample_width:.3f}")
            self.log_window.append(
                f"Set Bound Y clicked. Sample Width: {self.sample_width:.3f}"
            )
        elif inp == "Rep_rate":
            if self.rep_rate_line.text():
                self.rep_rate = int(float(self.rep_rate_line.text()) * 1000)
                self.log_window.append(
                    f"Rep. Rate changed to: {self.rep_rate//1000:.1f} s"
                )
                if (
                    self.step_length_line.text()
                    and self.sample_length_line.text()
                    and self.sample_width_line.text()
                ):
                    self.raster_btn.setEnabled(True)
        # elif inp == 'num_shots':
        #     if self.num_shots_line.text():
        #         self.num_shots = int(self.num_shots_line.text())

        # Calculate the maximum number of shots if all inputs have been filled
        if (
            self.step_length_line.text()
            and self.sample_length_line.text()
            and self.sample_width_line.text()
        ):
            if self.step_length == 0:
                self.messages.setText("ERROR: Step Length cannot be 0")
                self.messages.setStyleSheet("color: red;font-size: 14pt")
                self.error_flag = True

                return
            if self.step_length > self.sample_length:
                self.messages.setText(
                    "ERROR: Step length cannot be greater than X bound"
                )
                self.messages.setStyleSheet("color: red;font-size: 12pt")
                self.error_flag = True

                return
            if self.step_length > self.sample_width:
                self.messages.setText(
                    "ERROR: Step length cannot be greater than Y bound"
                )
                self.messages.setStyleSheet("color: red;font-size: 12pt")
                self.error_flag = True

                return
            else:
                if self.error_flag:
                    self.messages.clear()
                    self.messages.setStyleSheet("color: blue")
                    self.error_flag = False
            self.max_cols = int(self.sample_length // self.step_length)
            self.max_rows = int(self.sample_width // self.step_length)
            self.max_shots = self.max_rows * self.max_cols
            self.max_shots_lbl.setText(f"Number of Steps in Raster: {self.max_shots}")
            # self.e.setValidator(QtGui.QIntValidator(1, self.max_shots, self))
            # self.num_shots_num_shots_linline.setEnabled(True)

    def start_raster(self):
        """
        Moves stage to initial position (half a step away from home) and starts timer for raster.
        If no rep rate was given, will assume 0 s.
        """
        self.ax.clear()
        self.canvas.draw()
        # self.ax.set_xticks([])
        # self.ax.set_yticks([])
        # self.ax.grid(True)
        self.current_row = 0
        self.current_col = 0
        # Set up the timer to control raster speed
        if self.rep_rate_line.text():
            rep_rate = int(float(self.rep_rate_line.text()) * 1000)
        else:
            rep_rate = 0
        # self.rast_timer = QtCore.QTimer(self, interval = rep_rate, timeout = self.perform_raster_step)
        self.log_window.append(f"Raster button Clicked!")
        self.rast_timer.setInterval(
            self.rep_rate
        )  # Set the interval to the desired rep rate
        self.rast_timer.timeout.connect(self.perform_raster_step)
        self.rast_timer.start()

    def perform_raster_step(self):
        """
        Moves the stage to the next position in the raster pattern.
        """
        if self.current_row < self.max_rows:
            # Calculate the current position
            x_pos = self.ref[0] + self.current_col * self.step_length
            y_pos = self.ref[1] + self.current_row * self.step_length

            # Move to the calculated position and take a shot
            self.move_to_position(x_pos, y_pos)
            self.take_shot()

            # Update the raster plot
            self.update_raster_plot(x_pos, y_pos)

            # Update to the next position
            self.current_col += 1
            if self.current_col >= self.max_cols:
                self.current_col = 0
                self.current_row += 1
        else:
            # Stop the timer once the raster is complete
            self.rast_timer.stop()

    def move_to_position(self, x_pos, y_pos):
        """
        Move the stage to a specific (x, y) position.

        Parameters
        ----------
        x_pos (float) : X-axis position to move to.
        y_pos (float) : Y-axis position to move to.
        """
        self.x_xps.moveAbsolute(self.x_axis, x_pos)
        self.y_xps.moveAbsolute(self.y_axis, y_pos)

    def update_raster_plot(self, x_pos, y_pos):
        """
        Update the raster plot with the new position.

        Parameters
        ----------
        x_pos (float) : X-axis position.
        y_pos (float) : Y-axis position.
        """
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.grid(True)
        self.ax.plot(x_pos, y_pos, "ro")  # 'ro' stands for red dot
        self.canvas.draw()

    def take_shot(self):
        """
        Trigger the measurement or capture process at the current stage position.
        """
        # Here, we would trigger our measurement device
        pass

    def chkvalue(self, mve):
        """
        Checks the value of the input fields for absolute movements.

        Parameters
        ----------
        mve (string) : The type of movement being checked. Either 'abs_x_length' or 'abs_y_length'.
        """
        if mve == "abs_x_length":
            if self.abs_x_line.text():
                if float(self.abs_x_line.text()) > self.abs_max[0]:
                    self.messages.setText(
                        "ERROR: Position X (abs.) is greater than the maximum value!"
                    )
                    self.messages.setStyleSheet("color: red;font-size: 11pt")
                    self.error_flag = True
                    return
                else:
                    self.messages.clear()
                    self.messages.setStyleSheet("color: blue")
                    self.error_flag = False
                    pos = float(self.abs_x_line.text())
        if mve == "abs_y_length":
            if self.abs_y_line.text():
                if float(self.abs_y_line.text()) > int(self.abs_max[1]):
                    self.messages.setText(
                        "ERROR: Position Y (abs.) is greater than the maximum value!"
                    )
                    self.messages.setStyleSheet("color: red;font-size: 11pt")
                    self.error_flag = True
                    return
                else:
                    self.messages.clear()
                    self.messages.setStyleSheet("color: blue")
                    self.error_flag = False
        if mve == "abs_z_length":
            if self.abs_z_line.text():
                if float(self.abs_z_line.text()) > int(self.abs_max[1]):
                    self.messages.setText(
                        "ERROR: Position Z (abs.) is greater than the maximum value!"
                    )
                    self.messages.setStyleSheet("color: red;font-size: 11pt")
                    self.error_flag = True
                    return
                else:
                    self.messages.clear()
                    self.messages.setStyleSheet("color: blue")
                    self.error_flag = False

    def absolute(self):
        """
        Controls absolute movements of the stage. X and y-axes can move absolutely
        independantly of eachother.
        """
        abs = [
            round(self.x_xps.getStagePosition(self.x_axis), 2),
            round(self.y_xps.getStagePosition(self.y_axis), 2),
            round(self.z_xps.getStagePosition(self.z_axis), 2),
        ]
        if self.abs_x_line.text():
            pos = float(self.abs_x_line.text())
            self.log_window.append(
                f"X moved to: {float(self.abs_x_line.text()):.2f} mm"
            )
        else:
            pos = float(abs[0])
        self.x_xps.moveAbsolute(self.x_axis, pos)
        if self.abs_y_line.text():
            pos = float(self.abs_y_line.text())
            self.log_window.append(
                f"Y moved to: {float(self.abs_y_line.text()):.2f} mm"
            )
        else:
            pos = float(abs[1])
        self.y_xps.moveAbsolute(self.y_axis, pos)
        if self.abs_z_line.text():
            pos = float(self.abs_z_line.text())
            self.log_window.append(
                f"Z moved to: {float(self.abs_z_line.text()):.2f} mm"
            )
        else:
            pos = float(abs[2])
        self.z_xps.moveAbsolute(self.z_axis, pos)

    def relative(self, btn):
        """
        Controls relative movements of the stage (relative stepping left, right, up, down).

        Parameters
        ----------
        btn (string) : Button pressed that determines the direction of step.
        """
        # check if XYZ Step Interval is evaluated or NOt?
        if btn == "left" or btn == "right":
            if not self.step_interval_x.text():
                self.messages.setText(
                    "ERROR: X Step Interval must be provided befor moving!"
                )
                self.messages.setStyleSheet("color:red;font-size:14px")
                return
            else:
                self.messages.clear()
        if btn == "up" or btn == "down":
            if not self.step_interval_y.text():
                self.messages.setText(
                    "ERROR: Y Step Interval must be provided befor moving!"
                )
                self.messages.setStyleSheet("color:red;font-size:14px")
                return
            else:
                self.messages.clear()
        if btn == "up_z" or btn == "down_z":
            if not self.step_interval_z.text():
                self.messages.setText(
                    "ERROR: Z Step Interval must be provided befor moving!"
                )
                self.messages.setStyleSheet("color:red;font-size:14px")
                return
            else:
                self.messages.clear()

        if self.step_interval_x.text():
            # Gets the step length to step relatively by
            dist = float(self.step_interval_x.text())
            current_value = (self.x_slider.value(), self.y_slider.value())
            if btn == "left":
                self.x_xps.moveRelative(self.x_axis, 0 - dist)
                new_value = max(
                    self.x_slider.minimum(),
                    current_value[0] - int(dist * self.slider_factor),
                )
                self.x_slider.setValue(new_value)
                self.log_window.append(f"X moved {-dist:.2f} mm to left.  ")
            elif btn == "right":
                self.x_xps.moveRelative(self.x_axis, dist)
                new_value = min(
                    self.x_slider.maximum(),
                    current_value[0] + int(dist * self.slider_factor),
                )
                self.x_slider.setValue(new_value)
                self.log_window.append(f"X Moved {dist:.3f} mm to Right. ")
        if self.step_interval_y.text():
            dist = float(self.step_interval_y.text())
            current_value = (self.x_slider.value(), self.y_slider.value())
            if btn == "up":
                self.y_xps.moveRelative(self.y_axis, 0 - dist)
                self.log_window.append(f"Y Moved {-dist:.3f} mm to Left.")
                new_value = max(
                    self.y_slider.minimum(),
                    current_value[1] - int(dist * self.slider_factor),
                )
                self.y_slider.setValue(new_value)
            elif btn == "down":
                self.y_xps.moveRelative(self.y_axis, dist)
                self.log_window.append(f"Y moved {dist:.3f} mm to Right.")
                new_value = min(
                    self.y_slider.maximum(),
                    current_value[1] + int(dist * self.slider_factor),
                )
                self.y_slider.setValue(new_value)
        if self.step_interval_z.text():
            dist = float(self.step_interval_z.text())
            current_value = (self.z_slider.value(), self.z_slider.value())
            if btn == "up_z":
                self.z_xps.moveRelative(self.z_axis, 0 - dist)
                self.log_window.append(f"Z Moved {-dist:.3f} mm to Down.")
                new_value = max(
                    self.z_slider.minimum(),
                    current_value[1] - int(dist * self.slider_factor),
                )
                self.z_slider.setValue(new_value)
            elif btn == "down_z":
                self.z_xps.moveRelative(self.z_axis, dist)
                self.log_window.append(f"Z moved {dist:.3f} mm to Up.")
                new_value = min(
                    self.z_slider.maximum(),
                    current_value[1] + int(dist * self.slider_factor),
                )
                self.z_slider.setValue(new_value)

    def update_group(self, axis):
        """
        Sets and gets the status of a new actuator group after changing actuators.

        Parameters
        ----------
        axis (string) : The axis of travel that the actuator will be moving along. Either "X" for
                        x-axis or "Y" for y-axis
        """
        self.xps_groups = self.x_xps.getXPSStatus()
        if axis == "X":
            self.x_axis = str(self.x_group_combo.currentText())
            self.x_xps.setGroup(self.x_axis)
            self.update_status(self.x_xps.getStageStatus(self.x_axis))

        elif axis == "Y":
            self.y_axis = str(self.y_group_combo.currentText())
            self.y_xps.setGroup(self.y_axis)
            self.update_status(self.y_xps.getStageStatus(self.y_axis))
        elif axis == "Z":
            self.z_axis = str(self.z_group_combo.currentText())
            self.z_xps.setGroup(self.z_axis)
            self.update_status(self.z_xps.getStageStatus(self.z_axis))

    def update_status(self, stage_status):
        """
        Enables and disables buttons according to the status of the two actuators.

        Parameters
        ----------
        stage_status (string) : status of the XPS actuator.
        """
        if (
            stage_status == "Not initialized state"
            or stage_status
            == "Not initialized state due to a GroupKill or KillAll command"
            or stage_status == "Not referenced state"
        ):
            for widget in self.translationStage.children():
                if not isinstance(
                    widget, (QtCore.QTimer, QtGui.QDoubleValidator, QtGui.QIntValidator)
                ):
                    widget.setEnabled(False)
            self.initialize_btn.setEnabled(True)
            self.messages.setText("Not Initialized")

        elif stage_status == "Disabled state":
            for widget in self.translationStage.children():
                if not isinstance(
                    widget, (QtCore.QTimer, QtGui.QDoubleValidator, QtGui.QIntValidator)
                ):
                    widget.setEnabled(False)
            self.enable_btn.setEnabled(True)
            self.messages.setText("Enable")

        # Initialized and enabled
        elif stage_status[:11].upper() == "Ready state".upper():
            for widget in self.translationStage.children():
                if not isinstance(
                    widget, (QtCore.QTimer, QtGui.QDoubleValidator, QtGui.QIntValidator)
                ):
                    if widget != self.rep_rate_line and widget != self.raster_btn:
                        widget.setEnabled(True)
            # self.messages.setText("Disable")

    def initialize(self):
        """
        Initializes and homes both selected actuators.
        """
        self.x_xps.initializeStage(self.x_axis)
        self.x_xps.homeStage(self.x_axis)
        self.y_xps.initializeStage(self.y_axis)
        self.y_xps.homeStage(self.y_axis)

        self.update_status(self.x_xps.getStageStatus(self.x_axis))
        self.update_status(self.y_xps.getStageStatus(self.y_axis))

    def kill(self):
        """
        Kills both selected actuators.
        """
        self.x_xps.killAll(self.x_axis)
        self.y_xps.killAll(self.y_axis)

        self.update_status(self.x_xps.getStageStatus(self.x_axis))
        self.update_status(self.y_xps.getStageStatus(self.y_axis))

    def enable_disable(self):
        """
        Enables or disables both selected actuators depending on its status.
        """
        if (
            self.x_xps.getStageStatus(self.x_axis).upper() == "Disabled state".upper()
            or self.y_xps.getStageStatus(self.y_axis).upper()
            == "Disabled state".upper()
        ):
            self.x_xps.enableGroup(self.x_axis)
            self.y_xps.enableGroup(self.y_axis)
        elif (
            self.x_xps.getStageStatus(self.x_axis)[:11].upper() == "Ready state".upper()
            or self.y_xps.getStageStatus(self.y_axis)[:11].upper()
            == "Ready state".upper()
        ):
            self.x_xps.disableGroup(self.x_axis)
            self.y_xps.disableGroup(self.y_axis)

        self.update_status(self.x_xps.getStageStatus(self.x_axis))
        self.update_status(self.y_xps.getStageStatus(self.y_axis))

    def print_location(self):
        """
        Prints the absolute and relative location of the 2 actuators. Also checks actuator
        status and enables/disables accordingly.
        """
        abs = [
            round(self.x_xps.getStagePosition(self.x_axis), 2),
            round(self.y_xps.getStagePosition(self.y_axis), 2),
            round(self.z_xps.getStagePosition(self.z_axis), 2),
        ]
        #  self.abs_lbl.setText(str(abs[0])+", "+str(abs[1]))
        #  self.rel_lbl.setText(str(abs[0]-self.ref[0])+", "+str(abs[1]-self.ref[1]))
        self.x_slider.setValue(int(abs[0] * 10))
        self.y_slider.setValue(int(abs[1] * 10))
        self.z_slider.setValue(int(abs[2] * 10))
        self.position_x.setText(f"Position X (abs.): {abs[0]:.2f} mm")
        self.position_y.setText(f"Position Y (abs.): {abs[1]:.2f} mm")
        self.position_z.setText(f"Position Z (abs.): {abs[2]:.2f} mm")
        self.position_x_ref.setText(
            f"Ref. X is: {self.ref[0]:.2f} mm"
            + ",  "
            + f"X (rel.): {(abs[0]-self.ref[0]):.2f} mm"
        )
        self.position_y_ref.setText(
            f"Ref. Y is: {self.ref[1]:.2f} mm"
            + ",  "
            + f"Y (rel.): {(abs[1]-self.ref[1]):.2f} mm"
        )
        self.position_z_ref.setText(
            f"Ref. Z is: {self.ref[2]:.2f} mm"
            + ",  "
            + f"Z (rel.): {(abs[2]-self.ref[2]):.2f} mm"
        )
        #  print(f"abs0:{abs[0]}")
        self.update_status(self.x_xps.getStageStatus(self.x_axis))

    def update_position_from_scrollbar(self, pos_scrollbar):
        """
        Update the stage position based on the scrollbar value.
        """
        if pos_scrollbar == "X_slider":
            x_value = self.x_slider.value() / self.slider_factor
            self.x_slider.setValue(int(x_value * 10))
        elif pos_scrollbar == "Y_slider":
            y_value = self.y_slider.value() / self.slider_factor
            self.y_slider.setValue(int(y_value * 10))
        elif pos_scrollbar == "Z_slider":
            z_value = self.z_slider.value() / self.slider_factor
            self.z_slider.setValue(int(z_value * 10))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
