from PyQt5.QtCore import Qt
import threading
import subprocess
import signal
import sys
import serial
import time
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from ctypes import *
import win32api,win32gui,win32con

from signalslot import slot                   #信号槽文件 
from transfer import trans                    #通信文件 
from Ui_control import Ui_Control  
from Ui_pw1dialog import Ui_Dialog       
from Ui_seaddialog import Ui_seedDialog


class MyWindow(QMainWindow, Ui_Control,trans,slot):
    threadLock = threading.Lock()           # 线程锁，用于1、出光触发打开除种子源以外所有开启预燃工作；一键全开；一键全关；轮询；
    #threadlock_search = threading.Lock()
    #threadlock_time = threading.Lock()      # 线程锁，用于各种计时，出光
    pop_signal = pyqtSignal(str)       # 弹窗信号

    def __init__(self, parent=None):                        
        super(MyWindow, self).__init__(parent)
        MVS = threading.Thread(target=self.runExe)
        MVS.start()
        time.sleep(1.5)
        self.setupUi(self)            
        self.pre = [self.pre1,self.pre2,self.pre3,self.pre4,self.pre5]
        self.on=[self.on1,self.on2,self.on3,self.on4,self.on5]
        self.pw_v=[self.pw1_v_send,self.pw2_v_send,self.pw3_v_send,self.pw4_v_send,self.pw5_v_send]
        self.init()                     # 参数初始化、开串口、设置轮询
        self.signalslot()               # 信号槽
        self.init_v()                   
        self.lcdNumber.display(0.0)

    @staticmethod
    def runExe():
        exePath = "./res/MVS/Applications/Win32/MVS.exe"
        subprocess.Popen(exePath)

if __name__ == '__main__':
    #QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)       # 高清屏幕自适应
    app = QApplication(sys.argv)    # 每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    myWin = MyWindow() 
    SetParent_def = windll.user32.SetParent 
    SetWindowPos_def = windll.user32.SetWindowPos
    notepad_handle = win32gui.FindWindow(0,"MVS")
    print("MVS句柄：",notepad_handle)
    windll.user32.SetParent(notepad_handle, int(myWin.camera.winId()))
    myWin.show() 
    win32gui.MoveWindow(notepad_handle,0,0,myWin.camera.width(),myWin.camera.height(),True)
    sys.exit(app.exec_())           # 调用QApplication的exec_()方法时会使程序进入主循环。主循环会获取并分发事件。


