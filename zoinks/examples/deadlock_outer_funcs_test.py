import threading
import time

from zoinks.macros import requires_lock

lock_a = threading.Lock()
lock_b = threading.Lock()

start_event = threading.Event()

def inner_func():
    start_event.wait()
    with lock_a:
        print("inner_func has lock_a")
        time.sleep(0.1)
        with lock_b:
            print("Inner function")

def outer_func():
    start_event.wait()
    with lock_b:
        print("outer_func has lock_b")
        time.sleep(0.1)
        with lock_a:
            print("Outer function")

t1 = threading.Thread(target=inner_func)
t2 = threading.Thread(target=outer_func)

t1.start()
t2.start()

time.sleep(0.05)
start_event.set()
t1.join()
t2.join()