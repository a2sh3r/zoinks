import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def do_something():
    pass

def run():
    for _ in range(1000):
        lock.acquire()
        try:
            do_something()
        finally:
            lock.release()