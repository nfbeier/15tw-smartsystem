import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout
from camera_widget import CameraWidget
import PySpin

class MainProgram(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QGridLayout(self)

        # Initialize PySpin system and get available cameras
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        num_cameras = self.cam_list.GetSize()

        # Create and add CameraWidget instances based on available cameras
        if num_cameras > 0:
            camera1 = CameraWidget(self)
            layout.addWidget(camera1, 0, 0)
            layout.setRowStretch(0, 1)
            layout.setColumnStretch(0, 1)

        if num_cameras > 1:
            camera2 = CameraWidget(self)
            layout.addWidget(camera2, 0, 1)
            layout.setRowStretch(0, 1)
            layout.setColumnStretch(1, 1)

        if num_cameras > 2:
            camera3 = CameraWidget(self)
            layout.addWidget(camera3, 1, 0)
            layout.setRowStretch(1, 1)
            layout.setColumnStretch(0, 1)

        if num_cameras > 3:
            camera4 = CameraWidget(self)
            layout.addWidget(camera4, 1, 1)
            layout.setRowStretch(1, 1)
            layout.setColumnStretch(1, 1)

        self.setLayout(layout)
        self.setWindowTitle('Multi-Camera Application')
        self.setGeometry(100, 100, 1600, 1200)  # Adjust window size as needed

        # Release cameras and system when done
        self.cam_list.Clear()
        self.system.ReleaseInstance()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainProgram()
    ex.show()
    sys.exit(app.exec_())
