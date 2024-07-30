import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QHBoxLayout, QComboBox,
    QLineEdit, QSpacerItem, QSizePolicy, QFormLayout, QCheckBox, QFileDialog, QInputDialog, QSlider, QDialog
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import PySpin
import cv2
import datetime
import numpy as np
import json
import os
import h5py

# Thread class to handle saving images
class SaveImagesThread(QThread):
    def __init__(self, image_data, hdf5_file, autosave_count, metadata):
        super().__init__()
        self.image_data = image_data
        self.hdf5_file = hdf5_file
        self.autosave_count = autosave_count
        self.metadata = metadata

    def run(self):
        # Append the image data and metadata to the HDF5 file
        image_key = f'image_{self.autosave_count:05d}'
        with h5py.File(self.hdf5_file, 'a') as hdf:
            if 'metadata' not in hdf:
                metadata_group = hdf.create_group('metadata')
                for key, value in self.metadata.items():
                    metadata_group.create_dataset(key, data=value)
            hdf.create_dataset(image_key, data=self.image_data, compression="gzip")

class ImageProcessingThread(QThread):
    imageProcessed = pyqtSignal(QImage)

    def __init__(self, image_data, zoom_level, show_crosshair, crosshair_x, crosshair_y):
        super().__init__()
        self.image_data = image_data
        self.zoom_level = zoom_level
        self.show_crosshair = show_crosshair
        self.crosshair_x = crosshair_x
        self.crosshair_y = crosshair_y

    def run(self):
        zoomed_image = cv2.resize(self.image_data, None, fx=self.zoom_level, fy=self.zoom_level, interpolation=cv2.INTER_LINEAR)
        zoomed_height, zoomed_width = zoomed_image.shape
        bytes_per_line = zoomed_width

        if self.show_crosshair:
            x = int(self.crosshair_x * zoomed_width)
            y = int(self.crosshair_y * zoomed_height)
            crosshair_length = 10
            cv2.line(zoomed_image, (x - crosshair_length, y), (x + crosshair_length, y), (255, 0, 0), 2)
            cv2.line(zoomed_image, (x, y - crosshair_length), (x, y + crosshair_length), (255, 0, 0), 2)

        image = QImage(zoomed_image.data, zoomed_width, zoomed_height, bytes_per_line, QImage.Format_Grayscale8)
        self.imageProcessed.emit(image)

# Dialog class for exposure and gain settings
class ExposureGainDialog(QDialog):
    def __init__(self, exposure_time, gain_value, parent=None):
        super().__init__(parent)
        self.exposure_time = exposure_time
        self.gain_value = gain_value
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Exposure and Gain Settings')

        self.exposure_input = QLineEdit(self)
        self.exposure_input.setText(str(self.exposure_time))
        self.exposure_input.setToolTip('Enter Exposure Time (ms)')

        self.gain_input = QLineEdit(self)
        self.gain_input.setText(str(self.gain_value))
        self.gain_input.setToolTip('Enter Gain Value')

        apply_button = QPushButton('Apply', self)
        apply_button.setToolTip('Apply Exposure and Gain Settings')
        apply_button.clicked.connect(self.apply_settings)

        input_layout = QFormLayout()
        input_layout.addRow("Exposure Time (ms):", self.exposure_input)
        input_layout.addRow("Gain Value:", self.gain_input)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addWidget(apply_button)

        self.setLayout(main_layout)

    def apply_settings(self):
        try:
            self.exposure_time = int(self.exposure_input.text())
            self.gain_value = float(self.gain_input.text())
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid values for exposure time and gain.")

# Main widget for the camera application
class CameraWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.crosshair_x = 0.5
        self.crosshair_y = 0.5
        self.is_paused = False
        self.show_crosshair = True
        self.exposure_time = 10
        self.zoom_level = 1.0
        self.gain_value = 8.0
        self.frame_rate = 14
        self.crosshair_file = "camera_settings.json"
        self.trigger_delay = 0.029
        self.autosave_enabled = False
        self.autosave_count = 0
        self.trigger_enabled = False
        self.save_directory = os.getcwd()  # Default save location is the current working directory
        self.file_name = None  # Default file name is None
        self.dummy_mode = False  # Flag to indicate dummy mode
        self.initUI()

        # Timer to update the image periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_image)

        if not self.init_camera():
            self.show_camera_error("No cameras detected. Running in dummy mode.")
            self.dummy_mode = True
            self.timer.start(1000 // self.frame_rate)

        self.update_frame_rate(self.exposure_time)
        if not self.dummy_mode:
            self.timer.start(1000 // self.frame_rate)

        self.load_camera_settings()

    # Sets up the UI components of the application
    def initUI(self):
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("Initializing Camera...")
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.set_crosshair

        self.crosshair_label = QLabel(self)
        self.crosshair_label.setAlignment(Qt.AlignCenter)
        self.crosshair_label.setText(f"Crosshair Position: (x: {self.crosshair_x:.2f}, y: {self.crosshair_y:.2f})")

        self.comboBox = QComboBox(self)
        self.comboBox.currentIndexChanged.connect(self.change_camera)

        save_button = QPushButton('Save Image', self)
        save_button.setToolTip('Click to save the current image displayed')
        save_button.clicked.connect(self.save_image)
        save_button.setEnabled(False)
        self.save_button = save_button

        save_settings_button = QPushButton('Save Settings', self)
        save_settings_button.setToolTip('Click to save the current settings')
        save_settings_button.clicked.connect(self.save_camera_settings)

        select_directory_button = QPushButton('Saving Location', self)
        select_directory_button.setToolTip('Click to select directory to save images')
        select_directory_button.clicked.connect(self.select_save_directory)

        set_file_name_button = QPushButton('File Name', self)
        set_file_name_button.setToolTip('Set the base file name for saving images')
        set_file_name_button.clicked.connect(self.set_file_name)
        set_file_name_button.setEnabled(False)
        self.set_file_name_button = set_file_name_button

        self.current_location_label = QLabel("No saving location set", self)

        self.pause_button = QPushButton('Stop', self)
        self.pause_button.setToolTip('Click to Start/Stop the camera')
        self.pause_button.clicked.connect(self.toggle_pause)

        self.trigger_button = QPushButton('Enable Trigger', self)
        self.trigger_button.setToolTip('Click to enable/disable trigger')
        self.trigger_button.clicked.connect(self.toggle_trigger)
        self.trigger_button.setEnabled(True)  # Initially enabled, but will be checked in toggle_trigger

        self.exposure_gain_button = QPushButton('Parameters', self)
        self.exposure_gain_button.setToolTip('Open Exposure and Gain Settings')
        self.exposure_gain_button.clicked.connect(self.open_exposure_gain_dialog)

        self.trigger_delay_input = QLineEdit(self)
        self.trigger_delay_input.setText(str(self.trigger_delay))
        self.trigger_delay_input.setToolTip('Enter Trigger Delay (ms)')
        self.trigger_delay_input.setEnabled(False)  # Initially disabled

        self.zoom_slider = QSlider(Qt.Horizontal, self)
        self.zoom_slider.setMinimum(int(self.zoom_level * 10))  # Set the minimum to the current zoom level
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(int(self.zoom_level * 10))
        self.zoom_slider.setToolTip('Zoom Level')
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        self.zoom_label = QLabel('Zoom Level:', self)

        apply_button = QPushButton('Apply', self)
        apply_button.setToolTip('Apply Exposure, Gain, and Trigger Delay Settings')
        apply_button.clicked.connect(self.apply_settings)

        self.autosave_checkbox = QCheckBox('Autosave during Triggering', self)
        self.autosave_checkbox.setChecked(self.autosave_enabled)
        self.autosave_checkbox.stateChanged.connect(self.toggle_autosave)
        self.autosave_checkbox.setEnabled(False)  # Disable autosave checkbox initially

        self.crosshair_checkbox = QCheckBox('Show Crosshair', self)
        self.crosshair_checkbox.setChecked(self.show_crosshair)
        self.crosshair_checkbox.stateChanged.connect(self.toggle_crosshair)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.comboBox)
        button_layout.addWidget(save_button)
        button_layout.addWidget(save_settings_button)
        button_layout.addWidget(select_directory_button)
        button_layout.addWidget(set_file_name_button)
        button_layout.addWidget(self.exposure_gain_button)
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.trigger_button)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(self.zoom_slider)

        input_layout = QFormLayout()

        # Create a horizontal layout for the autosave and crosshair checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox_layout.addWidget(self.autosave_checkbox)
        checkbox_layout.addWidget(self.current_location_label)
        checkbox_layout.addWidget(self.crosshair_checkbox)
        checkbox_layout.addWidget(self.crosshair_label)

        input_layout.addRow("Trigger Delay (ms):", self.trigger_delay_input)
        input_layout.addRow(checkbox_layout)
        input_layout.addRow(apply_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(zoom_layout)
        main_layout.addLayout(input_layout)

        self.setLayout(main_layout)
        self.setMinimumSize(400, 400)

    # Initializes the camera
    def init_camera(self):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()

        if (num_cameras == 0):
            return False

        self.comboBox.clear()
        for i in range(num_cameras):
            cam = self.cam_list.GetByIndex(i)
            cam.Init()
            camera_id = cam.DeviceSerialNumber.GetValue()
            self.comboBox.addItem(f"Camera {i+1} - ID: {camera_id}")
            if cam.IsStreaming():
                cam.EndAcquisition()
            cam.DeInit()

        self.cam = self.cam_list.GetByIndex(0)
        self.cam.Init()
        self.update_exposure(self.exposure_time * 1000)
        self.update_gain(self.gain_value)
        self.update_frame_rate(self.exposure_time)
        self.configure_trigger()
        self.cam.BeginAcquisition()
        return True

    # Configures the camera trigger settings
    def configure_trigger(self):
        try:
            self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
            self.cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
            self.cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)
            current_trigger_mode = self.cam.TriggerMode.GetValue()
            if current_trigger_mode == PySpin.TriggerMode_On:
                self.trigger_button.setText('Disable Trigger')
                self.trigger_delay_input.setEnabled(True)
            else:
                self.trigger_button.setText('Enable Trigger')
                self.trigger_delay_input.setEnabled(False)
            print("Trigger configured successfully.")
            self.set_trigger_delay()
        except PySpin.SpinnakerException as ex:
            print(f"Error configuring trigger: {ex}")

    # Toggles the camera trigger on or off
    def toggle_trigger(self):
        try:
            if not self.dummy_mode and self.cam.TriggerMode.GetAccessMode() != PySpin.RW:
                self.trigger_button.setText('Trigger Not Connected')
                self.trigger_button.setEnabled(False)
                self.trigger_delay_input.setEnabled(False)
                self.autosave_checkbox.setEnabled(False)
                self.autosave_enabled = False
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Trigger cannot be enabled because it is not accessible.")
                msg.setWindowTitle("Trigger Error")
                msg.exec_()
                print("Trigger not connected.")
                return

            if not self.dummy_mode and self.cam.TriggerMode.GetValue() == PySpin.TriggerMode_On:
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)
                self.trigger_button.setText('Enable Trigger')
                self.trigger_delay_input.setEnabled(False)
                self.autosave_checkbox.setEnabled(False)
                self.autosave_enabled = False
                print("Trigger turned off.")
            else:
                self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)
                self.trigger_button.setText('Disable Trigger')
                self.trigger_delay_input.setEnabled(True)
                self.autosave_checkbox.setEnabled(bool(self.save_directory) and bool(self.file_name))
                print("Trigger turned on.")
        except PySpin.SpinnakerException as ex:
            print(f"Error toggling trigger: {ex}")

    # Changes the active camera
    def change_camera(self, index):
        num_cameras = self.cam_list.GetSize()

        if num_cameras <= 1:
            self.show_camera_error("Only one camera detected. Please connect more than one camera to switch between them.")
            return

        try:
            if hasattr(self, 'cam') and self.cam is not None:
                try:
                    current_camera_index = self.cam.DeviceSerialNumber.GetValue()
                except PySpin.SpinnakerException:
                    current_camera_index = None

                new_camera = self.cam_list.GetByIndex(index)
                if not new_camera.IsInitialized():
                    new_camera.Init()

                try:
                    new_camera_index = new_camera.DeviceSerialNumber.GetValue()
                except PySpin.SpinnakerException:
                    new_camera_index = None

                if current_camera_index == new_camera_index:
                    print("Already using the selected camera.")
                    return

            self.cam = self.cam_list.GetByIndex(index)
            if not self.cam.IsInitialized():
                self.cam.Init()
            self.update_exposure(self.exposure_time * 1000)
            self.update_gain(self.gain_value)
            self.update_frame_rate(self.exposure_time)
            self.configure_trigger()

            if not self.cam.IsStreaming():
                self.cam.BeginAcquisition()

            self.timer.start(1000 // self.frame_rate)

        except PySpin.SpinnakerException as ex:
            print(f"Error changing camera: {ex}")

    # Shows an error message if no cameras are detected
    def show_camera_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Camera Error")
        msg.exec_()

    # Updates the displayed image from the camera
    def update_image(self):
        if self.is_paused:
            return

        try:
            if self.dummy_mode:
                self.image_data = self.generate_placeholder_image()
            else:
                image_result = self.cam.GetNextImage()
                if image_result.IsIncomplete():
                    print(f'Image incomplete with image status {image_result.GetImageStatus()}')
                    return
                else:
                    self.image_data = image_result.GetNDArray()
                    image_result.Release()

            height, width = self.image_data.shape
            zoomed_image = cv2.resize(self.image_data, None, fx=self.zoom_level, fy=self.zoom_level, interpolation=cv2.INTER_LINEAR)
            zoomed_height, zoomed_width = zoomed_image.shape

            # Crop the zoomed image to fit the original image size
            start_x = max(0, (zoomed_width - width) // 2)
            start_y = max(0, (zoomed_height - height) // 2)
            end_x = start_x + width
            end_y = start_y + height
            cropped_image = zoomed_image[start_y:end_y, start_x:end_x]

            # Ensure cropped image size matches the original size
            cropped_image = cv2.resize(cropped_image, (width, height), interpolation=cv2.INTER_LINEAR)

            bytes_per_line = width
            image = QImage(cropped_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)

            pixmap = QPixmap.fromImage(image)
            painter = QPainter(pixmap)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

            if self.show_crosshair:
                crosshair_length = 10
                x = int(self.crosshair_x * width)
                y = int(self.crosshair_y * height)
                painter.drawLine(x - crosshair_length, y, x + crosshair_length, y)
                painter.drawLine(x, y - crosshair_length, x, y + crosshair_length)
            painter.end()

            self.image_label.setPixmap(pixmap)
            self.crosshair_label.setText(f"Crosshair Position: (x: {self.crosshair_x:.2f}, y: {self.crosshair_y:.2f})")

            if self.autosave_enabled:
                self.save_image(autosave=True)

        except PySpin.SpinnakerException as ex:
            print('Error: %s' % ex)

    def display_image(self, image):
        pixmap = QPixmap.fromImage(image)
        self.image_label.setPixmap(pixmap)

    # Generates a placeholder image for dummy mode
    def generate_placeholder_image(self):
        placeholder_image = np.full((480, 640), 128, dtype=np.uint8)  # Gray image
        cv2.putText(placeholder_image, 'No Camera Connected', (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        return placeholder_image

    # Updates the zoom level
    def update_zoom(self, value):
        self.zoom_level = value / 10.0
        self.update_image()

    # Saves the current image
    def save_image(self, autosave=False):
        if not self.save_directory or not self.file_name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a save location and set a file name before saving.")
            msg.setWindowTitle("Save Error")
            msg.exec_()
            return

        # Gather metadata
        metadata = {
            "exposure_time": self.exposure_time,
            "gain_value": self.gain_value,
            "trigger_delay": self.trigger_delay
        }

        if autosave:
            # Save the image in autosave mode as HDF5 using QThread
            self.autosave_thread = SaveImagesThread(self.image_data, self.hdf5_file, self.autosave_count, metadata)
            self.autosave_thread.start()
            self.autosave_count += 1
        else:
            # Save the image normally as TIFF
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_directory, f'{self.file_name}_{timestamp}.tiff')
            cv2.imwrite(filename, self.image_data)
            print(f'Saved {filename}')
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Image saved as {filename}")
            msg.setWindowTitle("Image Saved")
            msg.exec_()

    # Sets the base file name for saving images
    def select_save_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.save_directory = directory
            self.current_location_label.setText(f"Save location: {self.save_directory}")
            self.set_file_name_button.setEnabled(True)
            self.check_save_enable()

    def set_file_name(self):
        file_name, ok = QInputDialog.getText(self, "Set File Name", "Enter the base file name:")
        if ok and file_name:
            self.file_name = file_name
            self.current_location_label.setText(f"Save location: {self.save_directory}, File name: {self.file_name}")
            self.check_save_enable()

    # Checks if both save location and file name are set to enable the save button
    def check_save_enable(self):
        if self.save_directory and self.file_name:
            self.save_button.setEnabled(True)
            if self.trigger_button.text() == 'Disable Trigger':
                self.autosave_checkbox.setEnabled(True)
        else:
            self.save_button.setEnabled(False)
            self.autosave_checkbox.setEnabled(False)

    # Saves the current settings (crosshair position, gain, trigger)
    def save_camera_settings(self):
        settings = {
            "crosshair_x": self.crosshair_x,
            "crosshair_y": self.crosshair_y,
            "gain_value": self.gain_value,
            "trigger_delay": self.trigger_delay,
            "trigger_enabled": not self.dummy_mode and self.cam.TriggerMode.GetValue() == PySpin.TriggerMode_On
        }
        with open(self.crosshair_file, 'w') as file:
            json.dump(settings, file)
        print(f'Settings saved to {self.crosshair_file}')
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Camera settings saved as {self.crosshair_file}")
        msg.setWindowTitle("Settings Saved")
        msg.exec_()

    # Sets the crosshair position based on a mouse click
    def set_crosshair(self, event):
        label_width = self.image_label.width()
        label_height = self.image_label.height()
        pixmap = self.image_label.pixmap()
        if pixmap is None:
            return

        image_width = pixmap.width()
        image_height = pixmap.height()

        scale_factor_x = image_width / label_width
        scale_factor_y = image_height / label_height

        scaled_width = label_width * scale_factor_x
        scaled_height = label_height * scale_factor_y

        margin_x = (label_width - scaled_width) / 2
        margin_y = (label_height - scaled_height) / 2

        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        if mouse_x < margin_x or mouse_x > margin_x + scaled_width or mouse_y < margin_y or mouse_y > scaled_height + margin_y:
            print("Click is outside the image bounds")
            return

        relative_x = (mouse_x - margin_x) / scaled_width
        relative_y = (mouse_y - margin_y) / scaled_height

        relative_x = np.clip(relative_x, 0, 1)
        relative_y = np.clip(relative_y, 0, 1)

        self.crosshair_x = relative_x
        self.crosshair_y = relative_y

        self.update_image()


    # Updates the camera exposure time
    def update_exposure(self, value):
        try:
            if not self.dummy_mode:
                self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
                self.cam.ExposureTime.SetValue(value)
        except PySpin.SpinnakerException as ex:
            print(f"Error setting exposure: {ex}")

    # Updates the camera gain
    def update_gain(self, value):
        try:
            if not self.dummy_mode:
                self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
                self.cam.Gain.SetValue(value)
        except PySpin.SpinnakerException as ex:
            print(f"Error setting gain: {ex}")

    # Updates the frame rate based on the exposure time
    def update_frame_rate(self, exposure_ms):
        try:
            if not self.dummy_mode:
                self.cam.AcquisitionFrameRateEnable.SetValue(True)
                max_frame_rate = self.cam.AcquisitionFrameRate.GetMax()
                self.frame_rate = int(min(1000 / exposure_ms, max_frame_rate))
                self.timer.setInterval(int(1000 // self.frame_rate))
                self.cam.AcquisitionFrameRate.SetValue(self.frame_rate)
        except PySpin.SpinnakerException as ex:
            print(f"Error setting frame rate: {ex}")

    # Opens the dialog for exposure and gain settings
    def open_exposure_gain_dialog(self):
        dialog = ExposureGainDialog(self.exposure_time, self.gain_value, self)
        if dialog.exec_():
            self.exposure_time = dialog.exposure_time
            self.gain_value = dialog.gain_value
            self.update_exposure(self.exposure_time * 1000)
            self.update_gain(self.gain_value)
            self.update_frame_rate(self.exposure_time)

    # Sets the camera trigger delay based on user input
    def set_trigger_delay(self):
        try:
            delay = float(self.trigger_delay_input.text())
            if not self.dummy_mode:
                min_delay = self.cam.TriggerDelay.GetMin() / 1000
                max_delay = self.cam.TriggerDelay.GetMax() / 1000

                if delay < min_delay:
                    delay = min_delay
                elif delay > max_delay:
                    delay = max_delay

                self.cam.TriggerDelay.SetValue(delay * 1000)
            print(f"Trigger delay set to {delay} ms")
        except PySpin.SpinnakerException as ex:
            print(f"Error setting trigger delay: {ex}")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for trigger delay.")

    # Applies the exposure time, gain, and trigger delay settings
    def apply_settings(self):
        self.set_trigger_delay()

    # Toggles the visibility of the crosshair
    def toggle_crosshair(self, state):
        self.show_crosshair = bool(state)
        self.update_image()

    # Pauses or resumes the camera feed
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.pause_button.setText('Start' if self.is_paused else 'Stop')

    # Toggles the autosave feature
    def toggle_autosave(self, state):
        if not self.dummy_mode and self.cam.TriggerMode.GetValue() != PySpin.TriggerMode_On:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Autosave cannot be enabled unless the trigger is enabled.")
            msg.setWindowTitle("Autosave Error")
            msg.exec_()
            self.autosave_checkbox.blockSignals(True)
            self.autosave_checkbox.setChecked(False)
            self.autosave_checkbox.blockSignals(False)
            return

        if not self.save_directory or not self.file_name:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a save location and set a file name before enabling autosave.")
            msg.setWindowTitle("Autosave Error")
            msg.exec_()
            self.autosave_checkbox.blockSignals(True)
            self.autosave_checkbox.setChecked(False)
            self.autosave_checkbox.blockSignals(False)
            return

        self.autosave_enabled = bool(state)
        if self.autosave_enabled:
            # Gather metadata
            metadata = {
                "exposure_time": self.exposure_time,
                "gain_value": self.gain_value,
                "trigger_delay": self.trigger_delay
            }

            # Open the HDF5 file with a timestamp and write metadata
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.hdf5_file = os.path.join(self.save_directory, f'{self.file_name}_{timestamp}.h5')
            with h5py.File(self.hdf5_file, 'w') as hdf:
                metadata_group = hdf.create_group('metadata')
                for key, value in metadata.items():
                    metadata_group.create_dataset(key, data=value)

            print(f"Autosave enabled. Saving to {self.hdf5_file}")
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Autosave turned off. {self.autosave_count} images saved.")
            msg.setWindowTitle("Autosave")
            msg.exec_()
            self.autosave_count = 0
            self.hdf5_file = None  # Close the HDF5 file

    # Loads the camera settings (crosshair, gain, trigger) from a file
    def load_camera_settings(self):
        if os.path.exists(self.crosshair_file):
            with open(self.crosshair_file, 'r') as file:
                settings = json.load(file)
                self.crosshair_x = settings.get("crosshair_x", 0.5)
                self.crosshair_y = settings.get("crosshair_y", 0.5)
                self.gain_value = settings.get("gain_value", 1.0)
                self.trigger_delay = settings.get("trigger_delay", 0.029)
                self.trigger_enabled = settings.get("trigger_enabled", False)

                if not self.dummy_mode:  # Add this line
                    self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)  # Modify this line to be within the condition
                if self.trigger_enabled:
                    if not self.dummy_mode:  # Add this line
                        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_On)  # Modify this line to be within the condition
                    self.trigger_button.setText('Disable Trigger')
                    self.trigger_delay_input.setEnabled(True)
                else:
                    if not self.dummy_mode:  # Add this line
                        self.cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)  # Modify this line to be within the condition
                    self.trigger_button.setText('Enable Trigger')
                    self.trigger_delay_input.setEnabled(False)
                self.update_gain(self.gain_value)
                self.set_trigger_delay()
            print("Camera settings loaded.")

    # Handles the close event to clean up resources
    def closeEvent(self, event):
        if not self.dummy_mode:
            self.cam.EndAcquisition()
            self.cam.DeInit()
            self.cam_list.Clear()
            self.system.ReleaseInstance()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraWidget()
    ex.show()
    sys.exit(app.exec_())
