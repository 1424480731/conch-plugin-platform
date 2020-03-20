import threading
import copy,time


class MyThread(threading.Thread):

    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None








class ThreadPool:

    def __init__(self,size):

        self.size =  size
        self.pool = []


    def add(self):
        pass

    def start(self):
        pass

    def join(self):
        pass






























