
#串口通信
#from PyQt5.QtCore import Qt
from PyQt5.QtCore import QUrl
import sys
import threading
from threading import Thread, Lock
from PyQt5 import QtCore, QtGui, QtWidgets,QtMultimedia
from PyQt5.QtCore import QTimer,pyqtSignal
import sys
from PyQt5.QtCore import QTimer
import time
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QMessageBox
from Ui_control import Ui_Control
from Ui_seaddialog import Ui_seedDialog

class trans():
    # 初始化操作，参数初始化、开串口、设置轮询
    def init(self):
        #thread_v = threading.Thread(target=self.init_v)
        #thread_v.setDaemon(True)
        self.timer = QTimer(self)
        self.timer9600 = QTimer(self)
        self.timer_stop = QTimer(self) 
        #self.timer.timeout.connect(self.data_read)   #下面读取电压的init_v
        print("start read")
        self.response = ''
        self.now_num = 0
        self.volt_state = [0,0,0,0,0]
        self.port_open()   



    
    def port_open(self):            # 搜索并打开serial串口
        port_list = list(serial.tools.list_ports.comports())        # 所有串口
        self.serial_9600_name = ''
        if len(port_list) == 0:     # 如果检测不到任何串口 
            print('无任何串口')
            QMessageBox.about( None,"错误",  "无任何串口！")
            

            sys.exit()              # 退出程序
        else:
            k = -2                  
            comm = []
            for i in range(0,len(port_list)):
                port = str(port_list[i])
                sign_serial = "erial"
                useful = port.find(sign_serial)
                if useful != -1:            # find函数的返回值不为-1，则查找到了serial串口
                    k = i                   # 记录查找到目标时的起始下标，因为查找的erial，前面至少一个s，所以起始下标一定会大于0
                    comm.append(port_list[i])       # 把找到的serial串口名添加进列表
            if len(comm) > 0: 
                COM_9600 = list(comm[0])          # 串口是列表中的元素
                self.serial_9600_name = COM_9600[0]    # 元素的第一部分是COM i    
                self.serial_9600 = serial.Serial(
                    port = self.serial_9600_name,
                    baudrate = 9600,
                    bytesize = 8,
                    stopbits = 1,
                    parity = "N")
                print("可用9600端口名>>>", self.serial_9600.name,self.serial_9600.isOpen)
                self.serial_9600.close()
                try:
                    self.serial_9600.open()
                except:
                    print("串口打开失败")
                    QMessageBox.about( None,"错误",  "打开串口失败！")
                    sys.exit()  
            else:
                print("无serial串口")
                QMessageBox.about( None,"错误",  "无serial串口！")
                sys.exit()
            if self.serial_9600.isOpen():
                print(self.serial_9600.port,"is open")
                for i in range(0,5):
                    self.on[i].setEnabled(False)
                print("运行按钮已false")
                self.timer.start(5000)      # 轮询查电压
                self.timer.timeout.connect(self.inquiry_def)

    def inquiry_def(self):
        print("开启轮询线程")
        thread_inquiry = threading.Thread(target=self.init_v)
        thread_inquiry.setDaemon(True)
        thread_inquiry.start()


    def init_v(self):
        self.threadLock.acquire()       # 和一键全开关锁在一起  
        # 电压值列表每一次轮询都归零
        self.voltage = [0,0,0,0,0]     
        # 发送指令获取电压值
        for i in range(1,6):                    
            addr = "0"+str(i)                   
            update_v=self.get_volt(addr)        # 发送指令，查询地址对应的电源电压
            #print("查询地址为",i,"的电源")
        print("这一轮查询电压结束","\n")
        # 查询温度
        self.data_write(str="01 04 03 E8 00 01 B1 BA")
        time.sleep(0.05)     
        # 读取返回指令
        hex_data = self.data_read()
        # 更新电压值数组和温度
        self.search_volt(hex_data)      

        # 根据电压值列表，二次确认电压后，更新界面
        for i in range(0,5):
            if self.voltage[i] == 0:
                time.sleep(0.1)
                self.get_volt("0"+str(i+1))
                time.sleep(0.1)
                second_read = self.data_read()
                self.search_volt(second_read)      #再查询该电源并更新电压值数组
                if self.voltage[i] == 0:
                    self.reset_v(i)      # 两次都未读到，才判断为未开机
                    self.volt_state[i] = 0
                    #print("两次未读到第%d台电压" % (i+1))
                    continue
            else:
                if self.voltage[i] > 0 and self.voltage[i] < 2000:
                    self.pw_v[i].setText(str(self.voltage[i]))
                    self.pre[i].setEnabled(True)
                    self.volt_state[i] = 1
                else:
                    print("电压值异常！")
                    self.volt_state[i] = 0
                    pass        
        # 运行全关或全开时才能动shutter
        shutter_enabled = 0
        for i in range(1,5):
            shutter_enabled += self.on[i].isChecked()
        #print("shutter_enabled:",shutter_enabled)
        if shutter_enabled == 0 or shutter_enabled == 4:
            self.shutter.setEnabled(True)
            #print("可动光阑")
        else:
            self.shutter.setEnabled(False)
            #print("不可动光阑")
        self.threadLock.release()

    def search_volt(self,get_v):
        if get_v == 0:
            return
        for i in range(0,len(get_v),3):             
            if get_v[i:i+2] == "BB" and get_v[i+6:i+8] == "C3" and  get_v[i+21:i+32] == "CC 33 C3 3C":
                addr_v = get_v[i+4]       # 地址位
                high_volt = get_v[i+9:i+11]
                low_volt = get_v[i+12:i+14]
                hex_volt = high_volt+low_volt
                self.real_v = int(hex_volt,16)
                print("得到第%c台电压值：" % addr_v,self.real_v)
                self.voltage[int(addr_v)-1] = self.real_v       # 更新电压值数组

            if get_v[i:i+8] == "01 04 02":
                high_tem = get_v[i+9:i+11]
                low_tem = get_v[i+12:i+14]
                hex_tem = high_tem+low_tem
                real_tem = int(hex_tem,16)/10
                print("温度是：",real_tem)
                self.lcdNumber.display(real_tem)
                if real_tem > 50:
                    url = QUrl.fromLocalFile(".\\res\\warm.mp3")
                    content =  QtMultimedia.QMediaContent(url)
                    player = QtMultimedia.QMediaPlayer()
                    player.setMedia(content)
                    player.play()
                    print("play")
                    player.setVolume(10)
                    QMessageBox.about( None,"错误",  "温度异常！")

            else:
                self.lcdNumber.display(0)



    def reset_v(self,ch):
        self.pw_v[ch].setText("loading")
        print("重置电压第",ch+1,"台电压值")
        self.pre[ch].setChecked(False)
        self.pre[ch].setEnabled(False)
        self.on[ch].setChecked(False)
        self.on[ch].setEnabled(False)



    def get_volt(self, address):    #2020年3月18日新加；返回值为电压值，
        time.sleep(0.05)
        read_v = "aa " + address + " c3 cc 33 c3 3c"     
        self.data_write(str=read_v)     #发送查询指令


    def data_write(self, str):      #发送指令
        if self.serial_9600.isOpen(): 
            input_s = str
            if input_s != "":
                input_s = input_s.strip()
                send_list = []
                while input_s != '':
                    try:
                        num = int(input_s[0:2], 16)
                    except ValueError:
                        return None
                    input_s = input_s[2:].strip()
                    send_list.append(num)
                input_s = bytes(send_list)
                num = self.serial_9600.write(input_s)
                print("已发送",input_s)
        else:
            print("未打开串口！")
            pass


    def data_write_pump(self,str):      
        if self.serial_9600.isOpen():      # 开启串行端口
            input_s = str
            input_s = (input_s + '\r\n').encode('utf-8')
            self.serial_9600.write(input_s)
            print("string:",input_s)

    # 读取返回指令处理成16进制
    def data_read(self):
        #print("开始读取")
        self.real_v = 0
        self.address_v = 0
        try:
            self.now_num = self.serial_9600.inWaiting()        #返回接收缓存中的字节数
        except:
            return None
        if self.now_num > 0:
            data = self.serial_9600.read(self.now_num)         #读取到的数据
            instruct = (data.decode('iso-8859-1'))
            num = len(data)                                 #数据的长度
            out_s = ''
            for i in range(0, len(data)):                         #从0到数据长度个元素
                out_s = out_s + '{:02X}'.format(data[i]) + ' '    #将data中的元素格式化转16进制，2位对齐，左补0，并拼接
            self.response = out_s
            print("返回的16进制指令  response =",self.response)                     #处理后得到的16进制返回指令
            return self.response
            #self.UpdateVolt(self.response)
        else:
            print("未接收到任何返回指令")
            return 0
