import threading
from zoinks.macros import requires_lock

rlock = threading.RLock()

@requires_lock("rlock")
def inner():
    pass

def outer():
    inner()

def run():
    for _ in range(1000):
        with rlock:
            outer()