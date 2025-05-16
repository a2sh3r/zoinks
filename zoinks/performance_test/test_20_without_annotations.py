import threading

lock_x = threading.Lock()
lock_y = threading.Lock()

def use_both():
    with lock_x:
        with lock_y:
            pass

def run():
    for _ in range(1000):
        use_both()