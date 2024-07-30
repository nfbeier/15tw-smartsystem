import sys
import time
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit, QLabel, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyvisa import ResourceManager
from instrumental.drivers.spectrometers.thorlabs_ccs import CCS, list_instruments
from instrumental import Q_
import datetime

class ThorlabsSpecThread(QThread):
    acquired = pyqtSignal(object)

    def __init__(self, exposureTime):
        super(ThorlabsSpecThread, self).__init__()
        self.spec = None
        self.rm = ResourceManager()
        self.res = self.rm.list_resources()
        print("Resource Manager found resources:", self.res)

        try:
            if self.res:
                paramsets = list_instruments()
                print("Paramsets found:", paramsets)
                if paramsets:
                    self.spec = CCS(paramsets[0])
                else:
                    print("No matching instruments found.")
            else:
                print("No instruments found.")
            
            if self.spec:
                self.running = False
                self.wave = self.spec._wavelength_array
                self.set_exposure_time(exposureTime)

                self.spec.start_single_scan()
                self.intensity = self.spec.get_scan_data()
            else:
                print("Failed to initialize spectrometer.")
        except Exception as e:
            print(f"Failed to initialize spectrometer: {e}")

    def set_exposure_time(self, exposureTime):
        if self.spec:
            self.spec.set_integration_time(Q_(float(exposureTime), 'ms'))
            print(f"Exposure time set to {exposureTime} ms")

    def __del__(self):
        self.wait()

    def run(self):
        if self.spec is None:
            print("Spectrometer not initialized.")
            return
        self.running = True
        self.is_paused = False
        while self.running:
            if self.spec:
                self.spec.start_single_scan()
                self.intensity = np.array(self.spec.get_scan_data())
                self.acquired.emit(self.intensity)
                time.sleep(0.001)
            while self.is_paused:
                time.sleep(0.01)

    def stop(self):
        self.running = False

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def getWavelength(self):
        return self.wave

    def getIntensity(self):
        return self.intensity

    def updateThorlabsParameters(self, val, param=None):
        '''Note this function is causing crashing at the moment. Haven't had time to debug it.'''
        self.pause()
        if param == "integrationTime":
            self.set_exposure_time(val)
        self.resume()


class SpectrometerWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Thorlabs Spectrometer GUI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Input for exposure time
        self.exposure_layout = QHBoxLayout()
        self.exposure_label = QLabel("Exposure Time (ms):")
        self.in_specexposure = QLineEdit()
        self.in_specexposure.editingFinished.connect(self.update_exposure_time)  # Connect the editingFinished signal to update the exposure time
        self.exposure_layout.addWidget(self.exposure_label)
        self.exposure_layout.addWidget(self.in_specexposure)
        self.layout.addLayout(self.exposure_layout)

        # Button to initialize spectrometer
        self.init_button = QPushButton("Initialize Spectrometer")
        self.init_button.clicked.connect(self.init_spectrometer)
        self.layout.addWidget(self.init_button)

        # Buttons to start/stop acquisition
        self.start_button = QPushButton("Start Acquisition")
        self.start_button.clicked.connect(self.start_acquisition)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Acquisition")
        self.stop_button.clicked.connect(self.stop_acquisition)
        self.layout.addWidget(self.stop_button)

        # Button to save data
        self.save_button = QPushButton("Save Data")
        self.save_button.clicked.connect(self.save_data)
        self.layout.addWidget(self.save_button)

        # Placeholder for matplotlib plot
        self.figure = Figure()
        self.alignmentPlot = FigureCanvas(self.figure)
        self.layout.addWidget(self.alignmentPlot)

        # Internal attributes
        self.ThorlabsThread = None
        self.wave = None
        self.intensity = None

    def init_spectrometer(self):
        if self.ThorlabsThread:
            print("Thorlabs Spectrometer has already been initialized")
        else:
            exposure_time = self.in_specexposure.text()
            if not exposure_time.isdigit():
                print("Invalid exposure time entered.")
                return

            self.ThorlabsThread = ThorlabsSpecThread(exposure_time)
            if not self.ThorlabsThread.spec:
                print("Failed to initialize Thorlabs Spectrometer.")
                return
            self.wave = self.ThorlabsThread.getWavelength()
            self.intensity = self.ThorlabsThread.getIntensity()
            self.alignmentPlot.figure.clf()
            self.ax = self.alignmentPlot.figure.add_subplot(111)
            self.alignPlot, = self.ax.plot(self.wave, self.intensity)
            self.ax.set_xlabel("Wavelength [nm]")
            self.ax.set_ylabel("Intensity [a.u.]")
            self.ax.set_ylim([0, 1])

            self.ThorlabsThread.acquired.connect(self.updateIntensity)

    def update_exposure_time(self):
        if self.ThorlabsThread:
            exposure_time = self.in_specexposure.text()
            if not exposure_time.isdigit():
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid exposure time.")
                return

            self.ThorlabsThread.updateThorlabsParameters(exposure_time, "integrationTime")

    def start_acquisition(self):
        if self.ThorlabsThread:
            self.ThorlabsThread.start()

    def stop_acquisition(self):
        if self.ThorlabsThread:
            self.ThorlabsThread.stop()

    def updateIntensity(self, intensity):
        self.intensity = intensity
        self.alignPlot.set_ydata(self.intensity)
        self.alignmentPlot.draw()

    def save_data(self):
        if self.wave is not None and self.intensity is not None:
            options = QFileDialog.Options()
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Data", f"spectrum_{timestamp}.csv", "CSV Files (*.csv);;All Files (*)", options=options)
            if file_path:
                df = pd.DataFrame({'Wavelength': self.wave, 'Intensity': self.intensity})
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Save Data", f"Data saved to {file_path}")
        else:
            QMessageBox.warning(self, "Save Data", "No data to save")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpectrometerWidget()
    window.show()
    sys.exit(app.exec_())
