import threading
from zoinks.macros import requires_lock, guards_variable

lock = threading.Lock()

@requires_lock("lock")
@guards_variable("data")
def complex_operation(data):
    data["count"] += 1

def run():
    d = {"count": 0}
    for _ in range(1000):
        with lock:
            complex_operation(d)