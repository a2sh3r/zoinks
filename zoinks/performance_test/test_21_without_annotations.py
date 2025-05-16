import threading

lock = threading.Lock()

def secured_function():
    pass

def run():
    for _ in range(1000):
        secured_function()