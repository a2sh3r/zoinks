import threading

lock = threading.Lock()

class Service:
    def process(self):
        pass

def run():
    service = Service()
    for _ in range(1000):
        with lock:
            service.process()