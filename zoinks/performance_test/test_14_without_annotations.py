import threading

rlock = threading.RLock()

class MyClass:
    def method(self):
        pass

def run():
    obj = MyClass()
    for _ in range(1000):
        with rlock:
            obj.method()