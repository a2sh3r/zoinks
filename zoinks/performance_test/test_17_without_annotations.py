import threading

lock = threading.Lock()

def complex_operation(data):
    data["count"] += 1

def run():
    d = {"count": 0}
    for _ in range(1000):
        with lock:
            complex_operation(d)