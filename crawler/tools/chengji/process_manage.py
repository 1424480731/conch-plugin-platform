from multiprocessing import Process

class MyProcess:

    def __init__(self):
        self.process_dict = {}

    def add(self,target,name,*args):
        try:
            p = Process(target=target,name=name,args=args)
            p.start()
            self.process_dict.update({name:p})
            return 1
        except:
            return 0
    def terminate_by_name(self,name):
        try:
            p = self.process_dict.get(name)
            p.terminate()
            return 1
        except:
            return 0