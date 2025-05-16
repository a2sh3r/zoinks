import threading
from zoinks.macros import requires_lock

lock = threading.Lock()

@requires_lock("lock")
def critical_section():
    pass

def run():
    for _ in range(1000):
        with lock:
            critical_section()