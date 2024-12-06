# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 12:21:36 2019
@author: chris
"""

from __future__ import unicode_literals
import sys
import os
import time
import seabreeze.spectrometers as sb
import matplotlib
import matplotlib.pyplot as plt
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
# Uncomment this line before running, it breaks sphinx-gallery builds
from PyQt5 import QtCore, QtWidgets
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"

spec = sb.Spectrometer.from_serial_number()
#https://oceanoptics.com/wp-content/uploads/External-Triggering-Options_Firmware3.0andAbove.pdf
spec.trigger_mode(0)
class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class InitialSpectrum(MyMplCanvas):

    def __init__(self, *args, **kwargs):
        self.integrationtime = 10000
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        self.bool=False
        timer.timeout.connect(self.update_figure)
        timer.start(1)
        self.background=0*spec.wavelengths()
        self.fwhm_t0=0
        self.overlay=False
        self.load_overlay=False
        self.load_overlaybkg=False
        self.setAxes=False
        self.trigmode=0
        spec.trigger_mode(self.trigmode)

    def compute_initial_figure(self):
        spec.integration_time_micros(self.integrationtime)
        self.axes.plot(spec.wavelengths(), spec.intensities())
        #self.axes.set_ylim([-1, 1.2])
        #self.axes.set_xlim((spm.freq_0 - 5 * spm.fwhm_f0), (spm.freq_0 + 5 * spm.fwhm_f0))
    def update_figure(self):
        spec.integration_time_micros(self.integrationtime)
        self.axes.cla()
        self.x=spec.wavelengths()
        y=spec.intensities()
        self.y=y-self.background
        if(self.bool==False):
            self.axes.plot(self.x, self.y)
        elif(self.bool==True):
            self.axes.plot(self.x, np.log(self.y))
        #print(self.integrationtime)
        if(self.setAxes==True):
            self.axes.set_ylim(self.ymin,self.ymax)
            self.axes.set_xlim(self.xmin,self.xmax)
        if(self.overlay==True):
            self.axes.plot(self.overlayx,self.overlayy)
        if(self.load_overlaybkg==True and self.load_overlay==True):
            self.axes.plot(self.load_overlayx,self.load_overlayy-self.load_overlaybkgy)
        if(self.load_overlay==True and self.load_overlaybkg==False):
            self.axes.plot(self.load_overlayx,self.load_overlayy)

        self.axes.text(self.x[np.argmax(self.y)], np.max(self.y), str(np.max(self.y)))
        self.draw()
        if(self.trigmode==2):
            plt.plot(self.x,self.y)
        
    def updateTrigMode(self,x):
        self.trigmode=x
        spec.trigger_mode(self.trigmode)
    def updateIntegrationTime(self,t):
        self.integrationtime = t
        # calculates FTL
        c=299700
        f=c /(np.array(self.x))
        f=np.flip(f)
        fvals=np.linspace(-1200,2800,num=2**13)
        print(np.all(np.diff(f) > 0))
        y=np.array(self.y-self.background)
        for i in range(len(y)):
            if(y[i]/np.max(y)<0.02):
                y[i]=0
        y=np.flip(y)
        yinterp=np.interp(fvals,f,y)
        time = np.fft.fftshift(np.fft.fftfreq(fvals.shape[0], fvals[1] -fvals[0]))
        Ef = np.sqrt(np.abs(yinterp))  # Electric field
        Et = np.fft.fftshift(np.fft.fft(Ef))
        
        It=np.abs(Et)**2
        
        Et=np.sqrt(It)*np.exp(1j*np.angle(Et))
        It=np.abs(Et)**2
        plt.plot(time,It/np.max(It))
        plt.show()
        print(It)
        print(time)
        print(time[It/np.max(It)>0.1])
        self.fwhm_t0 = (time[It/np.max(It)>0.1][-1]) - (time[It/np.max(It)>0.5][0])
        print(self.fwhm_t0*1000)
    def updateBackground(self,b):
        self.background = b
    def captureOverlay(self,b,x,y):
        self.overlay=b
        self.overlayx=x
        self.overlayy=y-self.background
    def loadOverlay(self,b,x,y):
        self.load_overlay=b
        self.load_overlayx=x
        self.load_overlayy=y
    def loadBackground(self,b,x,y):
        self.load_overlaybkg=b
        self.load_overlaybkgx=x
        self.load_overlaybkgy=y
        if(len(self.load_overlaybkgy)==2048):
            self.background=self.load_overlaybkgy
    def switchToLog(self):
        self.bool=True
    def switchOffLog(self):
        self.bool=False
    def autoScaleSwitch(self,b,xmin,xmax,ymin,ymax):
        self.setAxes=b
        self.xmin=float(xmin)
        self.xmax=float(xmax)
        self.ymin=float(ymin)
        self.ymax=float(ymax)
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        
        openFile = QtWidgets.QAction("&Open File", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.file_open)
        openBkgFile = QtWidgets.QAction("&Open Bkg File", self)
        openBkgFile.setShortcut("Ctrl+B")
        openBkgFile.setStatusTip('Open bkg File')
        openBkgFile.triggered.connect(self.bkgfile_open)
        self.file_menu.addAction(openFile)
        self.file_menu.addAction(openBkgFile)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)
        
        l = QtWidgets.QVBoxLayout(self.main_widget)
        
        #combo box for trigger mode
        self.cb = QtWidgets.QComboBox()
        self.cb.addItem("Normal (Free running) Mode")
        self.cb.addItem("Software Trigger Mode")
        self.cb.addItem("External Hardware Level Trigger Mode")
        self.cb.addItem("External Synchronization Trigger Mode")
        self.cb.addItem("External Hardware Edge Trigger Mode")
        self.cb.currentIndexChanged.connect(self.triggerMode)
        l.addWidget(self.cb)
        
        hbox = QtWidgets.QHBoxLayout()
        self.timeInput = QtWidgets.QLineEdit('1')
        self.fileNumberInput =QtWidgets.QLineEdit('0')
        self.fileNameInput =QtWidgets.QLineEdit(r'C:\Users\chris\OneDrive\Documents\spectrometer program')
        self.fileNameInput2 =QtWidgets.QLineEdit('\\')
        
        self.logcheckbox = QtWidgets.QCheckBox('Log')
        self.logcheckbox.stateChanged.connect(self.checkbox1)
        hbox.addWidget(self.logcheckbox)
        self.overlay_from_old = QtWidgets.QCheckBox('check if loading spectrum from oceanview')
        hbox.addWidget(self.overlay_from_old)
        self.pybutton5 = QtWidgets.QPushButton('capture overlay', self)
        self.pybutton5.clicked.connect(self.button5)
        hbox.addWidget(self.pybutton5)
        l.addLayout(hbox)
        self.sc = InitialSpectrum(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(self.sc)
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(QtWidgets.QLabel('xmin: '))
        self.xminInput = QtWidgets.QLineEdit('200')
        hbox1.addWidget(self.xminInput)
        hbox1.addWidget(QtWidgets.QLabel('xmax: '))
        self.xmaxInput = QtWidgets.QLineEdit('1000')
        hbox1.addWidget(self.xmaxInput)
        hbox1.addWidget(QtWidgets.QLabel('ymin: '))
        self.yminInput = QtWidgets.QLineEdit('0')
        hbox1.addWidget(self.yminInput)
        hbox1.addWidget(QtWidgets.QLabel('ymax: '))
        self.ymaxInput = QtWidgets.QLineEdit('10000')
        hbox1.addWidget(self.ymaxInput)
        self.pybutton5 = QtWidgets.QPushButton('Enable/Disable autoscale', self)
        self.pybutton5.clicked.connect(self.scaleButton)
        hbox1.addWidget(self.pybutton5)
        l.addLayout(hbox1)
        self.fwhmLabel=QtWidgets.QLabel('fwhm:'+str(self.sc.fwhm_t0))
        l.addWidget(self.fwhmLabel)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(QtWidgets.QLabel('integration time in ms'))
        hbox2.addWidget(self.timeInput)
        self.integration_time = self.timeInput.text()
        self.integration_time = int(self.integration_time)
        self.pybutton = QtWidgets.QPushButton('update integration time', self)
        self.pybutton.clicked.connect(self.button1)
        hbox2.addWidget(self.pybutton)
        l.addLayout(hbox2)
        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(QtWidgets.QLabel('number of files to save'))
        hbox3.addWidget(self.fileNumberInput)
        l.addLayout(hbox3)
        hbox4= QtWidgets.QHBoxLayout()
        hbox4.addWidget(QtWidgets.QLabel('file path'))
        hbox4.addWidget(self.fileNameInput)
        hbox4.addWidget(self.fileNameInput2)
        self.end_of_path=QtWidgets.QLabel('_spectrum'+'_'+str(self.integration_time)+'ms'+'_')
        hbox4.addWidget(self.end_of_path)
        l.addLayout(hbox4)
        self.pybutton2 = QtWidgets.QPushButton('Save', self)
        self.pybutton2.clicked.connect(self.button2)
        self.pybutton3 = QtWidgets.QPushButton('Plot', self)
        self.pybutton3.clicked.connect(self.button3)
        l.addWidget(self.pybutton2)
        hbox.addWidget(self.pybutton3)
        l.addLayout(hbox)
        self.pybutton4 = QtWidgets.QPushButton('Subtract Background', self)
        self.pybutton4.clicked.connect(self.button4)
        hbox.addWidget(self.pybutton4)
        
        
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("Which came first, the phoenix or the flame?", 2000)
        #If the internet can be trusted, this is a quote from Harry Potter book 7
        
    def triggerMode(self):
        print(self.cb.currentText())
        mode=self.cb.currentText()
        if(mode =='Normal (Free running) Mode'):
            self.sc.updateTrigMode(x=0)
        if(mode == 'Software Trigger Mode'):
            self.sc.updateTrigMode(x=1)
        if(mode == 'External Hardware Level Trigger Mode'):
            self.sc.updateTrigMode(x=2)
        if(mode == 'External Synchronization Trigger Mode'):
            self.sc.updateTrigMode(x=3)
        if(mode == 'External Hardware Edge Trigger Mode'):
            self.sc.updateTrigMode(x=4)
        
    def file_open(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File')
        file = open(name[0],'r')
        with file:
            if(self.overlay_from_old.isChecked()==True):
                z=np.loadtxt(file,skiprows=15)
                y=z[:,1]
                x=z[:,0]
                self.sc.loadOverlay(b=True,y=y,x=x)
            else:
                z=np.loadtxt(file)
                y=z[:,1]
                x=z[:,0]
                self.sc.loadOverlay(b=True,y=y,x=x)
    def bkgfile_open(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Bkg File')
        file = open(name[0],'r')
        with file:
            if(self.overlay_from_old.isChecked()==True):
                z=np.loadtxt(file,skiprows=15)
                y=z[:,1]
                x=z[:,0]
                self.sc.loadBackground(b=True,y=y,x=x)
            else:
                z=np.loadtxt(file)
                y=z[:,1]
                x=z[:,0]
                self.sc.loadBackground(b=True,y=y,x=x)
                
    def checkbox1(self):
        if(self.logcheckbox.isChecked()==True):
            self.sc.switchToLog()
        if(self.logcheckbox.isChecked()==False):
            self.sc.switchOffLog()
        
    #updates integration time and calculates FTL   
    def button1(self):
        self.integration_time = self.timeInput.text()
        self.integration_time = int(self.integration_time)*1000
        self.sc.updateIntegrationTime(t=self.integration_time)
        self.end_of_path.setText('_spectrum'+'_'+str(self.integration_time/1000)+'ms'+'_')
        self.fwhmLabel.setText('fwhm: '+str(self.sc.fwhm_t0)+' fs')
    
    #saves spectrum
    def button2(self):
        filenum = self.fileNumberInput.text()
        filenum = int(filenum)
        filename = self.fileNameInput.text()
        filename2 = self.fileNameInput2.text()
        x=spec.wavelengths()
        y=spec.intensities()
        x=np.array(x)
        y=np.array(y)
        yave=0*x
        for i in range(filenum):
            y=spec.intensities()
            y=np.array(y)
            yave=yave+y
            z=np.vstack((x,y)).T
            time.sleep(self.integration_time/(10**6))
            np.savetxt(str(filename)+str(filename2)+'_spectrum'+'_'+str(self.integration_time)+'us'+'_'+str(i)+'.txt',z)
        if(filenum==0):
            yave=y
        if(filenum!=0):
            yave=yave/(filenum)
            if(filenum>1):
                z=np.vstack((x,yave)).T
                np.savetxt(str(filename)+str(filename2)+'_spectrum'+'_'+str(self.integration_time)+'us'+'_'+'average'+'.txt',z)
        
        
    def button3(self):
        filenum = self.fileNumberInput.text()
        filenum = int(filenum)
        x=spec.wavelengths()
        y=spec.intensities()
        x=np.array(x)
        y=np.array(y)
        yave=0*x
        for i in range(filenum):
            y=spec.intensities()
            y=np.array(y)
            y=y-np.array(self.sc.background)
            yave=yave+y
            time.sleep(self.integration_time/(10**6))
        if(filenum==0):
            yave=y-np.array(self.sc.background)
        if(filenum!=0):
            yave=yave/(filenum)
        if(self.logcheckbox.isChecked()==False):
            plt.plot(x,yave)
        if(self.logcheckbox.isChecked()==True):
            plt.plot(x,np.log(yave))
        plt.show()
        
    #subtracts background
    def button4(self):
        b=spec.intensities()
        self.sc.updateBackground(b=b)
    def button5(self):
        if(self.sc.overlay ==False):
            b=True
        else:
            b=False
        x=spec.wavelengths()
        y=spec.intensities()
        print(y)
        self.sc.captureOverlay(b=b,x=x,y=y)
    def scaleButton(self):
        if(self.sc.setAxes == False):
            b=True
        else:
            b=False
        self.sc.autoScaleSwitch(b,xmin=self.xminInput.text(),xmax=self.xmaxInput.text(),ymin=self.yminInput.text(),ymax=self.ymaxInput.text())
    def fileQuit(self):
        self.close()
        spec.close()
    def closeEvent(self, ce):
        self.fileQuit()
    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """GUI for looking at spectrum from ocean optics spectrometer"""
                                )

if __name__ == "__main__":
    qApp = QtWidgets.QApplication(sys.argv)
    aw = ApplicationWindow()
    aw=ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    #qApp.exec_()