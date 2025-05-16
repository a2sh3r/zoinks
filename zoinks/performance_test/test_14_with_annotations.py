import threading
from zoinks.macros import requires_lock

rlock = threading.RLock()

class MyClass:
    @requires_lock("rlock")
    def method(self):
        pass

def run():
    obj = MyClass()
    for _ in range(1000):
        with rlock:
            obj.method()