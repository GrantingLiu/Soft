# coding=utf-8
# @Author    : LYG
# @Time      : 2019/2/28 11:12
# @Name      : server.py
# coding: utf-8
 
import select
import socket
 
 
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('localhost',1234))
server.listen(1)
 
inputs = [server,]
outputs = []
errors = []
 
print("服务器的socket：",server.fileno())
 
while True:
    read_list, write_list, err_list = select.select(inputs, outputs, errors)
    for item in read_list:
        if item is server:
            client, address = item.accept()
            print("嘿，有人跟你建立连接了:",client.fileno())
            inputs.append(client)
        else:
            msg = item.recv(1024)
            if msg != b'':
                print("收到{:s}消息：{:s}".format(str(item.getsockname()),msg.decode()))
 
                if item not in outputs:
                    outputs.append(item)
            else:
                print("不好，{:d}走了".format(item.fileno()))
                if item in outputs:
                    outputs.remove(item)
                inputs.remove(item)
                item.close()
 
 
    for item in outputs:
        item.send(("嗨喽！{:d}你好，我已经收到你的消息了".format(item.fileno())).encode())
        print("消息已经发出！")
        outputs.remove(item)
 
 
    for item in errors:
        print("完蛋，{:d} 出现异常了！".format(item.fileno()))
        inputs.remove(item)
        if item in outputs:
            outputs.remove(item)
 
 