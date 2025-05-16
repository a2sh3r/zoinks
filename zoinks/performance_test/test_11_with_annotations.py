import threading
from zoinks.macros import requires_lock

lock1 = threading.Lock()
lock2 = threading.Lock()

@requires_lock("lock1")
@requires_lock("lock2")
def nested_locks():
    pass

def run():
    for _ in range(1000):
        with lock1:
            with lock2:
                nested_locks()