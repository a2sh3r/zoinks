import threading
from zoinks.macros import requires_lock

lock_a = threading.Lock()
lock_b = threading.Lock()

@requires_lock("lock_a")
@requires_lock("lock_b")
def thread1():
    with lock_a:
        with lock_b:
            pass

@requires_lock("lock_b")
@requires_lock("lock_a")
def thread2():
    with lock_b:
        with lock_a:
            pass

def run():
    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()