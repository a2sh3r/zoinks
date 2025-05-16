import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

class Worker:
    @requires_lock("lock")
    def work(self):
        pass

def run():
    w = Worker()
    for _ in range(1000):
        w.work()