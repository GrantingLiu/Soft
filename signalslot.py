
#信号槽
#from PyQt5.Qt import *
import sys
from PyQt5.QtCore import QTimer,pyqtSignal
#from PyQt5 import QtCore, QtGui, QtWidgets
import time
#import serial 
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox
from Ui_pw1dialog import Ui_Dialog
from Ui_seaddialog import Ui_seedDialog
import threading
from transfer import trans      #2020年1月20日加的
import transfer
from  Ui_control import Ui_Control

# 电源预燃和运行
pre_onorder = ["aa 01 12 cc 33 c3 3c","aa 02 12 cc 33 c3 3c","aa 03 12 cc 33 c3 3c","aa 04 12 cc 33 c3 3c","aa 05 12 cc 33 c3 3c"]
pre_offorder = [ "aa 01 10 cc 33 c3 3c","aa 02 10 cc 33 c3 3c","aa 03 10 cc 33 c3 3c","aa 04 10 cc 33 c3 3c", "aa 05 10 cc 33 c3 3c"]
on_onorder = ["aa 01 22 cc 33 c3 3c","aa 02 22 cc 33 c3 3c","aa 03 22 cc 33 c3 3c","aa 04 22 cc 33 c3 3c","aa 05 22 cc 33 c3 3c"]
on_offorder = ["aa 01 20 cc 33 c3 3c","aa 02 20 cc 33 c3 3c","aa 03 20 cc 33 c3 3c","aa 04 20 cc 33 c3 3c","aa 05 20 cc 33 c3 3c"]

class slot():
    def signalslot(self):

        self.pre[0].clicked.connect(lambda:self.power_pre(0))
        self.pre[1].clicked.connect(lambda:self.power_pre(1))
        self.pre[2].clicked.connect(lambda:self.power_pre(2))
        self.pre[3].clicked.connect(lambda:self.power_pre(3))
        self.pre[4].clicked.connect(lambda:self.power_pre(4))

        self.on[0].clicked.connect(lambda:self.power_on(0))
        self.on[1].clicked.connect(lambda:self.power_on(1))
        self.on[2].clicked.connect(lambda:self.power_on(2))
        self.on[3].clicked.connect(lambda:self.power_on(3))
        self.on[4].clicked.connect(lambda:self.power_on(4))

        self.pw1_v_send.clicked.connect(lambda:self.change_power(0))
        self.pw2_v_send.clicked.connect(lambda:self.change_power(1))
        self.pw3_v_send.clicked.connect(lambda:self.change_power(2))
        self.pw4_v_send.clicked.connect(lambda:self.change_power(3))
        self.pw5_v_send.clicked.connect(lambda:self.change_power(4))

        self.on_all.clicked.connect(self.all_on_def)     # 电源全开
        self.off_all.clicked.connect(self.alloff_def)    # 电源全关
        self.shutter.clicked.connect(self.shutter_con)   # 光阑
        self.stop_emer.clicked.connect(self.stop_judge)  # 急停                  
        self.start_laser.clicked.connect(self.count_down_def)       # 出光
        self.pop_signal.connect(self.pop_error)
        
    # 电源全开的线程槽函数
    def all_on_def(self):
        print("开启全开线程")
        thread_allon = threading.Thread(target=self.allon)
        thread_allon.setDaemon(True)
        thread_allon.start()

    # 出光的线程槽函数
    def count_down_def(self):
        thread_count_down = threading.Thread(target=self.count_down)
        thread_count_down.setDaemon(True)
        thread_count_down.start()

    def start_light_def(self):
        thread_start_light = threading.Thread(target=self.start_light)
        thread_start_light.setDaemon(True)
        thread_start_light.start()
    
    # 除了种子源的工作，其他全开
    def start_light(self):
        print("开启出光")
        self.threadLock.acquire()  
        for i in range(0,5):        # 预燃全开
            self.data_write(str=pre_onorder[i])
            self.pre[i].setChecked(True)
            self.on[i].setEnabled(True)
            time.sleep(1)
        for i in range(1,5):        # 种子源工作不开
            self.on[i].setChecked(True)
            self.data_write(str=on_onorder[i])
            time.sleep(0.5)
        self.threadLock.release()# 释放锁，开启下一个线程        


    # 电源全关线程槽函数
    def alloff_def(self):
        thread_alloff = threading.Thread(target=self.alloff,args=(0,))
        thread_alloff.start()

    def stop_judge(self):
        self.stop_emer.clicked.disconnect(self.stop_judge)      # 解除原有信号槽。因为都要用到clicked
        self.times = 1  
        self.timer_stop.singleShot(700,lambda:self.count_stop_judge(self.times))   # 定时器触发信号                                        # 点击次数为1
        self.stop_emer.clicked.connect(self.inclease_times)
        # self.timer_stop.timeout.connect(lambda:self.count_stop_judge(self.times))      # 计时结束后查看点击次数

    def inclease_times(self):
        self.times += 1
        if self.times == 2:       
            # 关闭所有预燃
            self.alloff(1)

    def count_stop_judge(self,all_times):
        # self.timer_stop.stop()
        print("0.7秒内点击急停次数：",all_times,"\n")
        self.stop_emer.clicked.disconnect(self.inclease_times)      # 解除现有计数信号槽
        self.stop_emer.clicked.connect(self.stop_judge)         # 变为原来触发计时信号槽

    def count_down(self):
        total_time = 180
        have_volt = []
        nohave_volt = []
        for i in range(0,5):
            print("看第",i+1,"台")
            if self.volt_state[i] == 1:
                have_volt.append(i+1)
                print("第%d台已开机" % (i+1))
            else:
                nohave_volt.append(i+1)
                print("第%d台未开机" % (i+1))

        if len(have_volt) == 5:          # 都开机了才能出光
            print("已全开机，准备出光")
            self.start_light_def()
            while total_time != 0:
                minute = total_time//60
                second = total_time % 60
                total_time -= 1
                time.sleep(1)
                print("%02d:%02d" % (minute,second))
                self.count_down_text.setText("%02d:%02d" % (minute,second))
            print("倒计时结束，出光")
            self.on[0].setEnabled(True)
            self.on[0].setChecked(True)
            self.data_write(str=on_onorder[0])
            self.count_down_text.setText("")
        else:
            print("未全开机")
            number_str = ""
            for i in range(0,len(nohave_volt)):
                if nohave_volt[i] == 1:     # 是种子源的话
                    name_volt = "种子源"
                else:
                    name_volt = "电源" + str(nohave_volt[i]-1) 
                if i == (len(nohave_volt))-1:   # 是未开机的设备中最后一个的话后面不加逗号
                    number_str = number_str + name_volt
                else:
                    number_str = number_str + name_volt + ","
            self.pop_signal.emit(number_str)

    def pop_error(self,num):
        QMessageBox.about( None,"错误",  num + "未开启!")
            
            


    def shutter_con(self):
        if self.shutter.isChecked():
            print("开shutter")
            self.data_write(str="FE 05 00 00 FF 00 98 35")
        else:
            self.data_write(str="FE 05 00 00 00 00 D9 C5")

    def power_pre(self,i):
        if self.pre[i].isChecked():
            print("开第%d台预燃"%(i+1))
            self.on[i].setEnabled(True)
            self.data_write(str=pre_onorder[i])
         
        else:
            print("关第%d台预燃"%(i+1))
            self.on[i].setChecked(False)
            self.on[i].setEnabled(False)
            self.data_write(str=pre_offorder[i])

    def power_on(self,i):
        if self.on[i].isChecked():
            print("开第%d台运行" % (i+1))
            self.data_write(str=on_onorder[i])
        else:
            print("关第%d台运行" % (i+1))
            self.data_write(str=on_offorder[i])

    def allon(self):
        print("准备全开")
        self.threadLock.acquire()  
        for i in range(0,5):
            if self.volt_state[i] == 1:     # 关机就不用管
                if self.pre[i].isChecked():     #要是已经开了就不用开了
                    pass
                else:
                    self.data_write(str=pre_onorder[i])
                    self.pre[i].setChecked(True)
                    self.on[i].setEnabled(True)
                    time.sleep(1)
        for i in range(0,5):
            if self.volt_state[i] == 1:
                if self.on[i].isChecked():
                    pass
                else:
                    self.on[i].setChecked(True)
                    self.data_write(str=on_onorder[i])
                    time.sleep(0.5)
        self.threadLock.release()# 释放锁，开启下一个线程
        
    
    def alloff(self,urgency):
        print("接受到的urgency：",urgency)
        if urgency == 0:     # 非急停，先关运行再关预燃
            self.threadLock.acquire() 
            for i in range(4,-1,-1):
                if self.on[i].isChecked():
                    self.data_write(str=on_offorder[i])
                    self.on[i].setChecked(False)
                    time.sleep(0.5)
            for i in range(4,-1,-1):
                if self.pre[i].isChecked():
                    self.on[i].setChecked(False)
                    self.pre[i].setChecked(False)
                    self.on[i].setEnabled(False)
                    self.data_write(str=pre_offorder[i])
                    time.sleep(1)
            self.threadLock.release()
        if urgency == 1:
            print("开始发送急停")
            for i in range(0,5):
                if self.pre[i].isChecked():
                    self.on[i].setChecked(False)
                    self.pre[i].setChecked(False)
                    self.on[i].setEnabled(False)
                    self.data_write(str=pre_offorder[i])
                    print("第%d台电源急停" % (i+1))
                    time.sleep(0.05)
        

    def change_power(self,ch):                        #设置电压
        volt_window = Ui_Dialog()
        if ch == 0:      # 种子源
            volt_window.setMaximum = 1400
        else:
            volt_window.setMaximum = 2000
        if self.pw_v[ch].text() == "loading":
            pass
        else:   
            volt_window.spinBox.setValue(int(self.pw_v[ch].text()))
            result = volt_window.exec_()
            set_value = volt_window.spinBox.value()
            hex_value = '%04x' % set_value                   #转换为16进制，不满4位前面补0
            send_value = "aa 0" + str(ch+1) + " a1 "+ hex_value + " cc 33 c3 3c"
            print("第%d台指令是" % (ch+1),send_value)
            self.data_write(str=send_value)
            self.pw_v[ch].setText(str(set_value))   #修改按钮显示电压