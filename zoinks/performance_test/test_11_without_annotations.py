import threading

lock1 = threading.Lock()
lock2 = threading.Lock()

def nested_locks():
    pass

def run():
    for _ in range(1000):
        with lock1:
            with lock2:
                nested_locks()