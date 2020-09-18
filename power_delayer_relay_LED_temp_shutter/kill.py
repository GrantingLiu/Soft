import inspect
import ctypes
import threading
from threading import Thread
import time

def count_down():
    total_time = 3
    while total_time != 0:
        minute = total_time//60
        second = total_time % 60
        total_time -= 1
        print("%02d:%02d" % (minute,second))
        time.sleep(1)
        

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    thread_num = len(threading.enumerate())
    print("主线程：线程数量是%d" % thread_num)
    # 输出所有线程名字
    print(str(threading.enumerate()))


    time.sleep(5)
    _async_raise(thread.ident, SystemExit)


a = threading.Thread(target=count_down)
a.start()


stop_thread(a)
# stop_thread("进程名")