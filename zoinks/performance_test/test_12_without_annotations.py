import threading

rlock = threading.RLock()

def inner():
    pass

def outer():
    inner()

def run():
    for _ in range(1000):
        with rlock:
            outer()