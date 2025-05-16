import threading

lock = threading.Lock()

def do_something():
    pass

def run():
    for _ in range(1000):
        lock.acquire()
        try:
            do_something()
        finally:
            lock.release()