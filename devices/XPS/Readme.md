# Newport XPS

This module provides code necessary to interface with Newport XPS controller using Python.

The framework for this class is built upon the SDK interface is developed in the Python module [newportxps](https://github.com/pyepics/newportxps). The code communicates with the XPS through "Actuator" objects, which are individual actuators connected to the XPS through the DRV slots.

As an example, connecting to and reading the status of an XPS Actuator may look like:
```python
from XPS import XPS

xps = XPS()
```

The original XPS class was written using newportxps-0.2.0. Since then a new release version 0.3 has become available. This might lead to breaking of certain functions, so testing should be performed.

Also provided is an SOP for working with the XPS hardware, and an example Python GUI written in [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro), a Python wrapper for the Qt application framework. The GUI was designed using the [Qt designer](https://doc.qt.io/qt-5/qtdesigner-manual.html) program bundled with Anaconda installation. The GUI enables interfacing with a single XPS stage.


## Update Nov 21, 2024:

Recent changes to the [newportxps](https://github.com/pyepics/newportxps) Python wrapper code for v0.9 has changed how connection to the XPS occurs. In order to properly connect, ssh keys needs to be saved onto the computer attempting to connect to the XPS. This can be performed with the command
```
ssh-keyscan (IP Address of XPS Controller) >> ~/.ssh/known_hosts
```
Note that a .ssh folder may need to be created in the default User directory of the computer. This command may generate a UTF-16 encoded file. The XPS code requires UTF-8 encoding. In order to change the UTF-16 encoding simply open the file in notepad and 'Save As' with the correct encoding selected.

![image](https://github.com/user-attachments/assets/a63d7491-da3d-4f0d-a64f-b13883bbde1c)
