import threading

lock = threading.Lock()

class Worker:
    def work(self):
        pass

def run():
    w = Worker()
    for _ in range(1000):
        w.work()