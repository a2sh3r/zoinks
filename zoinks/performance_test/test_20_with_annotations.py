import threading
from zoinks.macros import requires_lock

lock_x = threading.Lock()
lock_y = threading.Lock()

@requires_lock("lock_x")
@requires_lock("lock_y")
def use_both():
    with lock_x:
        with lock_y:
            pass

def run():
    for _ in range(1000):
        use_both()