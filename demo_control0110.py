
import threading
import signal
import sys
import serial
import time
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QToolTip,QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal

from signalslot import slot                   #信号槽文件 
from transfer import trans                    #通信文件 
from Ui_controlUI0319 import Ui_Control  
from Ui_pw1dialog0110 import Ui_Dialog       
from Ui_seaddialog import Ui_seedDialog


class MyWindow(QMainWindow, Ui_Control,trans,slot):
    threadLock = threading.Lock()       # 用于开关电源
    threadlock_search = threading.Lock()
    threadlock_time = threading.Lock()      # 用于各种计时，出光

    pop_signal = pyqtSignal(str)       # 弹窗信号

    def __init__(self, parent=None):                        
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)            
        print("主界面")

        self.pre = [self.pre1,self.pre2,self.pre3,self.pre4,self.pre5]
        self.on=[self.on1,self.on2,self.on3,self.on4,self.on5]
        self.pw_v=[self.pw1_v_send,self.pw2_v_send,self.pw3_v_send,self.pw4_v_send,self.pw5_v_send]

        print("信号槽")
        self.init()                     #开串口
        print("串口")
        self.signalslot()
        self.init_v()             #2020.03.13测试初始化GUI界面显示电压值从 
        self.lcdNumber.display(0.0)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    myWin = MyWindow() 
    
    myWin.show() 
    
    sys.exit(app.exec_())    


