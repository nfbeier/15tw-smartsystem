import sys
from PyQt5.QtWidgets import QApplication, QCheckBox, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit
from PyQt5.QtCore import QSize, QTimer
import PySpin
import os
import datetime
import h5py
import numpy as np
from devices.FLIR.camera_widget import CameraWidget
from devices.CCS200.spectrometer_widget import SpectrometerWidget, ThorlabsSpecThread
from devices.XGS600.XGS600_Widget import XGSWidget

# Preventing multiple OpenMP runtime issues
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

class MainProgram(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)

        camera_layout = QGridLayout()
        control_layout = QVBoxLayout()

        # Initialize PySpin system and get available cameras
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()

        # Create and add CameraWidget instances based on available cameras
        self.camera_widgets = []
        for i in range(num_cameras):
            camera_widget = CameraWidget(parent=self)
            self.camera_widgets.append(camera_widget)
            row = i // 2
            col = i % 2
            camera_layout.addWidget(camera_widget, row, col)
            camera_layout.setRowStretch(row, 1)
            camera_layout.setColumnStretch(col, 1)

        # Add camera layout to main layout
        main_layout.addLayout(camera_layout)

        # Spectrometer and Vacuum controls
        spectrometer_control_layout = QVBoxLayout()

        # Spectrometer controls
        exposure_layout = QHBoxLayout()
        exposure_label = QLabel("Exposure Time (ms):")
        self.in_specexposure = QLineEdit()
        exposure_layout.addWidget(exposure_label)
        exposure_layout.addWidget(self.in_specexposure)
        spectrometer_control_layout.addLayout(exposure_layout)

        self.init_button = QPushButton("Initialize Spectrometer")
        self.init_button.clicked.connect(self.init_spectrometer)
        spectrometer_control_layout.addWidget(self.init_button)

        self.start_button = QPushButton("Start Acquisition")
        self.start_button.clicked.connect(self.start_acquisition)
        spectrometer_control_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Acquisition")
        self.stop_button.clicked.connect(self.stop_acquisition)
        spectrometer_control_layout.addWidget(self.stop_button)

        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_spectrometer_data)
        spectrometer_control_layout.addWidget(self.save_button)

        # Spectrometer plot
        self.spectrometer_widget = SpectrometerWidget()
        self.spectrometer_widget.setMinimumSize(QSize(400, 300))  # Set minimum size for the spectrometer plot
        spectrometer_control_layout.addWidget(self.spectrometer_widget.alignmentPlot)

        # Add spectrometer control layout to main layout
        control_layout.addLayout(spectrometer_control_layout)

        # Add vacuum control widget to the control layout
        self.vacuum_widget = XGSWidget()
        control_layout.addWidget(self.vacuum_widget)

        # Directory and file name selection
        directory_layout = QHBoxLayout()
        self.save_directory = None
        self.select_directory_button = QPushButton('Select Save Directory', self)
        self.select_directory_button.clicked.connect(self.select_save_directory)
        directory_layout.addWidget(self.select_directory_button)

        self.file_name_input = QLineEdit()
        self.file_name_input.setPlaceholderText("Enter file name")
        directory_layout.addWidget(self.file_name_input)
        control_layout.addLayout(directory_layout)

        # Capture button to save images from all cameras
        self.capture_button = QPushButton('Capture Images from All Cameras')
        self.capture_button.clicked.connect(self.capture_images_from_all_cameras)
        control_layout.addWidget(self.capture_button)

        # Enable/Disable Trigger Button
        self.trigger_button = QPushButton('Enable Trigger for All Cameras', self)
        self.trigger_button.clicked.connect(self.toggle_trigger_for_all_cameras)
        control_layout.addWidget(self.trigger_button)

        # Autosave Checkbox
        self.autosave_checkbox = QCheckBox('Keep Saving While Trigger is Enabled', self)
        self.autosave_checkbox.setChecked(False)
        control_layout.addWidget(self.autosave_checkbox)

        # Add control layout to main layout
        main_layout.addLayout(control_layout)
        main_layout.setStretch(0, 2)  # Camera layout stretch factor
        main_layout.setStretch(1, 1)  # Control layout stretch factor

        self.setLayout(main_layout)
        self.setWindowTitle('Multi-Camera and Spectrometer Application')
        self.setGeometry(100, 100, 1600, 1200)  # Adjust window size as needed

    def select_save_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.save_directory = directory

    def capture_images_from_all_cameras(self):
        if not self.save_directory:
            print("Save directory not set")
            return

        file_name = self.file_name_input.text()
        if not file_name:
            print("File name not set")
            return

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        hdf5_filename = os.path.join(self.save_directory, f'{file_name}_{timestamp}.h5')

        with h5py.File(hdf5_filename, 'w') as hdf5_file:
            hdf5_file.attrs['timestamp'] = timestamp

            for camera_index in range(self.cam_list.GetSize()):
                cam = self.cam_list[camera_index]
                cam.Init()

                try:
                    if cam.IsStreaming():
                        cam.EndAcquisition()
                    cam.BeginAcquisition()

                    image_result = cam.GetNextImage()
                    if image_result.IsIncomplete():
                        print("Image incomplete with image status %d ..." % image_result.GetImageStatus())
                    else:
                        image_data = image_result.GetNDArray()
                        image_dataset_name = f'camera{camera_index + 1}_image'
                        metadata_dataset_name = f'camera{camera_index + 1}_metadata'

                        # Save image data
                        image_dataset = hdf5_file.create_dataset(image_dataset_name, data=image_data)

                        # Retrieve metadata from the camera
                        metadata = {
                            'timestamp': "Time: " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'width': "Width: " + str(image_result.GetWidth()),
                            'height': "Height: " + str(image_result.GetHeight()),
                            'pixel_format': "Pixel: " + image_result.GetPixelFormatName(),
                            'camera_serial': "Camera ID: " + cam.GetUniqueID(),
                            'exposure_time': "Exposure Time: " + str(cam.ExposureTime.GetValue()),
                            'gain_value': "Gain Value: " + str(cam.Gain.GetValue()),
                            'trigger_delay': "Trigger Delay: " + str(cam.TriggerDelay.GetValue())
                        }

                        # Save metadata
                        metadata_dtype = h5py.special_dtype(vlen=str)  # Using variable length string type
                        metadata_array = np.array(list(metadata.values()), dtype=metadata_dtype)

                        # Create a dataset for metadata with correct dimensions
                        metadata_dataset = hdf5_file.create_dataset(metadata_dataset_name, data=metadata_array)

                        print(f"Image and metadata from camera {camera_index + 1} saved in HDF5 file")

                    image_result.Release()
                except PySpin.SpinnakerException as ex:
                    print(f"Error: {ex}")
                finally:
                    cam.EndAcquisition()
                    cam.DeInit()

            self.save_spectrometer_data(hdf5_file)

        print(f"All images and metadata saved in HDF5 file {hdf5_filename}")

        # If autosave is enabled, continue saving images
        if self.autosave_checkbox.isChecked():
            QTimer.singleShot(100, self.capture_images_from_all_cameras)

    def toggle_trigger_for_all_cameras(self):
        # Check the current state of the first camera's trigger
        trigger_state = self.camera_widgets[0].cam.TriggerMode.GetValue() == PySpin.TriggerMode_On
        
        # Enable or disable trigger for all cameras based on the current state
        for camera_widget in self.camera_widgets:
            if trigger_state:
                camera_widget.disable_trigger()
            else:
                camera_widget.enable_trigger()

        # Update the trigger button text based on the new state
        if self.camera_widgets[0].cam.TriggerMode.GetValue() == PySpin.TriggerMode_On:
            self.trigger_button.setText('Disable Trigger for All Cameras')
            if self.autosave_checkbox.isChecked():
                self.capture_images_from_all_cameras()  # Start capturing images if autosave is checked
        else:
            self.trigger_button.setText('Enable Trigger for All Cameras')

    def init_spectrometer(self):
        if self.spectrometer_widget.ThorlabsThread:
            print("Thorlabs Spectrometer has already been initialized")
        else:
            exposure_time = self.in_specexposure.text()
            if not exposure_time.isdigit():
                print("Invalid exposure time entered.")
                return

            self.spectrometer_widget.ThorlabsThread = ThorlabsSpecThread(exposure_time)
            if not self.spectrometer_widget.ThorlabsThread.spec:
                print("Failed to initialize Thorlabs Spectrometer.")
                return
            self.wave = self.spectrometer_widget.ThorlabsThread.getWavelength()
            self.intensity = self.spectrometer_widget.ThorlabsThread.getIntensity()
            self.spectrometer_widget.alignmentPlot.figure.clf()
            self.ax = self.spectrometer_widget.alignmentPlot.figure.add_subplot(111)
            self.alignPlot, = self.ax.plot(self.wave, self.intensity)
            self.ax.set_xlabel("Wavelength [nm]")
            self.ax.set_ylabel("Intensity [a.u.]")
            self.ax.set_ylim([0, 1])

            self.spectrometer_widget.ThorlabsThread.acquired.connect(self.updateIntensity)

    def start_acquisition(self):
        if self.spectrometer_widget.ThorlabsThread:
            self.spectrometer_widget.ThorlabsThread.start()

    def stop_acquisition(self):
        if self.spectrometer_widget.ThorlabsThread:
            self.spectrometer_widget.ThorlabsThread.stop()

    def updateIntensity(self, intensity):
        self.intensity = intensity
        self.alignPlot.set_ydata(self.intensity)
        self.spectrometer_widget.alignmentPlot.draw()

    def save_spectrometer_data(self, hdf5_file=None):
        if not self.save_directory:
            print("Save directory not set")
            return

        file_name = self.file_name_input.text()
        if not file_name:
            print("File name not set")
            return

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        hdf5_filename = os.path.join(self.save_directory, f'{file_name}_{timestamp}.h5')

        if not hasattr(self, 'wave') or not hasattr(self, 'intensity'):
            print("Spectrometer data not available")
            return

        if hdf5_file is None:
            hdf5_file = h5py.File(hdf5_filename, 'a')
            hdf5_file.attrs['timestamp'] = timestamp

        # Save spectrometer data
        hdf5_file.create_dataset('wavelength', data=self.wave)
        hdf5_file.create_dataset('intensity', data=self.intensity)

        print(f"Spectrometer data saved in HDF5 file {hdf5_filename}")

        if hdf5_file is not None:
            hdf5_file.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainProgram()
    ex.show()
    sys.exit(app.exec_())
