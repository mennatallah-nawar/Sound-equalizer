from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType # loadUiType: Open File
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters
import matplotlib.pyplot as plt
from scipy import signal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import math
import scipy.io.wavfile as wavfile
import scipy
from scipy.fftpack import fft, fftfreq
import scipy.fftpack as fftpk
from scipy.fftpack import irfft
from os import path ## os --> Operating system / path --> Ui File
import sys
import numpy as np

FORM_CLASS,_= loadUiType(path.join(path.dirname(__file__),"Sound_Equlizer.ui"))   # Creat Variable that load .ui file from folder path 

# Class Take main window from Qt Designer and the file of the GUI (FORM_CLass)that take file path and name
class MainApp(QtWidgets.QMainWindow, FORM_CLASS):                #QmainWindow: refers to main window in Qt Designer
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        #intial values
        self.SliderVal = 0
        self.NewFFT = 0
        self.workFlag = 0        
        self.counter = 0
        self.range_counter=0
        self.slider_counter=0
        self.SpectroHighFreq = 0
        self.SpectrolowFreq = 0
        self.zoomIn = 0
        self.zoomout = 0
        self.scale = 0.01
        self.zoomFlag = 0

        self.Handel_Botton()
        self.compute_data()
        self.DrawSignal()
        self.colors()
        self.DrawSpectro()
        self.HandleSlider()
        self.HandelSliderHorizontal()
        self.SpectroChangeSlider()

       
    def Handel_Botton(self):

        self.StartButton.clicked.connect(self.Handel_Start)
        self.StopButton.clicked.connect(self.Handel_Pause)
        self.ZoominButton.clicked.connect(self.Zoom_In)
        self.ZoomoutButton.clicked.connect(self.Zoom_Out)
        self.insert.clicked.connect(self.insert_Tab)
        self.horizontalSlider.valueChanged.connect(self.Change_Slider)

    def Handel_Start(self):
        self.timer.start()
        self.workFlag = 0    #signal on

    def Handel_Pause(self):
        self.timer.stop()
        self.workFlag = 1   #signal off


    def Zoom_In(self):

        if self.workFlag == 1 :
            self.zoomFlag = 1
            self.zoomIn = self.horizontalSlider.value()/100000
            print(self.zoomIn)
            self.scale *= 0.8
            self.graphicsView_inputsignal.setXRange( self.zoomIn  + (10*self.scale) ,self.zoomIn - (10*self.scale),padding=0)
            self.graphicsView_outputsignal.setXRange( self.zoomIn  + (10*self.scale) ,self.zoomIn - (10*self.scale),padding=0)
        
    def Zoom_Out(self):
        if self.workFlag == 1 :
            self.zoomFlag = 2
            self.zoomout = self.horizontalSlider.value()/100000
            self.scale *= 1.2
            self.graphicsView_inputsignal.setXRange( self.zoomout  - (10*self.scale) ,self.zoomout + (10*self.scale),padding=0)
            self.graphicsView_outputsignal.setXRange( self.zoomout  - (10*self.scale) ,self.zoomout + (10*self.scale),padding=0)
       

    def insert_Tab(self):
       
        self.tabWidget.addTab(MainApp(), "new tab" )
        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        
    def close_tab(self,index):               #tab (tab) close the function;
        self.tabWidget.removeTab(index)
    
 
    ########################### Read and Draw signals ##############################

        
    def Timer(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.DrawSignal)
        self.timer.start()


    def generate_sine_wave(self, freq):
        self.s_rate = 9000 # Hertz
        self.duration = 5  # Seconds
        self.x = np.linspace(0, self.duration, self.s_rate * self.duration, endpoint=False)
        self.frequencies = self.x * freq
        print()
        
        # 2pi because np.sin takes radians
        self.y1 = np.sin((2 * np.pi) * self.frequencies)
        self.y2 = np.sin((2 * np.pi) * self.frequencies * 5)
        self.y3 = np.sin((2 * np.pi) * self.frequencies * 10)
        self.y4 = np.sin((2 * np.pi) * self.frequencies * 15)
        self.y5 = np.sin((2 * np.pi) * self.frequencies * 20)
        self.y6 = np.sin((2 * np.pi) * self.frequencies * 25)
        self.y7 = np.sin((2 * np.pi) * self.frequencies * 30)
        self.y8 = np.sin((2 * np.pi) * self.frequencies * 35)
        self.y9 = np.sin((2 * np.pi) * self.frequencies * 40)
        self.y10 = np.sin((2 * np.pi) * self.frequencies * 45)
        self.y = self.y1 + self.y2 + self.y3 + self.y4 + self.y5 + self.y6 + self.y7 + self.y8 + self.y9 + self.y10
        return self.x, self.y



    def compute_data(self):
        #self.s_rate, self.signal = wavfile.read("sine.wav") 
        self.time_vec, self.signal = self.generate_sine_wave(100)
        self.n = len(self.signal)  # length of the signal
        self.time_step = 1.0/self.s_rate
        self.timeLength = self.n / self.s_rate
        self.time_vec = np.arange(0, self.timeLength, self.time_step)

        self.FFT = abs(fft(self.signal))
        self.freqs = fftpk.fftfreq(len(self.FFT), self.time_step)
        self.fmax = (len(self.FFT)//2)
     

        self.sig_fft = scipy.fftpack.fft(self.signal)
        self.power = np.abs(self.sig_fft)
        self.NewFFT = np.array(self.power)

        # The corresponding frequencies
        self.sample_freq = scipy.fftpack.fftfreq(self.signal.size, d=self.time_step)
        self.pos_mask = np.where(self.sample_freq > 0)
        self.freq = self.sample_freq[self.pos_mask]
        self.peak_freq = self.freq[self.NewFFT[self.pos_mask].argmax()]
        self.high_freq_fft = self.sig_fft.copy()
        self.spectro = self.high_freq_fft.copy()
        self.inverseSignal()

    def inverseSignal(self):

        self.high_freq_fft[np.abs(self.sample_freq) > self.peak_freq] = 0
        self.filtered_sig = scipy.fftpack.ifft(self.high_freq_fft)
        self.spectro[np.abs(self.sample_freq) > self.peak_freq] = 0
        self.filtered_sig_spectro = scipy.fftpack.ifft(self.spectro)
        self.Timer()
        

    def DrawSignal(self):       #Draw input and output signals

        self.filtered_sig_real = self.filtered_sig.real
        self.counter = self.counter + 500
        self.graphicsView_outputsignal.clear()
        self.graphicsView_outputsignal.plot(self.time_vec [0:self.counter], self.filtered_sig_real [0:self.counter])

        self.signal_real = self.signal.real
        self.graphicsView_inputsignal.clear()
        self.graphicsView_inputsignal.plot(self.time_vec [0:self.counter], self.signal_real [0:self.counter])
        self.SpectroChangeSlider()
        self.DrawSpectro()

        if self.slider_counter < len(self.time_vec):                                                        #To stop at the limit of the graph
            self.graphicsView_inputsignal.setXRange( self.range_counter,self.range_counter+0.05,padding=0)
            self.graphicsView_outputsignal.setXRange( self.range_counter,self.range_counter+0.05,padding=0)
            #print(self.range_counter)
            self.horizontalSlider.setValue(self.slider_counter)
            #print(self.horizontalSlider.value())
            self.range_counter = self.range_counter + 0.05
            self.slider_counter = self.slider_counter + 450


    def DrawSpectro(self):
        self.inverseSignal()
        self.color = self.colorpalette.currentText()
        self.filtered_sig_spectro_real = self.filtered_sig_spectro.real
        self.graphicsView_spectrogram.canvas.axes.clear()
        self.graphicsView_spectrogram.canvas.axes.specgram(self.filtered_sig_spectro_real,cmap= (self.color))
        self.graphicsView_spectrogram.canvas.draw()


    ###################### Sliders Part ############################

    def HandelSliderHorizontal(self):
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(len(self.time_vec)-200)
        self.horizontalSlider.setTickInterval(200)
    
    def Change_Slider(self):
        #Normal Mode
        if self.zoomFlag == 0: 
            self.value = self.horizontalSlider.value()/100000
            if self.workFlag == 1: #paused
                self.graphicsView_inputsignal.setXRange(self.value,self.value+1)
                self.graphicsView_outputsignal.setXRange(self.value,self.value+1)
            elif self.workFlag == 2: #End of array (Paused)
                self.graphicsView_inputsignal.setXRange(self.value,self.value+1)
                self.graphicsView_outputsignal.setXRange(self.value,self.value+1)
        #Zoom In Mode        
        elif self.zoomFlag ==1:
            self.zoom = self.horizontalSlider.value()/100000
            if self.workFlag == 1:
                self.graphicsView_inputsignal.setXRange(self.zoom  + (10*self.scale),self.zoom  - (10*self.scale))
                self.graphicsView_outputsignal.setXRange(self.zoom  + (10*self.scale),self.zoom  - (10*self.scale))
            elif self.workFlag == 2:
                self.graphicsView_inputsignal.setXRange(self.zoom  + (10*self.scale),self.zoom  - (10*self.scale))
                self.graphicsView_outputsignal.setXRange(self.zoom  + (10*self.scale),self.zoom  - (10*self.scale))
        #Zoom Out Mode 
        elif self.zoomFlag ==2:
            self.zoom = self.horizontalSlider.value()/100000
            if self.workFlag == 1:
                self.graphicsView_inputsignal.setXRange(self.zoom  - (10*self.scale),self.zoom  + (10*self.scale))
                self.graphicsView_outputsignal.setXRange(self.zoom  - (10*self.scale),self.zoom  + (10*self.scale))
            elif self.workFlag == 2:
                self.graphicsView_inputsignal.setXRange(self.zoom  - (10*self.scale),self.zoom  + (10*self.scale))
                self.graphicsView_outputsignal.setXRange(self.zoom  - (10*self.scale),self.zoom  + (10*self.scale)) 


    def SpectroChangeSlider(self):

        self.spectro = self.high_freq_fft.copy()
        print("low")
        print(self.verticalSlider_11.value())
        print("high")
        print(self.verticalSlider_12.value())

        

        self.SpectrolowFreq = int ((self.verticalSlider_11.value()/100) * (len(self.spectro)//2))
        self.SpectroHighFreq = int((self.verticalSlider_12.value()/100) * (len(self.spectro)//2))

        self.SpectrolowFreqNeg = - self.SpectrolowFreq 
        self.SpectroHighFreqNeg = - self.SpectroHighFreq
        self.lenNeg = - (len(self.spectro)//2)

        if self.SpectrolowFreq == 0 and self.SpectroHighFreq == (len(self.spectro)//2):
            self.spectro = self.spectro
            print(self.spectro)

        if self.SpectrolowFreq != 0:
            self.spectro [0 : self.SpectrolowFreq] = (self.high_freq_fft [0 : self.SpectrolowFreq]) * 0
            self.spectro [self.SpectrolowFreqNeg : -1] = (self.high_freq_fft [self.SpectrolowFreqNeg : -1]) * 0
            
            print("low")

        if self.SpectroHighFreq != (len(self.spectro)//2):
            self.spectro[self.SpectroHighFreq : len(self.spectro)//2] = (self.high_freq_fft [self.SpectroHighFreq : len(self.spectro)//2]) * 0
            self.spectro[self.lenNeg : self.SpectroHighFreqNeg] = (self.high_freq_fft [self.lenNeg  : self.SpectroHighFreqNeg]) * 0
            print("high")

        
        if self.verticalSlider_11.value() == 50 and self.verticalSlider_12.value() == 50:
            self.spectro = np.zeros(len(self.spectro))

        print(len(self.filtered_sig_real))
        print(self.SpectrolowFreq)
        print(self.SpectroHighFreq)
        self.DrawSpectro()

    
    def HandleSlider(self):
        self.verticalSlider_1.valueChanged.connect(lambda: self.ChangeSlider(1))
        self.verticalSlider_2.valueChanged.connect(lambda: self.ChangeSlider(2))
        self.verticalSlider_3.valueChanged.connect(lambda: self.ChangeSlider(3))
        self.verticalSlider_4.valueChanged.connect(lambda: self.ChangeSlider(4))
        self.verticalSlider_5.valueChanged.connect(lambda: self.ChangeSlider(5))
        self.verticalSlider_6.valueChanged.connect(lambda: self.ChangeSlider(6))
        self.verticalSlider_7.valueChanged.connect(lambda: self.ChangeSlider(7))
        self.verticalSlider_8.valueChanged.connect(lambda: self.ChangeSlider(8))
        self.verticalSlider_9.valueChanged.connect(lambda: self.ChangeSlider(9))
        self.verticalSlider_10.valueChanged.connect(lambda: self.ChangeSlider(10))
        self.verticalSlider_11.valueChanged.connect(self.SpectroChangeSlider)
        self.verticalSlider_12.valueChanged.connect(self.SpectroChangeSlider)


    def ChangeSlider(self, SliderNumber):
        lowFreq = int(((SliderNumber-1)/10)*self.fmax)
        HighFreq = int(((SliderNumber)/10)*self.fmax)
        print(lowFreq)
        print(HighFreq)
        if lowFreq == 0:
            negLow = -1
            print(self.NewFFT[-1])
            print(0)
        else:
            negLow = - lowFreq
            print("notzero")
        
        negHigh = - HighFreq

        self.SliderValue(SliderNumber)
      
        self.NewFFT[lowFreq:HighFreq] = (self.power[lowFreq:HighFreq])*(self.SliderVal)
        self.NewFFT[negHigh:negLow] = (self.power[negHigh:negLow])*(self.SliderVal)

        self.high_freq_fft[lowFreq:HighFreq] = (self.sig_fft[lowFreq:HighFreq])*(self.SliderVal)
        self.high_freq_fft[negHigh:negLow] = (self.sig_fft[negHigh:negLow])*(self.SliderVal)

        
        self.inverseSignal()
        if lowFreq == 0:
            negLow = -1
            self.NewFFT[-1:0]=0
            self.NewFFT[-1]=0
            self.NewFFT[0] =0

        self.DrawSignal()


    def SliderValue(self, SliderNumber):
        
        if  SliderNumber == 1:
            self.SliderVal = self.verticalSlider_1.value()
        elif SliderNumber == 2:
            self.SliderVal = self.verticalSlider_2.value()
        elif SliderNumber == 3:
            self.SliderVal = self.verticalSlider_3.value()
        elif SliderNumber == 4:
            self.SliderVal = self.verticalSlider_4.value()
        elif SliderNumber == 5:
            self.SliderVal = self.verticalSlider_5.value()
        elif SliderNumber == 6:
            self.SliderVal = self.verticalSlider_6.value()
        elif SliderNumber == 7:
            self.SliderVal = self.verticalSlider_7.value()
        elif SliderNumber == 8:
            self.SliderVal = self.verticalSlider_8.value()
        elif SliderNumber == 9:
            self.SliderVal = self.verticalSlider_9.value()
        elif SliderNumber == 10:
            self.SliderVal = self.verticalSlider_10.value()
        elif SliderNumber == 11:
            self.SliderVal = self.verticalSlider_11.value()
        elif SliderNumber == 12:
            self.SliderVal = self.verticalSlider_12.value()

    ################## color palette ###############

    def colors (self):
        self.colorpalette.currentIndexChanged.connect(self.selectedcolor)
        

    def selectedcolor (self): 
        self.color = self.colorpalette.currentText()
        self.graphicsView_spectrogram.canvas.axes.specgram(self.filtered_sig_spectro_real,cmap= (self.color))
        self.graphicsView_spectrogram.canvas.draw()
        print (self.color)
        
#######################################################