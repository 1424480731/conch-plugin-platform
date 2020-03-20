import threading


class ThreadPool:

    def __init__(self):

        self.pool = []

    def add(self,tl):

        self.pool.extend(tl)



    def start(self):

        for t in self.pool:
            t.start()
        print(len(self.pool),'个线程已启动抓取')


    def join(self):

        for t in self.pool:
            t.join()



