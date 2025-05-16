import threading

lock = threading.Lock()

def critical_section():
    pass

def run():
    for _ in range(1000):
        with lock:
            critical_section()