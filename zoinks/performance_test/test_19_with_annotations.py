import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

class Service:
    @requires_lock("lock")
    def process(self):
        pass

def run():
    service = Service()
    for _ in range(1000):
        with lock:
            service.process()