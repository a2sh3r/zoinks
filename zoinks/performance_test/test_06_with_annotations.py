import threading
from zoinks.macros import requires_lock, guards_variable

my_lock = threading.Lock()

class SharedData:
    def __init__(self):
        self.value = 0

    @requires_lock("my_lock")
    @guards_variable("value")
    def increment(self):
        self.value += 1

def run():
    data = SharedData()
    with my_lock:
        for _ in range(1000):
            data.increment()