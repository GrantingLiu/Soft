
import threading
import signal
import sys
import serial
import time
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
#from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from signalslot import slot                   #信号槽文件 
from transfer import trans                    #通信文件 
from Ui_control import Ui_Control  
from Ui_pw1dialog import Ui_Dialog       
from Ui_seaddialog import Ui_seedDialog


class MyWindow(QMainWindow, Ui_Control,trans,slot):
    threadLock = threading.Lock()           # 线程锁，用于1、出光触发打开除种子源以外所有开启预燃工作；一键全开；一键全关；轮询；
    #threadlock_search = threading.Lock()
    #threadlock_time = threading.Lock()      # 线程锁，用于各种计时/，出光
    pop_signal = pyqtSignal(str)       # 弹窗信号

    def __init__(self, parent=None):                        
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)            
        self.pre = [self.pre1,self.pre2,self.pre3,self.pre4,self.pre5]
        self.on=[self.on1,self.on2,self.on3,self.on4,self.on5]
        self.pw_v=[self.pw1_v_send,self.pw2_v_send,self.pw3_v_send,self.pw4_v_send,self.pw5_v_send]
        self.init()                     # 参数初始化、开串口、设置轮询
        self.signalslot()               # 信号槽
        self.init_v()                   
        self.lcdNumber.display(0.0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow() 
    myWin.show() 
    sys.exit(app.exec_())    


