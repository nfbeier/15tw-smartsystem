import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QHBoxLayout, QComboBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import PySpin
import cv2
import datetime
import numpy as np

class CameraApp(QMainWindow):
    """ Initialises the UI and Camera and throws errors if camera is not detected, 
    also uses a timer to update the image every 30ms"""
    def __init__(self):
        super().__init__()
        self.initUI()  
        if not self.init_camera(): 
            self.show_camera_error() 
            sys.exit(0)  

        self.timer = QTimer(self)  
        self.timer.timeout.connect(self.update_image) 
        self.timer.start(30)  
    
    """ Details of the UI"""
    def initUI(self):
        self.setWindowTitle('Blackfly Camera Viewer and Image Saver') 
        self.setGeometry(100, 100, 800, 600) 

        self.image_label = QLabel(self) 
        self.image_label.setAlignment(Qt.AlignCenter)  
        self.image_label.setText("Initializing Camera...")  

        self.comboBox = QComboBox(self)  
        self.comboBox.addItem("BFS-U3_13Y3") 
        self.comboBox.addItem("BFS-U3-04S2")
        self.comboBox.currentIndexChanged.connect(self.change_camera)  

        save_button = QPushButton('Save Current Image', self)  
        save_button.setToolTip('Click to save the current image displayed')  
        save_button.clicked.connect(self.save_image)  

        button_layout = QHBoxLayout()  
        button_layout.addWidget(self.comboBox)  
        button_layout.addWidget(save_button) 

        main_layout = QVBoxLayout()  
        main_layout.addWidget(self.image_label) 
        main_layout.addLayout(button_layout)  

        container = QWidget()  
        container.setLayout(main_layout) 
        self.setCentralWidget(container)  

    
    """ Initiates the camera and lists them and checks if cameras are available"""
    def init_camera(self):
        self.system = PySpin.System.GetInstance()  
        self.cam_list = self.system.GetCameras()  
        if self.cam_list.GetSize() == 0: 
            return False  

        self.cam = self.cam_list.GetByIndex(0)  
        self.cam.Init() 
        self.cam.BeginAcquisition() 
        return True  
    
    """ Changes the camera and restarts the timer"""
    def change_camera(self, index):
        self.timer.stop() 
        self.cam.EndAcquisition() 
        self.cam.DeInit() 

        self.cam = self.cam_list.GetByIndex(index) 
        self.cam.Init()  
        self.cam.BeginAcquisition()  
        self.timer.start(30) 

    """Dialog Box for the Error"""
    def show_camera_error(self):
        msg = QMessageBox()  
        msg.setIcon(QMessageBox.Critical)  
        msg.setText("No cameras detected") 
        msg.setInformativeText("Please connect a camera and try again.") 
        msg.setWindowTitle("Camera Error") 
        msg.exec_() 

    """To update and get details of the image"""
    def update_image(self):
        try:
            image_result = self.cam.GetNextImage() 
            if image_result.IsIncomplete():  
                print(f'Image incomplete with image status {image_result.GetImageStatus()}') 
            else:
                self.image_data = image_result.GetNDArray()  
                height, width = self.image_data.shape  
                bytes_per_line = width  
                image = QImage(self.image_data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)  
                self.image_label.setPixmap(QPixmap.fromImage(image))  
            image_result.Release()  
        except PySpin.SpinnakerException as ex: 
            print('Error: %s' % ex)  

    """generates a timestamp and saves the image"""
    def save_image(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  
        filename = f'Snapshot_{timestamp}.png'  
        cv2.imwrite(filename, self.image_data)  
        print(f'Saved {filename}')  
        msg = QMessageBox() 
        msg.setIcon(QMessageBox.Information)  
        msg.setText(f"Image saved as {filename}") 
        msg.setWindowTitle("Image Saved")  
        msg.exec_() 

    """Closes and Deinitializes the cameras"""
    def closeEvent(self, event):
        self.cam.EndAcquisition()  
        self.cam.DeInit()  
        self.cam_list.Clear() 
        self.system.ReleaseInstance() 
        super().closeEvent(event)  

if __name__ == '__main__':
    app = QApplication(sys.argv)  
    ex = CameraApp()  # Create an instance of the CameraApp
    ex.show()  # Show the main window
    sys.exit(app.exec_())  # Start the application event loop
