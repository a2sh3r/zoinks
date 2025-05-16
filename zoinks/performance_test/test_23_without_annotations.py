import threading

lock = threading.Lock()

def dangerous_call():
    pass

def run():
    for _ in range(1000):
        dangerous_call()