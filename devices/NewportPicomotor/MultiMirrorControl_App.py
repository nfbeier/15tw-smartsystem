from pylablib.devices import Newport
import sys
from PyQt5 import QtWidgets
from MirrorControlWidget import MirrorControlWidget

# Create the main application to use the widget (Multi-mirror control GUI)

class MultiMirrorControl_App(QtWidgets.QWidget):
    def __init__(self):
        super(MultiMirrorControl_App, self).__init__()

        try:
            self.stage1 = Newport.Picomotor8742(conn=0,multiaddr=True)
            print("Stage 1 initialized successfully.")
        except Newport.base.NewportBackendError as e:
            print(f"Stage 1 could not be initialized: {e}")
            self.stage1 = None

        try:
            self.stage2 = Newport.Picomotor8742(conn=1,multiaddr=True)
            print("Stage 2 initialized successfully.")
        except Newport.base.NewportBackendError as e:
            print(f"Stage 2 could not be initialized: {e}")
            self.stage2 = None

        print(f"Number of connected devices: {Newport.get_usb_devices_number_picomotor()}")

        # Create widgets for each mirror mount
        self.mirror1 = MirrorControlWidget(self.stage1, 1, 2, "Mirror 1")
        self.mirror2 = MirrorControlWidget(self.stage1, 3, 4, "Mirror 2")
        self.mirror3 = MirrorControlWidget(self.stage2, 1, 2, "Mirror 3")
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.mirror1)
        layout.addWidget(self.mirror2)
        layout.addWidget(self.mirror3)

        self.setLayout(layout)

        # Set fixed size for the main window
        self.setFixedSize(1000, 400)

    def closeEvent(self, event):
        if self.stage1:
            self.stage1.close()
        if self.stage2:
            self.stage2.close()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainApp = MultiMirrorControl_App()
    mainApp.show()
    sys.exit(app.exec_())
