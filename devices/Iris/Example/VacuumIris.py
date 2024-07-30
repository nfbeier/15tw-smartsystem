from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout
import sys, os
cwd = os.getcwd()
if '15tw-smartsystem' not in cwd.split(os.path.sep):
    raise ValueError("The directory does not contain '15tw-smartsystem' folder.")

# Rebuild the directory string up to and including '15tw-smartsystem', prevent import errors
cwd = os.path.sep.join(cwd.split(os.path.sep)[:cwd.split(os.path.sep).index('15tw-smartsystem') + 1])

sys.path.insert(0,cwd)

from devices.Iris.irisgui import IrisGUIWidget


app = QApplication(sys.argv)

main_window = QWidget()
main_window.resize(800, 600)  # Set the default window size

layout = QVBoxLayout(main_window)
grid_layout = QGridLayout()
for i in range(2):
    for j in range(1):
        iris_gui = IrisGUIWidget()
        grid_layout.addWidget(iris_gui, i, j)

layout.addLayout(grid_layout)

main_window.setLayout(layout)

main_window.show()

sys.exit(app.exec_())
